#!/usr/bin/env python3
"""Fiber uniformity and freeness of the fibers' sum and intersection (lem:hole-splitting), one row, p = 3.

For a member Z on N = 10 holes and a hole j, with fibers Z^0, Z^1 on the other 9 holes, compute for
e = 1, 2 the coefficient systems S -> a_{S,e}(Z^0), a_{S,e}(Z^1), their sum and intersection, and
the short Jordan strings of r on each (strings of length < 3 ending in degree d; 0 through the
range means free there). Also count the hole sets S where a(Z^0) != a(Z^1) (fiber non-uniformity).
Degrees d <= 4 (the column tensor powers on 9 - e holes are free below (9-e)/2).
Hole j is either a free hole (column of zeros in every form) or a hole in the forms' supports.
"""
import itertools, json, sys
import numpy as np
sys.path.insert(0, __file__.rsplit('/', 1)[0])
from vanishing_tops import rref3, nullspace3, rank3

P = 3
N, m = 10, 11
rng = np.random.default_rng(20260925)
phi = rng.integers(0, 3, size=(4, N))
phi[:, 9] = 0                                   # hole 9 is free: no form involves it
form = lambda c, b: int(np.dot(phi[b], c) % 3)
clause = lambda c, i, S, k: form(c, i) == k[i] and all(form(c, j) != k[j] for j in S)
members = {
    'slice': lambda c: True,
    'one clause, k=1': lambda c: not clause(c, 0, [1], {0: 0, 1: 0}),
    "two-block pair, k=1, i=i'": lambda c: not clause(c, 0, [1], {0: 0, 1: 0}) and not clause(c, 0, [1], {0: 1, 1: 1}),
    'three clauses on four forms': lambda c: not clause(c, 0, [1], {0: 0, 1: 0}) and not clause(c, 2, [3], {2: 1, 3: 2})
                                   and not clause(c, 1, [2], {1: 2, 2: 0}),
}
DMAX = 4


def tops(pts, holes, e):
    mons = [mu for k in range(e + 1) for mu in itertools.combinations(holes, k)]
    col = {h: i for i, h in enumerate(holes)}
    if len(pts) == 0:
        ker = np.eye(len(mons), dtype=np.int64)
    else:
        E = np.array([[int(all(p[col[h]] for h in mu)) for mu in mons] for p in pts], dtype=np.int64)
        ker = nullspace3(E)
    ti = [i for i, mu in enumerate(mons) if len(mu) == e]
    T = ker[:, ti] if len(ker) else np.zeros((0, len(ti)), dtype=np.int64)
    R = rref3(T)[0] if len(T) else T
    return [mons[i] for i in ti], R


def short_strings(holes, e, sysfun):
    """sysfun(S) -> rows (basis) over Mon_e(holes minus S) in lexicographic monomial order."""
    def coords(d):
        out = [(S, mu) for S in itertools.combinations(holes, d - e)
               for mu in itertools.combinations([h for h in holes if h not in S], e)]
        return out, {c: i for i, c in enumerate(out)}
    C = {d: coords(d) for d in range(e, DMAX + 2)}
    cache = {}
    def basis(d):
        idx = C[d][1]
        rows = []
        for S in itertools.combinations(holes, d - e):
            if S not in cache:
                cache[S] = sysfun(S)
            mus = [mu for mu in itertools.combinations([h for h in holes if h not in S], e)]
            for t in cache[S]:
                v = np.zeros(len(idx), dtype=np.int64)
                for mu, cf in zip(mus, t):
                    if cf:
                        v[idx[(S, mu)]] = cf
                rows.append(v)
        return np.array(rows, dtype=np.int64).reshape(len(rows), len(idx))
    def rmat(d):
        src, sidx = C[d]; tgt, tidx = C[d + 1]
        R = np.zeros((len(src), len(tgt)), dtype=np.int64)
        for (S, mu), i in sidx.items():
            for h in holes:
                if h in S or h in mu:
                    continue
                R[i, tidx[(tuple(sorted(S + (h,))), mu)]] += 1
        return R % P
    B = {d: basis(d) for d in range(e, DMAX + 2)}
    Rm = {d: rmat(d) for d in range(e, DMAX + 1)}
    r1 = {d: rank3(B[d] @ Rm[d]) for d in range(e, DMAX + 1)}
    r2 = {d: rank3(B[d] @ Rm[d] @ Rm[d + 1]) for d in range(e, DMAX)}
    return {d: int(len(B[d]) - r1[d] - r2.get(d - 2, 0)) for d in range(e, DMAX + 1)}, \
           {d: int(len(B[d])) for d in B}


def main():
    out = {}
    for name, allowed in members.items():
        pts = np.array([c for c in itertools.product((0, 1), repeat=N) if sum(c) % 3 == m % 3 and allowed(c)])
        out[name] = {}
        for j, kind in ((9, 'free hole'), (0, 'support hole')):
            holes = [h for h in range(N) if h != j]
            Z0 = pts[pts[:, j] == 0][:, holes]
            Z1 = pts[pts[:, j] == 1][:, holes]
            res = {}
            for e in (1, 2):
                def fib(Zf):
                    def f(S):
                        sel = Zf[np.all(Zf[:, [holes.index(h) for h in S]] == 1, axis=1)] if S else Zf
                        rest = [h for h in holes if h not in S]
                        return tops(sel[:, [holes.index(h) for h in rest]], rest, e)[1]
                    return f
                f0, f1 = fib(Z0), fib(Z1)
                nonuni = [0]
                def fsum(S):
                    a, b = f0(S), f1(S)
                    M = np.vstack([a, b]) if len(a) and len(b) else (a if len(a) else b)
                    return rref3(M)[0] if len(M) else M
                def fint(S):
                    a, b = f0(S), f1(S)
                    if len(a) == 0 or len(b) == 0:
                        return np.zeros((0, a.shape[1] if len(a) else b.shape[1]), dtype=np.int64)
                    if not (rank3(a) == rank3(b) == rank3(np.vstack([a, b]))):
                        nonuni[0] += 1
                    # intersection of row spaces: solve x a = y b
                    M = np.vstack([a, -b % 3])
                    ns = nullspace3(M.T)          # combos (x, y) with x a - y b = 0
                    if len(ns) == 0:
                        return np.zeros((0, a.shape[1]), dtype=np.int64)
                    I = (ns[:, :len(a)] @ a) % 3
                    return rref3(I)[0]
                s_sum, d_sum = short_strings(holes, e, fsum)
                s_int, d_int = short_strings(holes, e, fint)
                s0, d0 = short_strings(holes, e, f0)
                res[e] = {'short_Z0': s0, 'short_Z1': short_strings(holes, e, f1)[0], 'short_sum': s_sum,
                          'short_int': s_int, 'dim_sum': d_sum, 'dim_int': d_int, 'nonuniform_links': nonuni[0]}
            out[name][kind] = res
            print(name, kind, json.dumps(res), flush=True)
    if '--out' in sys.argv:
        json.dump({'phi': phi.tolist(), 'results': out}, open(sys.argv[sys.argv.index('--out') + 1], 'w'), indent=1)


if __name__ == "__main__":
    main()
