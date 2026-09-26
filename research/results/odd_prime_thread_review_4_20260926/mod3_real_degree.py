"""Real degree of the mod-3 zero indicator, for the thread review of 26 September 2026.

Statement tested: over the reals, the multilinear polynomial of f(x) = [x_1 + ... + x_n = 0 mod 3]
on {0,1}^n has degree n or n-1 or n-2 (it is symmetric, so its degree is the degree of the
univariate interpolant of k -> [k = 0 mod 3] on k = 0..n, by Minsky-Papert symmetrization).
Low real degree is what a polynomial-method (Aaronson-Shi) transfer would need.
"""
import json, sys
from fractions import Fraction

def interp_degree(vals):
    # degree = largest d with nonzero d-th finite difference at 0
    diffs = [Fraction(v) for v in vals]
    deg = 0
    for d in range(1, len(vals)):
        diffs = [diffs[i+1] - diffs[i] for i in range(len(diffs)-1)]
        if any(x != 0 for x in diffs):
            deg = d
    return deg

out = [{'n': n, 'real_degree': interp_degree([1 if k % 3 == 0 else 0 for k in range(n+1)])}
       for n in range(3, 31)]
json.dump(out, open(sys.argv[1], 'w'), indent=1)
print(json.dumps(out))
