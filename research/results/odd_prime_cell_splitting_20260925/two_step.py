#!/usr/bin/env python3
"""Two recursion steps of the monotone recursion (conj:good-column), column members, N = 12, p = 3, e = 2.

Step 1: split Z at a good column j1 (from good_column*.json). Step 2: for each fiber Z^a (a = 0, 1) on the
other 11 holes, count for every remaining hole j2 the links S (|S| <= 2) where a_S(Z^a_{j2,0}) is not
contained in a_S(Z^a_{j2,1}), split by |S|. A fiber has a good column if some j2 has no failing link.
Members: the two-block pair with a dense outside form (good_column_dense.py's forms) and the three clauses
on the sparse seeded forms (good_column.py's forms).
"""
import itertools, json, sys
import numpy as np
here = __file__.rsplit('/', 1)[0]
sys.path.insert(0, here); sys.path.insert(0, here + '/../odd_prime_closure_route_review_20260925')
from vanishing_tops import rank3
from fiber_check import tops

N = 12; m = N + 1; e = 2
def contained(A, B):
    if len(A) == 0: return True
    if len(B) == 0: return False
    return rank3(np.vstack([A, B])) == rank3(B)

def make(dense):
    rng = np.random.default_rng(20260925 + N)
    phi = rng.integers(0, 3, size=(4, N))
    if dense:
        phi[0] = rng.integers(1, 3, size=N)
    phi[:, N - 1] = 0
    form = lambda c, b: int(np.dot(phi[b], c) % 3)
    clause = lambda c, i, S, k: form(c, i) == k[i] and all(form(c, j) != k[j] for j in S)
    return clause

def good_counts(pts, holes):
    res = {}
    for j in holes:
        hs = [h for h in holes if h != j]
        Z0 = pts[pts[:, holes.index(j)] == 0]; Z1 = pts[pts[:, holes.index(j)] == 1]
        Z0 = Z0[:, [holes.index(h) for h in hs]]; Z1 = Z1[:, [holes.index(h) for h in hs]]
        fails = {0: 0, 1: 0, 2: 0}
        for ysz in (0, 1, 2):
            for S in itertools.combinations(hs, ysz):
                rest = [h for h in hs if h not in S]
                def t(Zf):
                    sel = Zf[np.all(Zf[:, [hs.index(h) for h in S]] == 1, axis=1)] if S else Zf
                    return tops(sel[:, [hs.index(h) for h in rest]], rest, e)[1]
                if not contained(t(Z0), t(Z1)):
                    fails[ysz] += 1
        res[j] = fails
    return res

out = {}
cases = [('two-block pair, dense l0', True, lambda cl: (lambda c: not cl(c, 0, [1], {0: 0, 1: 0}) and not cl(c, 0, [1], {0: 1, 1: 1})), 0),
         ('three clauses, sparse forms', False, lambda cl: (lambda c: not cl(c, 0, [1], {0: 0, 1: 0}) and not cl(c, 2, [3], {2: 1, 3: 2})
                                                            and not cl(c, 1, [2], {1: 2, 2: 0})), 0)]
for name, dense, mk, j1 in cases:
    allowed = mk(make(dense))
    pts = np.array([c for c in itertools.product((0, 1), repeat=N) if sum(c) % 3 == m % 3 and allowed(c)])
    holes = [h for h in range(N) if h != j1]
    rec = {}
    for a in (0, 1):
        F = pts[pts[:, j1] == a][:, holes]
        counts = good_counts(F, holes)
        good = [j for j, f in counts.items() if sum(f.values()) == 0]
        rec[f'fiber {a}'] = {'points': int(len(F)), 'good_columns': good, 'per_hole': counts}
        print(name, 'fiber', a, len(F), 'good', good, flush=True)
    out[name] = rec
if '--out' in sys.argv:
    json.dump(out, open(sys.argv[sys.argv.index('--out') + 1], 'w'), indent=1)
