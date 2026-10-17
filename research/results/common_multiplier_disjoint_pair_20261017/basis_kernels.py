"""Common kernels of partition errors on the functional pigeonhole system over F_p, through the IPS basis.

The degree-D closure C, for D <= ceil(N/2), is H plus the lift of K_D = span(B_D minus T_D) (lem:admissible-numbering-
transfer's record: "So C is H plus the lift of K_D"), B_D the x_a, a a partial map of pigeons to holes or to 0 (the
factor Q_i), whose matching part has a dance, T_D its matching monomials. Modulo H (the hole, functionality and
Booleanity closure) the multilinear degree-<= D space is spanned by the matching monomials, so C/H is spanned by the
reductions of x_t prod_{i in Z} Q_i, Z nonempty, |t| + |Z| <= D, t dancing. For errors E the common kernel
{u in V_K : uE in C} has dimension dim(H cap V_K) + dim{u in span(T_K) : uE in C/H}, and W = C cap V_K the same
with E = 1. A dance: pigeons in increasing order, each moved once to the smallest free hole above it (a greedy that
finds a dance whenever one exists, by exchange).

Statement tested: whether two disjoint partition errors E_A, E_B (pigeons 1, 2; A = {0, 1}, B = {2, 3}) at six
pigeons and five holes, D = 3, K = 2, have a common surviving killer over F_3, dim J > dim W, the case
thm:partition-killer-degree (e) leaves open in characteristic other than 2.
Expected: no outcome is predicted for F_3.
Refuted by: nothing is refuted; the F_3 figure is the result.
Possible because: no recorded statement fixes the F_3 common kernel here.
Control: over F_2 the same route must reproduce mixing_pairs_65.json and dims_65.json at six pigeons and five holes:
dim W = 276, single kernel 332 at A = {0, 1}, J = 300 for the pair A = {0, 1}, B = {2, 3}; and dim of the quotient
span(T_D)/(C/H) must equal the number of dancing matchings of size <= D, the basis count.
Refuted by: any F_2 figure different from 276, 332, 300, or a quotient dimension different from the dance count.
Possible because: a wrong dance, a wrong reduction or a wrong generator set would change them.
Positive control: over F_2 the pair has J = 300 > 276 = W, a common surviving killer that the route must see.
Refuted by: J = W over F_2.
Possible because: a route that loses killers would give J = W.
Forced by counts: nothing; the dimensions are computed.
Baseline: W <= J <= single kernel; at F_3 the containment leaves J anywhere in [W, single kernel].
Record checked: the claims read were thm:partition-killer-degree, check:representative-intersection-kernels and
lem:admissible-numbering-transfer; none gives the F_3 common kernel of the disjoint pair.
"""
import argparse
import itertools
import json
import pathlib
import time

import numpy as np


def matchings(m, n, dmax):
    out = [()]
    for size in range(1, dmax + 1):
        for pigeons in itertools.combinations(range(m), size):
            for holes in itertools.permutations(range(n), size):
                out.append(tuple(zip(pigeons, holes)))
    return out


def dances(t):
    occupied = {h for _, h in t}
    for p, h in sorted(t):
        free = [g for g in range(h + 1, N) if g not in occupied]
        if not free:
            return False
        occupied.discard(h)
        occupied.add(free[0])
    return True


def mul(a, b):
    """Product of two matchings modulo H, or None."""
    pa, ha = dict(a), {h: p for p, h in a}
    for p, h in b:
        if p in pa and pa[p] != h:
            return None
        if h in ha and ha[h] != p:
            return None
    return tuple(sorted(set(a) | set(b)))


def poly_mul(f, g):
    out = {}
    for a, ca in f.items():
        for b, cb in g.items():
            c = mul(a, b)
            if c is not None:
                out[c] = (out.get(c, 0) + ca * cb) % P
    return {k: v for k, v in out.items() if v}


def q(i):
    f = {(): 1}
    for h in range(N):
        f[((i, h),)] = P - 1
    return f


def rref(rows):
    """Row-reduced basis mod P of an integer matrix, with its pivot columns."""
    a = rows.copy() % P
    pivots, r = [], 0
    for c in range(a.shape[1]):
        nz = np.nonzero(a[r:, c])[0]
        if nz.size == 0:
            continue
        k = r + nz[0]
        a[[r, k]] = a[[k, r]]
        a[r] = (a[r] * pow(int(a[r, c]), P - 2, P)) % P
        col = a[:, c].copy()
        col[r] = 0
        a = (a - np.outer(col, a[r])) % P
        pivots.append(c)
        r += 1
        if r == a.shape[0]:
            break
    return a[:r], pivots


