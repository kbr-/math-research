#!/usr/bin/env python3
"""Cheap tests for the second closure-route review (one row, p = 3; each part seconds to a minute).

T1  Distributivity of the four fibers' vanishing tops (holes 0, 1; e = 2) on links |S| = 3 at N = 12,
    for the two-block pair and three clauses (atom_check.py used links up to |S| = 4).
T2  Generic weights: Jordan type of r_c = sum_j c_j e_j (random c_j in F_3^*) on A_2 of the two-block pair at
    N = 10, degrees <= 4, versus r = sum_j e_j (short strings; 0 = free in range).
T3  Falsification: a six-clause member at N = 10 (density below one half): short strings of A_e(Z) and of the
    sum and intersection of its fibers at hole 0, e = 1, 2, degrees <= 4.
B1  Nonzero atoms X_T / Y_T of the four-fiber lattice at N = 12 (dimension in degree 4), for the poset picture.
"""
import itertools, json, sys
import numpy as np
sys.path.insert(0, __file__.rsplit('/', 1)[0])
from vanishing_tops import rref3, rank3
from fiber_check import tops, short_strings
from distributivity_check import inter, dimsum
import fiber_check

out = {}
# ---------- T1 ----------
N = 12; m = N + 1
rng = np.random.default_rng(20260925 + N)
phi = rng.integers(0, 3, size=(4, N)); phi[:, N - 1] = 0
form = lambda c, b: int(np.dot(phi[b], c) % 3)
clause = lambda c, i, S, k: form(c, i) == k[i] and all(form(c, j) != k[j] for j in S)
mem12 = {
    "two-block pair": lambda c: not clause(c, 0, [1], {0: 0, 1: 0}) and not clause(c, 0, [1], {0: 1, 1: 1}),
    "three clauses": lambda c: not clause(c, 0, [1], {0: 0, 1: 0}) and not clause(c, 2, [3], {2: 1, 3: 2})
                     and not clause(c, 1, [2], {1: 2, 2: 0}),
}
holes = [h for h in range(N) if h not in (0, 1)]
t1 = {}
for name, allowed in mem12.items():
    pts = np.array([c for c in itertools.product((0, 1), repeat=N) if sum(c) % 3 == m % 3 and allowed(c)])
    fib = {(a, b): pts[(pts[:, 0] == a) & (pts[:, 1] == b)][:, holes] for a in (0, 1) for b in (0, 1)}
    fails = checked = 0
    for S in itertools.combinations(holes, 3):
        rest = [h for h in holes if h not in S]
        sub = []
        for Zf in fib.values():
            sel = Zf[np.all(Zf[:, [holes.index(h) for h in S]] == 1, axis=1)]
            sub.append(tops(sel[:, [holes.index(h) for h in rest]], rest, 2)[1])
        bad = False
        for fam in [list(range(4))] + [list(t) for t in itertools.combinations(range(4), 3)]:
            lhs = dimsum([sub[k] for k in fam]); rhs = 0
            for r in range(1, len(fam) + 1):
                for T in itertools.combinations(fam, r):
                    I = sub[T[0]]
                    for k in T[1:]:
                        I = inter(I, sub[k])
                    rhs += (-1) ** (r + 1) * (rank3(I) if len(I) else 0)
            bad |= lhs != rhs
        fails += int(bad); checked += 1
    t1[name] = {'links_S3_failing': fails, 'links_S3': checked}
    print('T1', name, t1[name], flush=True)
out['T1'] = t1
# ---------- T2 and T3 at N = 10 ----------
N10 = 10; m10 = 11
phi10 = fiber_check.phi
f10 = lambda c, b: int(np.dot(phi10[b], c) % 3)
cl10 = lambda c, i, S, k: f10(c, i) == k[i] and all(f10(c, j) != k[j] for j in S)
pair10 = lambda c: not cl10(c, 0, [1], {0: 0, 1: 0}) and not cl10(c, 0, [1], {0: 1, 1: 1})
six10 = lambda c: all(not cl10(c, i, [j], {i: a, j: b}) for (i, j, a, b) in
                      [(0, 1, 0, 0), (0, 1, 1, 1), (2, 3, 1, 2), (1, 2, 2, 0), (3, 0, 0, 1), (2, 1, 2, 2)])
