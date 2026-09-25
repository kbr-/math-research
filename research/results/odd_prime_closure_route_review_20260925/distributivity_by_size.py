#!/usr/bin/env python3
"""Distributivity failures of the fibers' vanishing tops by link size, at N = 10 and N = 12 (p = 3).

Same test as distributivity_check.py (inclusion-exclusion for the four fibers at holes 0, 1, triples and
the quadruple, e = 2, links |S| <= 2), for the two-block pair and three clauses on four forms, with
fresh seeded column forms at each N (hole N-1 free). Reports failures per |S|, to separate a
small-size artifact (failures only on the smallest links) from a persistent effect.
"""
import itertools, json, sys
import numpy as np
sys.path.insert(0, __file__.rsplit('/', 1)[0])
from vanishing_tops import rank3
from fiber_check import tops
from distributivity_check import inter, dimsum

out = {}
for N in (10, 12):
    m = N + 1
    rng = np.random.default_rng(20260925 + N)
    phi = rng.integers(0, 3, size=(4, N)); phi[:, N - 1] = 0
    form = lambda c, b: int(np.dot(phi[b], c) % 3)
    clause = lambda c, i, S, k: form(c, i) == k[i] and all(form(c, j) != k[j] for j in S)
    mem = {
        "two-block pair": lambda c: not clause(c, 0, [1], {0: 0, 1: 0}) and not clause(c, 0, [1], {0: 1, 1: 1}),
        "three clauses": lambda c: not clause(c, 0, [1], {0: 0, 1: 0}) and not clause(c, 2, [3], {2: 1, 3: 2})
                         and not clause(c, 1, [2], {1: 2, 2: 0}),
    }
    for name, allowed in mem.items():
        pts = np.array([c for c in itertools.product((0, 1), repeat=N) if sum(c) % 3 == m % 3 and allowed(c)])
        holes = [h for h in range(N) if h not in (0, 1)]
        fib = {(a, b): pts[(pts[:, 0] == a) & (pts[:, 1] == b)][:, holes] for a in (0, 1) for b in (0, 1)}
        per = {}
        for ysz in (0, 1, 2):
            fails = checked = 0
            for S in itertools.combinations(holes, ysz):
                rest = [h for h in holes if h not in S]
                sub = {}
                for k, Zf in fib.items():
                    sel = Zf[np.all(Zf[:, [holes.index(h) for h in S]] == 1, axis=1)] if S else Zf
                    sub[k] = tops(sel[:, [holes.index(h) for h in rest]], rest, 2)[1]
                keys = list(sub)
                bad = False
                for fam in [keys] + [list(t) for t in itertools.combinations(keys, 3)]:
                    lhs = dimsum([sub[k] for k in fam])
                    rhs = 0
                    for r in range(1, len(fam) + 1):
                        for T in itertools.combinations(fam, r):
                            I = sub[T[0]]
                            for k in T[1:]:
                                I = inter(I, sub[k])
                            rhs += (-1) ** (r + 1) * (rank3(I) if len(I) else 0)
                    bad |= lhs != rhs
                fails += int(bad); checked += 1
            per[ysz] = {'links_failing': fails, 'links': checked}
        out[f'N={N} {name}'] = per
        print(N, name, per, flush=True)
if '--out' in sys.argv:
    json.dump(out, open(sys.argv[sys.argv.index('--out') + 1], 'w'), indent=1)