def reduce_mod(vecs, basis, pivots):
    v = vecs.copy() % P
    for row, c in zip(basis, pivots):
        v = (v - np.outer(v[:, c], row)) % P
    return v


def rank(rows):
    return len(rref(rows)[1]) if rows.size else 0


def error(A):
    f = {}
    for h in range(N):
        f[((1, h),) if h in A else ((2, h),)] = 1
    return f


def kernel_dim(errors, setup):
    tk, index, cbasis, cpiv = setup['tk'], setup['index'], setup['cbasis'], setup['cpiv']
    blocks = []
    for E in errors:
        rows = np.zeros((len(tk), len(index)), dtype=np.int64)
        for r, t in enumerate(tk):
            for mono, c in poly_mul({t: 1}, E).items():
                rows[r, index[mono]] = c
        blocks.append(reduce_mod(rows, cbasis, cpiv))
    stacked = np.concatenate(blocks, axis=1)
    return len(tk) - rank(stacked)


def run(m, n, D, K, pairs):
    global N
    N = n
    t0 = time.time()
    td = matchings(m, n, D)
    index = {t: i for i, t in enumerate(td)}
    gens = []
    for t in td:
        if not dances(t):
            continue
        free = [i for i in range(m) if i not in dict(t)]
        for z in range(1, D - len(t) + 1):
            for Z in itertools.combinations(free, z):
                f = {t: 1}
                for i in Z:
                    f = poly_mul(f, q(i))
                v = np.zeros(len(td), dtype=np.int64)
                for mono, c in f.items():
                    v[index[mono]] = c
                gens.append(v)
    cbasis, cpiv = rref(np.array(gens, dtype=np.int64))
    dance_count = sum(dances(t) for t in td)
    tk = [t for t in td if len(t) <= K]
    non_matching = None   # dim(H cap V_K) is the same on both sides of every comparison; reported relative to it
    setup = {'tk': tk, 'index': index, 'cbasis': cbasis, 'cpiv': cpiv}
    out = {'p': P, 'pigeons': m, 'holes': n, 'D': D, 'K': K, 'quotient_dim': len(td) - len(cpiv),
           'dancing_matchings': dance_count, 'W_mod_H': kernel_dim([{(): 1}], setup), 'singles': {}, 'pairs': []}
    for A, B in pairs:
        for S in (A, B):
            out['singles'][str(S)] = kernel_dim([error(S)], setup)
        out['pairs'].append({'A': A, 'B': B, 'J_mod_H': kernel_dim([error(A), error(B)], setup)})
    out['seconds'] = round(time.time() - t0, 1)
    return out


def main():
    global P
    ap = argparse.ArgumentParser()
    ap.add_argument('--out', required=True)
    args = ap.parse_args()
    series = []
    # smallest board first (four pigeons, three holes, D = 2, K = 1), then six pigeons and five holes
    for p, m, n, D, K in ((2, 4, 3, 2, 1), (2, 6, 5, 3, 2), (3, 6, 5, 3, 2)):
        P = p
        pairs = [([0], [1, 2])] if n == 3 else [([0, 1], [2, 3]), ([0, 1], [0, 2])]
        r = run(m, n, D, K, pairs)
        series.append(r)
        print(json.dumps(r), flush=True)
        pathlib.Path(args.out).write_text(json.dumps(series, indent=1) + '\n')
        assert r['quotient_dim'] == r['dancing_matchings'], 'control: quotient dimension against the dance count'
    # the F_2 control at six pigeons, five holes, relative to H cap V_2 (135 non-matching monomials of degree <= 2)
    f2 = series[1]
    shift = 466 - (1 + 30 + 300)
    assert f2['W_mod_H'] + shift == 276, f'control: W {f2["W_mod_H"] + shift}'
    assert f2['singles'][str([0, 1])] + shift == 332, 'control: single kernel'
    assert f2['pairs'][0]['J_mod_H'] + shift == 300, 'positive control: disjoint pair over F_2'
    assert f2['pairs'][1]['J_mod_H'] + shift == 290, 'control: overlapping pair over F_2'


if __name__ == '__main__':
    main()
