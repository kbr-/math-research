"""The transfer review's decisive test: proper-closure killers against domain killers at K=2.

System: functional pigeonhole over F_2, 6 pigeons, 5 holes, multilinear ring, D=3 (proper,
check:functional-factor-kernels). C is its degree-3 closure; H the degree-3 closure of the monomial axioms
alone (hole and functionality axioms), the domain model of partial matchings. For an error x_v and k<=2,
Ann_X^(k)(x_v) = {f in V_k : f x_v in X}; A_v = Ann_H^(2)(x_v); C2 = C cap V_2. Error sets F3 = {x00,x11,x22},
F4 = F3 + {x33}. Quantities, as dimensions modulo C2:
  (i) single excess: dim Ann_C^(2)(x_v) - dim(A_v + C2), per v;
  (ii) joint defect: dim of the intersection over v of (A_v + C2) minus dim(intersection of A_v, plus C2);
  (iii) surviving domain killers: dim(Ann_H^(2)(F) + C2) - dim C2;
  total excess dim Ann_C^(2)(F) - dim(Ann_H^(2)(F) + C2), and its cancellation part
  dim Ann_C^(2)(F) - dim(intersection over v of (A_v + C2)).
Statement tested: the transfer review's Prediction, untested; the review's hypothesis of the sandwich is
that (iii) is positive. No outcome of (i), (ii) or the cancellation part is predicted.
Expected: (iii) positive for F3 and F4 (x20 x01 lies in Ann_H(F3) and is asserted outside C2 by the run);
(i), (ii) printed.
Refuted by: (iii) zero for F3, which would mean every domain killer of degree 2 lies in the closure.
Possible because: the proper closure contains degree-2 consequences of the pigeon axioms not in H.
Control: at K=1 the total excess for F3 must be 0, as check:functional-factor-kernels recorded for its sets.
Refuted by: a positive K=1 excess, contradicting the recorded check or showing an error in this script.
Possible because: a bug in the kernel or intersection code would show spurious killers.
"""
import argparse
import itertools
import json
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / 'tools'))
import pc_closure as pc


def systems(m, n):
    v = lambda i, j: i * n + j
    mono = []
    for j in range(n):
        for i, k in itertools.combinations(range(m), 2):
            mono.append({(1 << v(i, j)) | (1 << v(k, j))})
    for i in range(m):
        for j, k in itertools.combinations(range(n), 2):
            mono.append({(1 << v(i, j)) | (1 << v(i, k))})
    pigeons = [{0} | {1 << v(i, j) for j in range(n)} for i in range(m)]
    return mono, mono + pigeons, m * n, v


def deg(m):
    return bin(m).count('1')


def prepare(c):
    c.mask = sum(1 << p for p in c.rows)
    for p, row in c.rows.items():
        assert row & c.mask == 1 << p, 'rows must be in reduced echelon form'
    return c


def red(c, v):
    bits = v & c.mask
    while bits:
        low = bits & -bits
        v ^= c.rows[low.bit_length() - 1]
        bits ^= low
    return v


class Space:
    """Subspaces of V_k as bit vectors over a fixed monomial list, with echelon bases."""
    def __init__(self, vecs=()):
        self.basis = {}
        for x in vecs:
            self.add(x)

    def reduce(self, x):
        for p in sorted(self.basis, reverse=True):
            if x >> p & 1:
                x ^= self.basis[p]
        return x

    def add(self, x):
        x = self.reduce(x)
        if x:
            self.basis[x.bit_length() - 1] = x
            return True
        return False

    def __add__(self, other):
        return Space(list(self.basis.values()) + list(other.basis.values()))

    def __len__(self):
        return len(self.basis)

    def __contains__(self, x):
        return self.reduce(x) == 0

    def __and__(self, other):
        a, b = list(self.basis.values()), list(other.basis.values())
        rows = [(x, 1 << i) for i, x in enumerate(a)] + [(x, 0) for x in b]
        piv, out = {}, Space()
        for x, tag in rows:            # combinations summing to zero; their A-part lies in A and in B
            for p in sorted(piv, reverse=True):
                if x >> p & 1:
                    x ^= piv[p][0]
                    tag ^= piv[p][1]
            if x:
                piv[x.bit_length() - 1] = (x, tag)
            elif tag:
                y = 0
                for i in range(len(a)):
                    if tag >> i & 1:
                        y ^= a[i]
                out.add(y)
        return out


