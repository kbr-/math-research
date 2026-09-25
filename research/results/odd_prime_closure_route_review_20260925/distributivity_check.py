#!/usr/bin/env python3
"""Distributivity of the fibers' vanishing-top subspaces at two holes (one row, p = 3, seconds).

For a member Z on N = 10 holes and holes j1, j2, the four fibers Z^{ab} = {c in Z : c_j1 = a,
c_j2 = b} live on the other 8 holes. For each hole set S (|S| <= 2) and e in {1, 2}, compare
inclusion-exclusion for the four subspaces a_{S,e}(Z^{ab}) of Mon_e(S^c):
   dim(sum of all four) versus the alternating sum of the dimensions of all intersections,
and the same for every triple. Equality for every subfamily is necessary for the subspaces to
generate a distributive lattice (a basis adapted to all of them); a gap means the iterated
hole-splitting recursion meets non-distributive sums and intersections.
"""
import itertools, json, sys
import numpy as np
sys.path.insert(0, __file__.rsplit('/', 1)[0])
from vanishing_tops import rref3, nullspace3, rank3
from fiber_check import members, tops, N, m

def inter(a, b):
    if len(a) == 0 or len(b) == 0:
        return np.zeros((0, a.shape[1] if len(a) else b.shape[1]), dtype=np.int64)
    ns = nullspace3(np.vstack([a, (-b) % 3]).T)
    return rref3((ns[:, :len(a)] @ a) % 3)[0] if len(ns) else np.zeros((0, a.shape[1]), dtype=np.int64)

def dimsum(vs):
    vs = [v for v in vs if len(v)]
    return rank3(np.vstack(vs)) if vs else 0

out = {}
for name, allowed in members.items():
    pts = np.array([c for c in itertools.product((0, 1), repeat=N) if sum(c) % 3 == m % 3 and allowed(c)])
    out[name] = {}
    for (j1, j2), kind in (((0, 1), 'two support holes'), ((0, 9), 'support and free hole')):
        holes = [h for h in range(N) if h not in (j1, j2)]
        fib = {(a, b): pts[(pts[:, j1] == a) & (pts[:, j2] == b)][:, holes] for a in (0, 1) for b in (0, 1)}
        gaps = {'quad': 0, 'triples': 0, 'checked': 0, 'max_gap': 0}
        for e in (1, 2):
            for ysz in (0, 1, 2):
                for S in itertools.combinations(holes, ysz):
                    rest = [h for h in holes if h not in S]
                    sub = {}
                    for k, Zf in fib.items():
                        sel = Zf[np.all(Zf[:, [holes.index(h) for h in S]] == 1, axis=1)] if S else Zf
                        sub[k] = tops(sel[:, [holes.index(h) for h in rest]], rest, e)[1]
                    keys = list(sub)
                    for fam in [keys] + [list(t) for t in itertools.combinations(keys, 3)]:
                        lhs = dimsum([sub[k] for k in fam])
                        rhs = 0
                        for r in range(1, len(fam) + 1):
                            for T in itertools.combinations(fam, r):
                                I = sub[T[0]]
                                for k in T[1:]:
                                    I = inter(I, sub[k])
                                rhs += (-1) ** (r + 1) * rank3(I) if len(I) else 0
                        gap = lhs - rhs
                        if gap:
                            gaps['quad' if len(fam) == 4 else 'triples'] += 1
                            gaps['max_gap'] = max(gaps['max_gap'], abs(gap))
                    gaps['checked'] += 1
        out[name][kind] = gaps
        print(name, kind, gaps, flush=True)
if '--out' in sys.argv:
    json.dump(out, open(sys.argv[sys.argv.index('--out') + 1], 'w'), indent=1)
