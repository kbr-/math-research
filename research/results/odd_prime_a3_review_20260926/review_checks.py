#!/usr/bin/env python3
"""Review checks for the product-top line, p = 3.

L1 (Wood-type balance): the law of one coordinate tau_z of a product top e_2(l) e_2(l') on four columns
   with one cell each: tau_z = sum over the 6 ordered splits (P, Q) of l_P l'_Q, 8 uniform F_3 variables.
   Wood's universality needs every entry alpha-balanced: max_c Pr[tau_z = c] <= 1 - alpha.
B1 (geminal powers): in the weak monomial algebra on N = 6 columns with m = 1, e_2(l)^2 over F_3
   (predicted 0, since l^3 = 0 and e_2 = 2 l^2) against the integer value 6 e_4(l).
"""
import itertools, json, sys
from collections import Counter

splits = [((0, 1), (2, 3)), ((0, 2), (1, 3)), ((0, 3), (1, 2))]
cnt = Counter()
for v in itertools.product(range(3), repeat=8):
    l, lp = v[:4], v[4:]
    s = sum(l[a] * l[b] * lp[c] * lp[d] + l[c] * l[d] * lp[a] * lp[b] for (a, b), (c, d) in splits) % 3
    cnt[s] += 1
law = {k: cnt[k] / 3 ** 8 for k in range(3)}
print('L1 law of tau_z:', law, flush=True)


def e2_squared(coeffs, mod):
    """Coefficients of e_2(l)^2 on 4-subsets, for l with one cell per column (m = 1)."""
    N = len(coeffs)
    e2 = {S: coeffs[S[0]] * coeffs[S[1]] for S in itertools.combinations(range(N), 2)}
    out = Counter()
    for A, x in e2.items():
        for B, y in e2.items():
            if set(A) & set(B):
                continue
            out[tuple(sorted(A + B))] += x * y
    return {S: (c % mod if mod else c) for S, c in out.items()}


coeffs = [1, 2, 1, 1, 2, 2]
sq3 = e2_squared(coeffs, 3)
sqZ = e2_squared(coeffs, 0)
e4 = {S: coeffs[S[0]] * coeffs[S[1]] * coeffs[S[2]] * coeffs[S[3]] for S in itertools.combinations(range(6), 4)}
res = {'L1_law': law, 'B1_char3_all_zero': all(v == 0 for v in sq3.values()),
       'B1_integer_equals_6_e4': all(sqZ[S] == 6 * e4[S] for S in e4)}
print('B1', res['B1_char3_all_zero'], res['B1_integer_equals_6_e4'], flush=True)
if '--out' in sys.argv:
    json.dump(res, open(sys.argv[sys.argv.index('--out') + 1], 'w'), indent=1)
