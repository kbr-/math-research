#!/usr/bin/env python3
"""Dense-outside-form variant of good_column.py (l0 has nonzero coefficients on every hole but the free one).
Is there a monotone column? (cor:monotone-fiber-recursion), column members at N = 12, p = 3, e = 2.

For each hole j and each link S not containing j (|S| <= 2), test a_S(Z^0_j) subset a_S(Z^1_j), where
Z^0_j, Z^1_j are the fibers of Z at hole j. A column j is good when the inclusion holds on every link.
Reports, per member, the failing links per hole, split by |S| (sub-instance rule).
"""
import itertools, json, sys
import numpy as np
here = __file__.rsplit('/', 1)[0]
sys.path.insert(0, here); sys.path.insert(0, here + '/../odd_prime_closure_route_review_20260925')
from vanishing_tops import rank3
from fiber_check import tops

N = 12; m = N + 1; e = 2
rng = np.random.default_rng(20260925 + N)
phi = rng.integers(0, 3, size=(4, N)); phi[0] = rng.integers(1, 3, size=N); phi[:, N - 1] = 0   # dense outside form l0
form = lambda c, b: int(np.dot(phi[b], c) % 3)
clause = lambda c, i, S, k: form(c, i) == k[i] and all(form(c, j) != k[j] for j in S)
mem = {
    "one clause": lambda c: not clause(c, 0, [1], {0: 0, 1: 0}),
    "two-block pair": lambda c: not clause(c, 0, [1], {0: 0, 1: 0}) and not clause(c, 0, [1], {0: 1, 1: 1}),
}
def contained(A, B):
    if len(A) == 0: return True
    if len(B) == 0: return False
    return rank3(np.vstack([A, B])) == rank3(B)
out = {}
for name, allowed in mem.items():
    pts = np.array([c for c in itertools.product((0, 1), repeat=N) if sum(c) % 3 == m % 3 and allowed(c)])
    per_hole = {}
    for j in range(N):
        holes = [h for h in range(N) if h != j]
        Z0 = pts[pts[:, j] == 0][:, holes]; Z1 = pts[pts[:, j] == 1][:, holes]
        fails = {0: 0, 1: 0, 2: 0}
        for ysz in (0, 1, 2):
            for S in itertools.combinations(holes, ysz):
                rest = [h for h in holes if h not in S]
                def t(Zf):
                    sel = Zf[np.all(Zf[:, [holes.index(h) for h in S]] == 1, axis=1)] if S else Zf
                    return tops(sel[:, [holes.index(h) for h in rest]], rest, e)[1]
                if not contained(t(Z0), t(Z1)):
                    fails[ysz] += 1
        per_hole[j] = fails
        print(name, 'hole', j, fails, flush=True)
    good = [j for j, f in per_hole.items() if sum(f.values()) == 0]
    good01 = [j for j, f in per_hole.items() if f[0] == 0 and f[1] == 0]
    out[name] = {'per_hole': per_hole, 'good_columns': good, 'good_on_S_le_1': good01}
if '--out' in sys.argv:
    json.dump(out, open(sys.argv[sys.argv.index('--out') + 1], 'w'), indent=1)
