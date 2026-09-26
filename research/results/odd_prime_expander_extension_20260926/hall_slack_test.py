#!/usr/bin/env python3
"""Sharper test for conj:expansion-matching-connectivity: does |N(U)| >= 2|U| - 1 for all U within S (the
chessboard threshold N >= 2s - 1 generalized) already force H~_{s-2}(M(G[S]); F_3) = 0?  Rows have random degrees
2..5 on few holes to make the condition tight; reuses matching_complex.py (FLINT ranks). Reports, by s, how many
sampled S meet the condition and how many have nonzero homology, and the same for S violating it (control)."""
import itertools, json, sys
import numpy as np
sys.path.insert(0, __file__.rsplit('/', 1)[0])
import matching_complex as mc

rng = np.random.default_rng(20260927)

def slack_ok(nbrs):
    s = len(nbrs)
    return all(len(set().union(*[nbrs[i] for i in U])) >= 2 * len(U) - 1
               for u in range(1, s + 1) for U in itertools.combinations(range(s), u))

res = []
for s in (2, 3, 4, 5):
    stats = {'s': s, 'meet': 0, 'meet_nonzero': 0, 'violate': 0, 'violate_nonzero': 0}
    tries = 0
    while (stats['meet'] < 40 or stats['violate'] < 20) and tries < 5000:
        tries += 1
        h = 2 * s - 1 + int(rng.integers(0, 3))
        nbrs = [frozenset(rng.choice(h, size=int(rng.integers(2, min(5, h) + 1)), replace=False).tolist())
                for _ in range(s)]
        key = 'meet' if slack_ok(nbrs) else 'violate'
        if stats[key] >= (40 if key == 'meet' else 20):
            continue
        stats[key] += 1
        if mc.reduced_homology(nbrs, s - 2) != 0:
            stats[key + '_nonzero'] += 1
    res.append(stats); print(stats, flush=True)
if '--out' in sys.argv:
    json.dump(res, open(sys.argv[sys.argv.index('--out') + 1], 'w'), indent=1)
