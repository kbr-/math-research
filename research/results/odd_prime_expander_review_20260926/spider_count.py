#!/usr/bin/env python3
"""Count spider centres in random residual expanders (test of the spider-count heuristic in the spider entry).

Residual model of thm:cell-family-w: r = h+1 rows, each a uniform 5-subset of h' holes. A row c is a spider centre
if its five holes can be assigned distinct other rows (legs, one per hole, each meeting c's holes only at its own
hole) such that every leg has a hole private within {c} + legs. Greedy search per centre (a lower bound on the
count). Reports the fraction of rows that are centres for h' = h and h' = h/2."""
import json, sys
import numpy as np

def count(h, hp, seed):
    rng = np.random.default_rng(seed)
    rows = [frozenset(rng.choice(hp, size=5, replace=False).tolist()) for _ in range(h + 1)]
    at = {}
    for i, R in enumerate(rows):
        for t in R:
            at.setdefault(t, []).append(i)
    centres = 0
    for c, R in enumerate(rows):
        legs, ok = [], True
        for t in sorted(R):
            cand = [j for j in at[t] if j != c and j not in legs and len(rows[j] & R) == 1]
            if not cand:
                ok = False; break
            legs.append(cand[0])
        if not ok:
            continue
        S = [c] + legs
        if all(any(all(u not in rows[o] for o in S if o != l) for u in rows[l]) for l in legs):
            centres += 1
    return centres / (h + 1)

res = []
for h in (500, 2000):
    for frac in (1.0, 0.5):
        hp = int(h * frac)
        fr = [count(h, hp, s) for s in range(3)]
        res.append({'h': h, 'holes': hp, 'centre_fraction': [round(x, 4) for x in fr]}); print(res[-1], flush=True)
if '--out' in sys.argv:
    json.dump(res, open(sys.argv[sys.argv.index('--out') + 1], 'w'), indent=1)
