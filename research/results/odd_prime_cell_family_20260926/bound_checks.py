#!/usr/bin/env python3
"""Sanity checks for two imported inequalities used by the cell-family theorem (thm:cell-family-w).

1. Ahle's Poisson moment bound: E[Z^q] <= (q / ln(1 + q/lam))^q for Z ~ Poisson(lam),
   computed exactly as the Touchard polynomial sum_w S(q,w) lam^w (exact rationals for lam, floats for the log).
2. The chord bound 1 - e^{-x} >= 2(1 - e^{-1/2}) x on [0, 1/2].
Grid: q = 1..60, lam in {1e-6, 1e-3, 0.01, 0.1, 1, 5, 20, 100}. Prints the worst ratio.
"""
import json, math, sys
from fractions import Fraction

def stirling2_row(q):
    S = [[0] * (q + 1) for _ in range(q + 1)]
    S[0][0] = 1
    for a in range(1, q + 1):
        for w in range(1, a + 1):
            S[a][w] = w * S[a - 1][w] + S[a - 1][w - 1]
    return S

Q = 60
S = stirling2_row(Q)
worst = 0.0
for q in range(1, Q + 1):
    for lam in (1e-6, 1e-3, 0.01, 0.1, 1.0, 5.0, 20.0, 100.0):
        L = Fraction(lam)
        touch = sum(S[q][w] * L ** w for w in range(1, q + 1))
        lhs = math.log(touch)
        rhs = q * (math.log(q) - math.log(math.log1p(q / lam)))
        worst = max(worst, lhs - rhs)
chord = min((1 - math.exp(-x)) / x for x in [i / 10000 for i in range(1, 5001)])
out = {'max log(E Z^q) - log(bound)': worst, 'min (1-e^-x)/x on (0,1/2]': chord,
       'chord constant 2(1-e^-1/2)': 2 * (1 - math.exp(-0.5))}
print(json.dumps(out, indent=1))
if '--out' in sys.argv:
    json.dump(out, open(sys.argv[sys.argv.index('--out') + 1], 'w'), indent=1)
