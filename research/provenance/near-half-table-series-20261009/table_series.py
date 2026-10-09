#!/usr/bin/env python3
"""Product series for systems of table rows: (1+z)^(v-mk) * h(z)^m.

Statement computed (a statement about power series, not about any system): a row on k variables
with allowed set of level sizes b_0..b_k has quotient series h(z)(1+z)^(v-k), h(z) = sum b_i z^i.
If m such rows behaved as independent conditions (the analogue of semi-regularity, which accounts
for the trivial relations g_a g_b = g_b g_a that a first-order count ignores), the quotient of the
sum of their ideals would have the series S(z) = (1+z)^v * (h(z)/(1+z)^k)^m up to its first
non-positive coefficient, at index D*.  The first-order count instead predicts the least D with
m * sum_i (binom(k,i) - b_i) N_{v-k}(D-i) >= N_v(D).  For half tables of largest immunity,
b_i = binom(k,i) for i < k/2, completed in the middle level(s) to total 2^(k-1).

Output per case: v, k, m, D* (or null up to v/2), D*/v, the first-order threshold, and v/2.
Exact integer arithmetic.  Arguments: --out PATH, then cases v:k:m.
"""
import argparse
import json
import math


def half_levels(k):
    b = [0] * (k + 1)
    left = 2 ** (k - 1)
    for i in range(k + 1):
        b[i] = min(math.comb(k, i), left)
        left -= b[i]
    return b


def cumulative(n, j):
    return sum(math.comb(n, i) for i in range(0, j + 1)) if j >= 0 else 0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--out', required=True)
    ap.add_argument('cases', nargs='+')
    args = ap.parse_args()
    rows = []
    for case in args.cases:
        v, k, m = (int(x) for x in case.split(':'))
        b = half_levels(k)
        upto = v // 2 + 1
        # (1+z)^(v-mk): negative exponent in general
        e = v - m * k
        coeff = [0] * (upto + 1)
        if e >= 0:
            for j in range(min(e, upto) + 1):
                coeff[j] = math.comb(e, j)
        else:
            n = -e
            for j in range(upto + 1):
                coeff[j] = (-1) ** j * math.comb(n + j - 1, j)
        for _ in range(m):
            new = [0] * (upto + 1)
            for i, bi in enumerate(b):
                if bi == 0 or i > upto:
                    continue
                for j in range(upto + 1 - i):
                    if coeff[j]:
                        new[i + j] += bi * coeff[j]
            coeff = new
        dstar = next((j for j, c in enumerate(coeff) if c <= 0), None)
        first_order = None
        for D in range(upto + 1):
            total = m * sum((math.comb(k, i) - b[i]) * cumulative(v - k, D - i) for i in range(k + 1))
            if total >= cumulative(v, D):
                first_order = D
                break
        rows.append({'v': v, 'k': k, 'm': m, 'levels': b, 'first_nonpositive': dstar,
                     'ratio': None if dstar is None else round(dstar / v, 4),
                     'first_order_threshold': first_order, 'half': v / 2})
        print(json.dumps(rows[-1]))
    with open(args.out, 'w') as f:
        json.dump(rows, f, indent=1)


if __name__ == '__main__':
    main()
