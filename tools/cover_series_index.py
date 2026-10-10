#!/usr/bin/env python3
"""Indices of the product series for M independent subspace rows of codimension w in dimension n.

Statement computed (about a power series, not about any system): the coefficients c_d of
(1+z)^n (1 - (z/(1+z))^w)^M, the series a quotient by M rows would have if the rows' multiples had only
the forced relations; equivalently (1+z)^(n-wM) ((1+z)^w - z^w)^M.  The graded index is the first d with
c_d <= 0, the cumulative index the first d with c_0 + ... + c_d <= 0 (null when there is none up to n).
Exact integer arithmetic.  Arguments: --out PATH, then cases n:w:M; one JSON line per case.
"""
import argparse
import json
from math import comb


def binomial(a, i):
    """Coefficient of z^i in (1+z)^a, also for negative a."""
    if i < 0:
        return 0
    return comb(a, i) if a >= 0 else (-1) ** i * comb(i - a - 1, i)


def coefficients(n, w, rows):
    return [sum((-1) ** j * comb(rows, j) * binomial(n - w * j, d - w * j) for j in range(min(rows, d // w) + 1))
            for d in range(n + 1)]


def indices(n, w, rows):
    graded = cumulative = None
    total = 0
    for d, c in enumerate(coefficients(n, w, rows)):
        total += c
        if graded is None and c <= 0:
            graded = d
        if cumulative is None and total <= 0:
            cumulative = d
    return graded, cumulative


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument('--out', required=True)
    ap.add_argument('cases', nargs='+', help='n:w:M')
    args = ap.parse_args()
    with open(args.out, 'w') as out:
        for case in args.cases:
            n, w, rows = map(int, case.split(':'))
            if not (1 <= w <= n and rows >= 1):
                raise SystemExit(f'{case}: need 1 <= w <= n and M >= 1')
            graded, cumulative = indices(n, w, rows)
            out.write(json.dumps({'n': n, 'w': w, 'rows': rows, 'graded_index': graded,
                                  'cumulative_index': cumulative}) + '\n')


if __name__ == '__main__':
    main()
