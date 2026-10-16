"""Decisive test of the factor-domination review: common factor kernels where truncation is active.

System: functional pigeonhole over F_2, m = n+1 pigeons, n holes, multilinear ring: pigeon axioms
1 + sum_j x_ij (degree 1), hole axioms x_ij x_kj and functionality axioms x_ij x_ij' (degree 2).  Its
proper windows lie above its axioms' degree, so its closure is not the degree part of a vanishing
ideal (it is unsatisfiable and proper).  H is the closure of the monomial axioms alone, the vanishing
ideal of the partial matchings Y'' in each degree (a domain model).  For a factor set F of variables,
Ann_X(F) = {u in V_1 : w u in X for all w in F}.

Statement tested (an untested hypothesis, stated so it can fail): at K=1 and the largest proper D
found (at least 3), for the factor sets {x00,x10} (one hole), {x00,x01} (one pigeon), {x00,x11},
{x00,x11,x22} and {x00,x11,x22,x33}, Ann_C(F) = Ann_H(F) + (C cap V_1): the non-monomial pigeon
axioms add no common killer beyond the domain model's and the relations.
Expected: equality for every F; the script prints PASS.
Refuted by: dim Ann_C(F) > dim(Ann_H(F) + (C cap V_1)) for some F.
Possible because: C contains degree-2 consequences of the pigeon axioms not in H, such as
x10 (1 + sum_j x0j) = x10 + sum_{j>0} x10 x0j modulo H, which can make new linear classes kill a factor.
Control: for a one-hole and a one-pigeon F the sum s of the factors is a linear generator, so
Ann_C(F) = Ann_C(s) must hold (lem:factor-ideal-domination (a)); asserted.

Run 5ec722393c (6 pigeons, 5 holes, D=3) passed.  Second version, after the review: --holes picks the
size; the review named 7 pigeons and 6 holes.  Positive control (the reviewer's counterexample): on
variables a, b, w, z with monomial axioms ab, bz and linear axiom w+a+z at D=2, F={w}: Ann_C(w) has
dimension 3 against 2 for Ann_H(w) + (C cap V_1), so the comparison detects a killer the linear axiom
transports (b kills a and z, and w = a+z).  Expected: the control shows 3 against 2, asserted.
Refuted by: the control showing equality, which would mean the script cannot see such killers.
Possible because: a bug in kernel_span or members_in_v1 would hide the transported killer.
"""
import argparse
import itertools
import json
import pathlib
import subprocess
import sys
import tempfile

ROOT = pathlib.Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / 'tools'))
import pc_closure as pc


def functional_php(m, n, with_pigeons=True):
    v = lambda i, j: i * n + j
    monomial = []
    for j in range(n):
        for i, k in itertools.combinations(range(m), 2):
            monomial.append({(1 << v(i, j)) | (1 << v(k, j))})
    for i in range(m):
        for j, k in itertools.combinations(range(n), 2):
            monomial.append({(1 << v(i, j)) | (1 << v(i, k))})
    pigeons = [{0} | {1 << v(i, j) for j in range(n)} for i in range(m)]
    return (monomial + pigeons if with_pigeons else monomial), m * n, v


def kernel_span(c, nv, polys):
    """Basis (as V_1 bit vectors: bit 0 the constant, bit i+1 the variable x_i) of {u in V_1: p u in C for all p}."""
    basis = [{0}] + [{1 << i} for i in range(nv)]
    rows = []
    for b in basis:
        vec, shift = 0, 0
        for p in polys:
            vec |= c.reduce(c.vector(pc.multiply(p, b))) << shift
            shift += len(c.monos)
        rows.append(vec)
    pivots, kern = {}, []
    for i, img in enumerate(rows):
        ident = 1 << i
        while img:
            top = img.bit_length() - 1
            if top in pivots:
                img ^= pivots[top][0]
                ident ^= pivots[top][1]
            else:
                pivots[top] = (img, ident)
                break
        if not img:
            kern.append(ident)
    return kern


def rank(vecs):
    piv = {}
    for v in vecs:
        while v:
            t = v.bit_length() - 1
            if t in piv:
                v ^= piv[t]
            else:
                piv[t] = v
                break
    return len(piv)


def members_in_v1(c, nv):
    """Basis of C cap V_1 as V_1 bit vectors."""
    return kernel_span(c, nv, [{0}])