def ann(c, monos, error):
    """{f in span(monos) : f * error in c}, as a Space over the index of monos."""
    rows = []
    for t, m in enumerate(monos):
        rows.append((red(c, c.vector(pc.multiply({m}, {error}))), 1 << t))
    piv, kern = {}, Space()
    for x, tag in rows:
        for p in sorted(piv, reverse=True):
            if x >> p & 1:
                x ^= piv[p][0]
                tag ^= piv[p][1]
        if x:
            piv[x.bit_length() - 1] = (x, tag)
        else:
            kern.add(tag)
    return kern


def members(c, monos):
    """C cap span(monos), over the index of monos: rows whose pivot has degree <= the top degree of monos."""
    top = max(deg(m) for m in monos)
    idx = {m: i for i, m in enumerate(monos)}
    out = Space()
    for p, row in c.rows.items():
        if deg(c.monos[p]) <= top:
            y = 0
            for m in c.poly(row):
                y ^= 1 << idx[m]
            out.add(y)
    return out


def quantities(cC, cH, monos, errors):
    C2 = members(cC, monos)
    annC = {e: ann(cC, monos, e) for e in errors}
    annH = {e: ann(cH, monos, e) for e in errors}
    single = {e: len(annC[e]) - len(annH[e] + C2) for e in errors}
    inter_plus = None
    inter_H = None
    inter_C = None
    for e in errors:
        s = annH[e] + C2
        inter_plus = s if inter_plus is None else inter_plus & s
        inter_H = annH[e] if inter_H is None else inter_H & annH[e]
        inter_C = annC[e] if inter_C is None else inter_C & annC[e]
    domain = inter_H + C2
    return {'dim_C2': len(C2), 'single_excess': {str(e): single[e] for e in errors},
            'joint_defect': len(inter_plus) - len(domain),
            'surviving_domain_killers': len(domain) - len(C2),
            'total_excess': len(inter_C) - len(domain),
            'cancellation_part': len(inter_C) - len(inter_plus)}, inter_H, C2


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--out', required=True)
    args = ap.parse_args()
    m, n, D = 6, 5, 3
    mono, full, nv, v = systems(m, n)
    cC, cH = prepare(pc.Closure(full, nv, D)), prepare(pc.Closure(mono, nv, D))
    assert cC.proper and cH.proper
    x = lambda i, j: 1 << v(i, j)
    out = {'system': 'functional pigeonhole, 6 pigeons, 5 holes, F_2, multilinear', 'D': D,
           'closure_dims': {'C': cC.dim, 'H': cH.dim}, 'sets': {}}
    v1 = [mm for mm in cC.monos if deg(mm) <= 1]
    v2 = [mm for mm in cC.monos if deg(mm) <= 2]
    F3 = [x(0, 0), x(1, 1), x(2, 2)]
    # Control at K=1.
    q1, _, _ = quantities(cC, cH, v1, F3)
    assert q1['total_excess'] == 0, ('K=1 control failed', q1)
    out['control_K1_F3'] = q1
    print('control K=1 F3', q1, flush=True)
    for name, errors in (('F3', F3), ('F4', F3 + [x(3, 3)])):
        q, inter_H, C2 = quantities(cC, cH, v2, errors)
        out['sets'][name] = q
        print(name, q, flush=True)
        if name == 'F3':
            idx = {mm: i for i, mm in enumerate(v2)}
            example = 1 << idx[x(2, 0) | x(0, 1)]
            out['example_x20x01'] = {'in_Ann_H_F3': example in inter_H, 'in_C2': example in C2}
        out['sets'][name]['prediction_iii_holds'] = q['surviving_domain_killers'] > 0
    pathlib.Path(args.out).write_text(json.dumps(out, indent=1) + '\n')
    print('PASS', flush=True)


if __name__ == '__main__':
    main()