def weighted_short(allowed, e, weights):
    pts = np.array([c for c in itertools.product((0, 1), repeat=N10) if sum(c) % 3 == m10 % 3 and allowed(c)])
    hol = list(range(N10))
    def sysf(S):
        sel = pts[np.all(pts[:, list(S)] == 1, axis=1)] if S else pts
        rest = [h for h in hol if h not in S]
        return tops(sel[:, rest], rest, e)[1]
    old = fiber_check.short_strings
    return short_strings_weighted(hol, e, sysf, weights)
def short_strings_weighted(holes_, e, sysfun, w):
    DMAX = 4
    def coords(d):
        o = [(S, mu) for S in itertools.combinations(holes_, d - e)
             for mu in itertools.combinations([h for h in holes_ if h not in S], e)]
        return o, {c: i for i, c in enumerate(o)}
    C = {d: coords(d) for d in range(e, DMAX + 2)}
    cache = {}
    B = {}
    for d in range(e, DMAX + 2):
        idx = C[d][1]; rows = []
        for S in itertools.combinations(holes_, d - e):
            cache.setdefault(S, sysfun(S))
            mus = list(itertools.combinations([h for h in holes_ if h not in S], e))
            for t in cache[S]:
                v = np.zeros(len(idx), dtype=np.int64)
                for mu, cf in zip(mus, t):
                    if cf: v[idx[(S, mu)]] = cf
                rows.append(v)
        B[d] = np.array(rows, dtype=np.int64).reshape(len(rows), len(idx))
    R = {}
    for d in range(e, DMAX + 1):
        src, sidx = C[d]; tgt, tidx = C[d + 1]
        M = np.zeros((len(src), len(tgt)), dtype=np.int64)
        for (S, mu), i in sidx.items():
            for h in holes_:
                if h not in S and h not in mu:
                    M[i, tidx[(tuple(sorted(S + (h,))), mu)]] += w[h]
        R[d] = M % 3
    r1 = {d: rank3(B[d] @ R[d] % 3) for d in range(e, DMAX + 1)}
    r2 = {d: rank3(B[d] @ R[d] @ R[d + 1] % 3) for d in range(e, DMAX)}
    return {d: int(len(B[d]) - r1[d] - r2.get(d - 2, 0)) for d in range(e, DMAX + 1)}
rw = np.random.default_rng(7)
t2 = {'unit weights': weighted_short(pair10, 2, [1] * N10)}
for trial in range(3):
    w = list(rw.integers(1, 3, size=N10))
    t2[f'random weights {trial}'] = weighted_short(pair10, 2, w)
print('T2', t2, flush=True)
out['T2'] = t2
t3 = {}
pts6 = np.array([c for c in itertools.product((0, 1), repeat=N10) if sum(c) % 3 == m10 % 3 and six10(c)])
t3['points'] = int(len(pts6))
for e in (1, 2):
    t3[f'A e={e}'] = weighted_short(six10, e, [1] * N10)
    hol = list(range(1, N10))
    Z0 = pts6[pts6[:, 0] == 0][:, hol]; Z1 = pts6[pts6[:, 0] == 1][:, hol]
    def fz(Zf):
        def f(S):
            sel = Zf[np.all(Zf[:, [hol.index(h) for h in S]] == 1, axis=1)] if S else Zf
            rest = [h for h in hol if h not in S]
            return tops(sel[:, [hol.index(h) for h in rest]], rest, e)[1]
        return f
    f0, f1 = fz(Z0), fz(Z1)
    def fsum(S):
        a, b = f0(S), f1(S); parts = [x for x in (a, b) if len(x)]
        return rref3(np.vstack(parts))[0] if parts else a
    def fint(S):
        return inter(f0(S), f1(S))
    t3[f'sum e={e}'] = short_strings_weighted(hol, e, fsum, {h: 1 for h in hol})
    t3[f'int e={e}'] = short_strings_weighted(hol, e, fint, {h: 1 for h in hol})
print('T3', t3, flush=True)
out['T3'] = t3
if '--out' in sys.argv:
    json.dump(out, open(sys.argv[sys.argv.index('--out') + 1], 'w'), indent=1)
