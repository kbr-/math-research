#!/usr/bin/env python3
"""Exact check of the cell-splitting identity (lem:cell-splitting) for W clauses on cell forms, p = 3.

Board: m rows, N holes; P = column-injective assignments (each hole empty or one row). Q = assignments on
which two W clauses (normalized, on random affine forms in the cells) vanish. A_d(X) = degree-d tops of
polynomials of degree <= d (in the cells, reduced by x^2 = x and x_ij x_i'j = 0) vanishing on X.
For column j, fibers Q^{(e)} (column j empty) and Q^{(i)} (row i at column j) on the other holes. Claim:
  dim A_d(Q) = sum_i dim A_{d-1}(Q^{(i)}) + dim A_{d-1}(Q^e) - dim(A_{d-1}(Q^e) cap cap_i A_{d-1}(Q^{(i)}))
               + dim cap_{all states s} A_d(Q^{(s)}).
Also checks the subspace statement for the column-free part: the projection of A_d(Q) onto monomials
without column j equals cap_s A_d(Q^{(s)}).
Sizes: m = 3, N = 5: 4^5 = 1024 assignments, at most 376 monomials of degree <= 3.
"""
import itertools, json, sys
import numpy as np
sys.path.insert(0, __file__.rsplit('/', 1)[0] + '/../odd_prime_closure_route_review_20260925')
from vanishing_tops import rref3, nullspace3, rank3

P = 3


def monomials(cells_by_col, d):
    """Column-injective monomials (sets of cells, at most one per column) of degree <= d."""
    cols = sorted(cells_by_col)
    out = [()]
    for k in range(1, d + 1):
        for cs in itertools.combinations(cols, k):
            for choice in itertools.product(*[cells_by_col[c] for c in cs]):
                out.append(tuple(choice))
    return out


def tops_space(points, cells_by_col, d):
    """Rows: basis of degree-d tops (coordinates over degree-d monomials) of the vanishing ideal."""
    mons = monomials(cells_by_col, d)
    if len(points) == 0:
        ker = np.eye(len(mons), dtype=np.int64)
    else:
        E = np.array([[int(all(pt.get(c[1]) == c[0] for c in mu)) for mu in mons] for pt in points], dtype=np.int64)
        ker = nullspace3(E)
    ti = [i for i, mu in enumerate(mons) if len(mu) == d]
    T = ker[:, ti] if len(ker) else np.zeros((0, len(ti)), dtype=np.int64)
    return [mons[i] for i in ti], (rref3(T)[0] if len(T) else T)


def embed(mus, T, target):
    idx = {mu: i for i, mu in enumerate(target)}
    M = np.zeros((len(T), len(target)), dtype=np.int64)
    for r, row in enumerate(T):
        for mu, cf in zip(mus, row):
            if cf:
                M[r, idx[mu]] = cf
    return M


def inter_all(mats):
    mats = [M for M in mats]
    cur = mats[0]
    for M in mats[1:]:
        if len(cur) == 0 or len(M) == 0:
            return np.zeros((0, mats[0].shape[1]), dtype=np.int64)
        ns = nullspace3(np.vstack([cur, (-M) % 3]).T)
        cur = rref3((ns[:, :len(cur)] @ cur) % 3)[0] if len(ns) else np.zeros((0, cur.shape[1]), dtype=np.int64)
    return cur


def main():
    m, N, dmax = 3, 5, 3
    rng = np.random.default_rng(20260925)
    res = []
    for trial in range(6):
        # affine forms on cells: coefficient per (row, hole) and a constant
        F = [(rng.integers(0, 3, size=(m, N)), int(rng.integers(0, 3))) for _ in range(3)]
        val = lambda pt, f: (sum(f[0][r][h] for h, r in pt.items()) + f[1]) % 3
        chi = lambda v, a: v == a
        # two W clauses chi_a(l0) (l1 - b): forbidden where l0 = a and l1 != b
        ncl = 2 if trial < 2 else 5
        cls = [(int(a), int(b), int(rng.integers(0, 3)), int(rng.integers(0, 3)))
               for a, b in [(0, 1), (0, 2), (1, 2), (2, 0), (1, 0)][:ncl]]
        allP = []
        for states in itertools.product(range(-1, m), repeat=N):
            allP.append({h: r for h, r in enumerate(states) if r >= 0})
        injective = trial % 2 == 1          # odd trials: each row used at most once (pigeon injectivity)
        Q = [pt for pt in allP if not any(val(pt, F[i]) == a and val(pt, F[j]) != b for (i, j, a, b) in cls)
             and (not injective or len(set(pt.values())) == len(pt))]
        j = 0
        rest = list(range(1, N))
        cbc_full = {h: [(r, h) for r in range(m)] for h in range(N)}
        cbc_rest = {h: [(r, h) for r in range(m)] for h in rest}
        fib = {'e': [{h: r for h, r in pt.items() if h != j} for pt in Q if j not in pt]}
        for i in range(m):
            fib[i] = [{h: r for h, r in pt.items() if h != j} for pt in Q if pt.get(j) == i]
        out = {'Q': len(Q), 'P': len(allP), 'clauses': ncl, 'row_injective': injective}
        for d in range(1, dmax + 1):
            musQ, AQ = tops_space(Q, cbc_full, d)
            lhs = rank3(AQ) if len(AQ) else 0
            mus_d1 = [mu for mu in monomials(cbc_rest, d - 1) if len(mu) == d - 1]
            mus_d = [mu for mu in monomials(cbc_rest, d) if len(mu) == d]
            A1 = {s: embed(*tops_space(fib[s], cbc_rest, d - 1), mus_d1) for s in fib}
            A0 = {s: embed(*tops_space(fib[s], cbc_rest, d), mus_d) for s in fib}
            term1 = sum(rank3(A1[i]) if len(A1[i]) else 0 for i in range(m))
            ge = rank3(A1['e']) if len(A1['e']) else 0
            cap1 = inter_all([A1[s] for s in fib])
            term2 = ge - (rank3(cap1) if len(cap1) else 0)
            cap0 = inter_all([A0[s] for s in fib])
            term3 = rank3(cap0) if len(cap0) else 0
            # projection of A_d(Q) onto column-free monomials versus cap0
            idx = {mu: k for k, mu in enumerate(mus_d)}
            proj = np.zeros((len(AQ), len(mus_d)), dtype=np.int64)
            for r_, row in enumerate(AQ):
                for mu, cf in zip(musQ, row):
                    if cf and all(c[1] != j for c in mu):
                        proj[r_, idx[mu]] = cf
            pr = rank3(proj) if len(proj) else 0
            same = pr == term3 and (rank3(np.vstack([proj, cap0])) if len(proj) and len(cap0) else max(pr, term3)) == pr
            out[d] = {'dim_A': lhs, 'predicted': term1 + term2 + term3, 'projection_equals_cap': bool(same)}
        res.append(out)
        print(trial, out, flush=True)
    if '--out' in sys.argv:
        json.dump(res, open(sys.argv[sys.argv.index('--out') + 1], 'w'), indent=1)


if __name__ == '__main__':
    main()
