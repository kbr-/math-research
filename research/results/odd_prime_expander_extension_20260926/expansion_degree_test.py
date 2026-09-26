#!/usr/bin/env python3
"""Does |N(U)| >= c|U| for all U within S (c = 3 and c = 5/2) force H~_{s-2}(M(G[S]); F_3) = 0 when rows have
degrees 3..5 rather than exactly 5?  Random rows on few holes; reuses matching_complex.py (FLINT ranks). Reports
by s and c the number of sampled S meeting the condition and the number with nonzero homology."""
import itertools, json, sys
import numpy as np
sys.path.insert(0, __file__.rsplit('/', 1)[0])
import matching_complex as mc

rng = np.random.default_rng(20260928)

def ok(nbrs, c):
    s = len(nbrs)
    return all(len(set().union(*[nbrs[i] for i in U])) >= c * len(U)
               for u in range(1, s + 1) for U in itertools.combinations(range(s), u))

res = []
for c in (3.0, 2.5):
    for s in (2, 3, 4, 5):
        st = {'c': c, 's': s, 'meet': 0, 'nonzero': 0}
        tries = 0
        while st['meet'] < 40 and tries < 20000:
            tries += 1
            h = int(np.ceil(c * s)) + int(rng.integers(0, 2))
            nbrs = [frozenset(rng.choice(h, size=int(rng.integers(3, 6)), replace=False).tolist()) for _ in range(s)]
            if not ok(nbrs, c):
                continue
            st['meet'] += 1
            if mc.reduced_homology(nbrs, s - 2) != 0:
                st['nonzero'] += 1
        res.append(st); print(st, flush=True)
if '--out' in sys.argv:
    json.dump(res, open(sys.argv[sys.argv.index('--out') + 1], 'w'), indent=1)
