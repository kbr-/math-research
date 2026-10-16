"""The 4x3 excess of linear_sizes.json: reconstruct the error, exhibit the extra killer, check it independently.

System: functional pigeonhole over F_2, 4 pigeons, 3 holes, multilinear, D=2, K=1 (inside the range of
conj:linear-kernel-transfer: n=3, D=2=ceil(3/2)). The error is random20 of linear_sizes.py, replayed from its
seed. The script prints E, finds u in Ann_C(E) cap V_1 outside the best domain side over all 16 representatives,
and checks uE in C by an independent route: C_2 is spanned by the non-matching monomials of degree <= 2, the
pigeon axioms Q_i and the products x_a Q_i reduced multilinearly (the degree-1 part of C being span{Q_i}, as
linear_sizes.py asserts), and membership is decided by an elimination written here, not by tools/pc_closure.py.
Statement tested: conj:linear-kernel-transfer at n=3; a confirmed u refutes it.
Expected: u exists and passes the independent membership check, and lies in no representative's domain side.
Refuted by: no such u, or the independent check rejecting uE, which would mean linear_sizes.py erred.
Possible because: the excess came from one tool chain, whose degree-2 closure could hold a spurious member.
Control: for x00 the independent check accepts u Q_0-type products and agrees with pc_closure on its kernel size.
Refuted by: the two routes giving different kernel dimensions for x00 or for the error.
Possible because: the independent span could miss closure members or contain extra ones.
Positive control: the independent route must find x01 * (x00 + Q_0) in C, a product of a variable and a
pigeon-axiom shift, which lies in C by construction; asserted.
Refuted by: the independent route rejecting that product.
Possible because: a reduction or indexing bug in the independent elimination.
Baseline: the bare count gives an excess of at most 13 - 4 minus the domain part; it does not decide it.
Record checked: the claims read are conj:linear-kernel-transfer, check:dense-linear-kernels and
lem:admissible-numbering-transfer; none decides this error.
"""
import argparse
import importlib.util
import itertools
import json
import pathlib
import random
import sys

ROOT = pathlib.Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / 'tools'))
import pc_closure as pc

spec = importlib.util.spec_from_file_location('linear_sizes', pathlib.Path(__file__).with_name('linear_sizes.py'))
ls = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ls)
tq, dl = ls.tq, ls.dl

M, N = 4, 3


def mul(a, b):
    """Multilinear product of polynomials given as sets of monomial bitmasks over F_2."""
    out = set()
    for s in a:
        for t in b:
            out ^= {s | t}
    return out


def matching(mono):
    cells = [k for k in range(M * N) if mono >> k & 1]
    return (len({k // N for k in cells}) == len(cells)) and (len({k % N for k in cells}) == len(cells))


class Span:
    """An F_2 span of polynomials (sets of monomials), by elimination on a fixed monomial order."""

    def __init__(self):
        self.piv = {}

    def reduce(self, p):
        p = set(p)
        for top in sorted(self.piv, reverse=True):
            if top in p:
                p ^= self.piv[top]
        return p

    def add(self, p):
        p = self.reduce(p)
        if p:
            self.piv[max(p)] = p

    def __contains__(self, p):
        return not self.reduce(p)


def independent_closure():
    x = lambda i, j: 1 << (i * N + j)
    Q = [{0} | {x(i, j) for j in range(N)} for i in range(M)]
    span = Span()
    for k in range(1, 3):
        for cells in itertools.combinations(range(M * N), k):
            mono = sum(1 << c for c in cells)
            if not matching(mono):
                span.add({mono})
    for q in Q:
        span.add(q)
        for c in range(M * N):
            span.add(mul({1 << c}, q))
    return span, Q, x


def kernel_size(span, E, monos):
    """dim {u in span(monos): uE in span}, by elimination of the images."""
    img = Span()
    rank = 0
    for m in monos:
        p = span.reduce(mul({m}, E))
        before = len(img.piv)
        img.add(p)
        rank += len(img.piv) - before
    return len(monos) - rank


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--out', required=True)
    args = ap.parse_args()
    rng = random.Random(20261017)
    for n in (3,):
        m = n + 1
        variables = [1 << (i * n + j) for i in range(m) for j in range(n)]
        errors = []
        for t in range(24):
            errors.append({u for u in [0] + variables if rng.random() < 0.5})
    E = errors[20]
    mono, full, nv, v = tq.systems(M, N)
    cC = tq.prepare(pc.Closure(full, nv, 2))
    cH = tq.prepare(pc.Closure(mono, nv, 2))
    monos = [x for x in cC.monos if tq.deg(x) <= 1]
    C1 = tq.members(cC, monos)
    Q = [{0} | {1 << v(i, j) for j in range(N)} for i in range(M)]
    annC = dl.ann_poly(cC, monos, E)
    reps = ls.representatives(Q)
    kernels = ls.domain_kernels(cH, monos, E, reps)
    best = max(kernels, key=lambda ck: len(ck[1] + C1))
    domain = best[1] + C1
    extra = [b for b in annC.basis.values() if b not in domain]
    u_bits = extra[0]
    u = {monos[t] for t in range(len(monos)) if u_bits >> t & 1}
    span, Qi, x = independent_closure()
    name = lambda mono: '1' if mono == 0 else '*'.join(f'x{k // N}{k % N}' for k in range(M * N) if mono >> k & 1)
    in_C = mul(u, E) in span
    control = mul({x(0, 1)}, {x(0, 0)} ^ Qi[0]) in span
    k_ind = kernel_size(span, E, monos)
    k_x00 = kernel_size(span, {x(0, 0)}, monos)
    in_any_domain = any(u_bits in (k + C1) for _, k in kernels)
    out = {'E': sorted(name(t) for t in E), 'u': sorted(name(t) for t in u), 'uE_in_C_independent': in_C,
           'u_in_some_representative_domain_side': in_any_domain, 'C_side_pc_closure': len(annC),
           'C_side_independent': k_ind, 'best_domain_side': len(domain), 'best_rep': best[0],
           'x00_C_side_pc_closure': len(dl.ann_poly(cC, monos, {x(0, 0)})), 'x00_C_side_independent': k_x00,
           'positive_control': control}
    print(json.dumps(out, indent=1), flush=True)
    assert control, 'positive control'
    assert out['x00_C_side_pc_closure'] == k_x00, 'routes differ on x00'
    pathlib.Path(args.out).write_text(json.dumps(out, indent=1) + '\n')


if __name__ == '__main__':
    main()