def refutation_degree(axioms, nv, dmax, binary, tmp):
    path = pathlib.Path(tmp) / 'instance.txt'
    path.write_text(f'{nv} {len(axioms)}\n' + ''.join(f'{len(p)} ' + ' '.join(map(str, sorted(p))) + '\n'
                                                      for p in axioms))
    return json.loads(subprocess.run([binary, str(path), str(dmax)], check=True, capture_output=True,
                                     text=True).stdout)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--out', required=True)
    parser.add_argument('--holes', type=int, default=0, help='run this size only (0: first with D>=3)')
    args = parser.parse_args()
    out = {'sizes': []}
    # Positive control: a=bit0, b=bit1, w=bit2, z=bit3.
    ctl_monomial = [{0b0011}, {0b1010}]
    ctl = pc.Closure(ctl_monomial + [{0b0100, 0b0001, 0b1000}], 4, 2)
    ctl_h = pc.Closure(ctl_monomial, 4, 2)
    ann_c, ann_h, rel_c = (kernel_span(ctl, 4, [{0b0100}]), kernel_span(ctl_h, 4, [{0b0100}]),
                           members_in_v1(ctl, 4))
    out['positive_control'] = dict(ann_C=rank(ann_c), ann_H_plus_relations=rank(ann_h + rel_c))
    print('positive control', json.dumps(out['positive_control']), flush=True)
    assert out['positive_control'] == dict(ann_C=3, ann_H_plus_relations=2)
    with tempfile.TemporaryDirectory() as tmp:
        binary = str(pathlib.Path(tmp) / 'fcd')
        subprocess.run(['g++', '-O2', '-o', binary, str(ROOT / 'tools' / 'f2_closure_degree.cpp')], check=True)
        chosen = None
        for n in ((args.holes,) if args.holes else (3, 4, 5)):
            axioms, nv, v = functional_php(n + 1, n)
            info = refutation_degree(axioms, nv, 4, binary, tmp)
            out['sizes'].append(dict(holes=n, pigeons=n + 1, result=info))
            print(json.dumps(out['sizes'][-1]), flush=True)
            proper = [int(d) for d in info['dimensions']]
            if chosen is None and max(proper) >= 3:
                chosen = (n, max(proper))
    assert chosen, 'no proper window at degree 3 or more'
    n, D = chosen
    m = n + 1
    axioms, nv, v = functional_php(m, n)
    monomial, _, _ = functional_php(m, n, with_pigeons=False)
    C = pc.Closure(axioms, nv, D)
    H = pc.Closure(monomial, nv, D)
    assert C.proper and H.proper
    rel = members_in_v1(C, nv)
    x = lambda i, j: {1 << v(i, j)}
    cases = {'one hole': [x(0, 0), x(1, 0)], 'one pigeon': [x(0, 0), x(0, 1)],
             'two': [x(0, 0), x(1, 1)], 'three': [x(0, 0), x(1, 1), x(2, 2)]}
    if n >= 4:
        cases['four'] = [x(0, 0), x(1, 1), x(2, 2), x(3, 3)]
    out['chosen'] = dict(holes=n, pigeons=m, D=D, K=1, dim_V1=nv + 1, relations=rank(rel))
    out['cases'] = {}
    refuted = []
    for name, F in cases.items():
        annC = kernel_span(C, nv, F)
        annH = kernel_span(H, nv, F)
        explained = rank(annH + rel)
        row = dict(ann_C=rank(annC), ann_H=rank(annH), ann_H_plus_relations=explained,
                   contains=rank(annC + annH + rel) == rank(annC))
        assert row['contains']
        if name in ('one hole', 'one pigeon'):
            s = {next(iter(F[0])), next(iter(F[1]))}
            row['ann_C_of_sum'] = rank(kernel_span(C, nv, [s]))
            assert rank(kernel_span(C, nv, [s]) + annC) == rank(annC) == row['ann_C_of_sum']
        if row['ann_C'] > explained:
            refuted.append(name)
        out['cases'][name] = row
        print(name, json.dumps(row), flush=True)
    out['refuted_for'] = refuted
    pathlib.Path(args.out).write_text(json.dumps(out, indent=1) + '\n')
    print('REFUTED for ' + ', '.join(refuted) if refuted else 'PASS')


if __name__ == '__main__':
    main()
