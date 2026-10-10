#!/usr/bin/env python3
"""Indices of the product series for M independent subspace rows of codimension w in dimension n.

Statement computed (about a power series, not about any system): the coefficients c_d of
(1+z)^n (1 - (z/(1+z))^w)^M, the series a quotient by M rows would have if the rows' multiples had only
the forced relations; equivalently (1+z)^(n-wM) ((1+z)^w - z^w)^M.  The graded index is the first d with
c_d <= 0, the cumulative index the first d with c_0 + ... + c_d <= 0 (null when there is none up to n).
Exact integer arithmetic.  Arguments: --out PATH, then cases n:w:M; one JSON line per case.  A case
n:w1:M1:w2:M2... has rows of several codimensions: the series (1+z)^n prod_i (1 - (z/(1+z))^w_i)^M_i.
With --levels each single-kind line also reports the level profile at the last degree j before the graded
index: the real X with binom(X, j) = c_j (its Kruskal-Katona dimension), X/(2j), and whether the coefficients
still increase there; a level bound binom(X, j) with X about 2j is what a thin top window would show.
"""
import argparse
import json
from math import comb, lgamma, log


def binomial(a, i):
    """Coefficient of z^i in (1+z)^a, also for negative a."""
    if i < 0:
        return 0
    return comb(a, i) if a >= 0 else (-1) ** i * comb(i - a - 1, i)


def coefficients(n, w, rows):
    return [sum((-1) ** j * comb(rows, j) * binomial(n - w * j, d - w * j) for j in range(min(rows, d // w) + 1))
            for d in range(n + 1)]


def mixed_coefficients(n, kinds):
    """Coefficients through degree n for rows of several codimensions, kinds = [(w, M), ...]: with W the sum
    of w M, the series is (1+z)^(n-W) prod ((1+z)^w - z^w)^M, a polynomial product times one binomial series."""
    product = [1]
    for w, rows in kinds:
        factor = [comb(w, i) for i in range(w)]
        for _ in range(rows):
            product = [sum(product[i] * factor[d - i] for i in range(max(0, d - w + 1), min(d, len(product) - 1) + 1))
                       for d in range(min(n, len(product) + w - 2) + 1)]
    power = n - sum(w * rows for w, rows in kinds)
    return [sum(product[i] * binomial(power, d - i) for i in range(min(d, len(product) - 1) + 1))
            for d in range(n + 1)]


def indices(n, w, rows, kinds=None):
    graded = cumulative = None
    total = 0
    for d, c in enumerate(coefficients(n, w, rows) if kinds is None else mixed_coefficients(n, kinds)):
        total += c
        if graded is None and c <= 0:
            graded = d
        if cumulative is None and total <= 0:
            cumulative = d
    return graded, cumulative


def level_profile(coeffs, graded):
    """At j = graded - 1: the real X >= j with binom(X, j) = c_j, by bisection on logarithms."""
    j = graded - 1
    if j < 1:
        return None
    target = log(coeffs[j])
    low, high = float(j), float(len(coeffs) - 1)
    for _ in range(80):
        mid = (low + high) / 2
        if lgamma(mid + 1) - lgamma(j + 1) - lgamma(mid - j + 1) < target:
            low = mid
        else:
            high = mid
    return {'last_level': j, 'kk_dimension': round(high, 3), 'ratio_to_2j': round(high / (2 * j), 4),
            'increasing_at_end': coeffs[j] > coeffs[j - 1]}


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument('--out', required=True)
    ap.add_argument('--levels', action='store_true', help='also report the level profile before the index')
    ap.add_argument('cases', nargs='+', help='n:w:M')
    args = ap.parse_args()
    with open(args.out, 'w') as out:
        for case in args.cases:
            numbers = list(map(int, case.split(':')))
            if len(numbers) > 3:
                if len(numbers) % 2 == 0 or any(not (1 <= w <= numbers[0] and rows >= 1)
                                                for w, rows in zip(numbers[1::2], numbers[2::2])):
                    raise SystemExit(f'{case}: need n:w1:M1:w2:M2... with 1 <= w <= n and M >= 1')
                kinds = list(zip(numbers[1::2], numbers[2::2]))
                graded, cumulative = indices(numbers[0], None, None, kinds)
                out.write(json.dumps({'n': numbers[0], 'kinds': kinds, 'graded_index': graded,
                                      'cumulative_index': cumulative}) + '\n')
                continue
            n, w, rows = numbers
            if not (1 <= w <= n and rows >= 1):
                raise SystemExit(f'{case}: need 1 <= w <= n and M >= 1')
            graded, cumulative = indices(n, w, rows)
            line = {'n': n, 'w': w, 'rows': rows, 'graded_index': graded, 'cumulative_index': cumulative}
            if args.levels and graded is not None:
                line['levels'] = level_profile(coefficients(n, w, rows), graded)
            out.write(json.dumps(line) + '\n')


if __name__ == '__main__':
    main()
