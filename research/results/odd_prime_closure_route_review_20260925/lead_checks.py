#!/usr/bin/env python3
"""Two cheap lead tests for the closure-route review (N = 10, p = 3; seconds).

1. Link uniformity (Gotzmann/Macaulay lead): for each member of vanishing_tops.py and e <= 2,
   |Y| <= 2, is the space of vanishing tops of the link Z_Y equal to pi_Y(a_{empty,e}), the tops of Z
   with every monomial meeting Y deleted?  Reports the number of (Y, e) where it fails, and whether
   the link space is larger or smaller.
2. Spin-coupling bridge: Jordan type of r = sum_j x_j on W = F_3[x_1..x_N]/(x_j^2) (N doublets coupled),
   from the ranks of r and r^2 in every degree; the modular Clebsch-Gordan prediction for J_2^(x)N over
   Z/3 is a free module plus one short summand.
"""
import itertools, json, sys
import numpy as np
sys.path.insert(0, __file__.rsplit('/', 1)[0])
from vanishing_tops import rref3, nullspace3, rank3

P = 3
N, m = 10, 11
rng = np.random.default_rng(20260925)
phi = rng.integers(0, 3, size=(4, N))
form = lambda c, b: int(np.dot(phi[b], c) % 3)
clause = lambda c, i, S, k: form(c, i) == k[i] and all(form(c, j) != k[j] for j in S)
members = {
    'one clause, k=1': lambda c: not clause(c, 0, [1], {0: 0, 1: 0}),
    "two-block pair, k=1, i=i'": lambda c: not clause(c, 0, [1], {0: 0, 1: 0}) and not clause(c, 0, [1], {0: 1, 1: 1}),
    'three clauses on four forms': lambda c: not clause(c, 0, [1], {0: 0, 1: 0}) and not clause(c, 2, [3], {2: 1, 3: 2})
                                   and not clause(c, 1, [2], {1: 2, 2: 0}),
}
out = {'uniformity': {}}
for name, allowed in members.items():
    pts = np.array([c for c in itertools.product((0, 1), repeat=N) if sum(c) % 3 == m % 3 and allowed(c)])
    def tops(Y, e):
        rest = [j for j in range(N) if j not in Y]
        sel = pts[np.all(pts[:, list(Y)] == 1, axis=1)] if Y else pts
        mons = [mu for k in range(e + 1) for mu in itertools.combinations(rest, k)]
        E = np.array([[int(np.all(s[list(mu)] == 1)) if mu else 1 for mu in mons] for s in sel])
        ker = nullspace3(E)
        ti = [i for i, mu in enumerate(mons) if len(mu) == e]
        return [mons[i] for i in ti], (rref3(ker[:, ti])[0] if len(ker) else np.zeros((0, len(ti)), int))
    fails = {'larger': 0, 'smaller': 0, 'other': 0, 'checked': 0}
    for e in (1, 2):
        mus0, T0 = tops((), e)
        for ysz in (1, 2):
            for Y in itertools.combinations(range(N), ysz):
                mus, T = tops(Y, e)
                idx = {mu: i for i, mu in enumerate(mus)}
                proj = np.zeros((len(T0), len(mus)), int)
                for r_, row in enumerate(T0):
                    for mu, cf in zip(mus0, row):
                        if cf and mu in idx:
                            proj[r_, idx[mu]] = cf
                rp, rt = rank3(proj), rank3(T)
                both = rank3(np.vstack([proj, T])) if len(T) or len(proj) else 0
                fails['checked'] += 1
                if both == rp == rt:
                    continue
                if both == rt and rt > rp:
                    fails['larger'] += 1
                elif both == rp and rp > rt:
                    fails['smaller'] += 1
                else:
                    fails['other'] += 1
    out['uniformity'][name] = fails
    print(name, fails, flush=True)
# spin coupling: Jordan type of r on W_N
dims = [len(list(itertools.combinations(range(N), d))) for d in range(N + 1)]
def rmat(d):
    src = list(itertools.combinations(range(N), d)); tgt = {c: i for i, c in enumerate(itertools.combinations(range(N), d + 1))}
    R = np.zeros((len(src), len(tgt)), int)
    for i, Y in enumerate(src):
        for j in range(N):
            if j not in Y:
                R[i, tgt[tuple(sorted(Y + (j,)))]] = 1
    return R
R = {d: rmat(d) for d in range(N)}
rk1 = {d: rank3(R[d]) for d in range(N)}
rk2 = {d: rank3(R[d] @ R[d + 1]) for d in range(N - 1)}
short = {d: dims[d] - rk1.get(d, 0) - rk2.get(d - 2, 0) for d in range(N + 1)}
out['spin_coupling'] = {'N': N, 'short_strings_ending_at': short}
print('W_N short strings', short, flush=True)
if '--out' in sys.argv:
    json.dump(out, open(sys.argv[sys.argv.index('--out') + 1], 'w'), indent=1)
