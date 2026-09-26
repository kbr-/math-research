#!/usr/bin/env python3
"""Selector span of restricted product-statistic forms L = sum_{i,t} alpha_i beta_t x_{it} + b over F_3.

Falsification test for the second restriction review: after freezing and restriction, a product-statistic
form restricts to sum over the expander cells (i,t) in G' of alpha_i beta_t y_{it} + const. G' is modelled as
r residual rows with 5 distinct random holes each out of h' holes. Blocks of N forms with independent random
(alpha, beta, b). Reports the span dimension of the selectors 1 - L^2 (multilinear, Booleanity only) against
1 + v + C(v,2), v = 5r. Exact GF(3) ranks; reuses the routines of restricted_span.py.
"""
import json, sys
import numpy as np
sys.path.insert(0, __file__.rsplit('/', 1)[0])
from restricted_span import rank3, selector_vec

rng = np.random.default_rng(20260927)
res = []
for r, hp in ((2, 6), (2, 20)):
    cells = []
    for i in range(r):
        for t in rng.choice(hp, size=5, replace=False):
            cells.append((i, int(t)))
    v = len(cells)
    for N in (20, 60, 120):
        rows = []
        for _ in range(N):
            al = rng.integers(0, 3, size=r); be = rng.integers(0, 3, size=hp); b = int(rng.integers(0, 3))
            a = np.array([al[i] * be[t] % 3 for (i, t) in cells])
            rows.append(selector_vec(a, b, v))
        res.append({'rows_r': r, 'holes': hp, 'v': v, 'N': N, 'span': int(rank3(np.array(rows))),
                    'max_quadratic': 1 + v + v * (v - 1) // 2})
        print(res[-1], flush=True)
if '--out' in sys.argv:
    json.dump(res, open(sys.argv[sys.argv.index('--out') + 1], 'w'), indent=1)
