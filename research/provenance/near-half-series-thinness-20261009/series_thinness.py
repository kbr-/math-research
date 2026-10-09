#!/usr/bin/env python3
"""Kruskal-Katona dimension of the coefficients of (1+z)^n / (1+z^k)^m below their first zero.

Statement computed (a statement about power series, not about any polynomial system): for the
series S(z) = (1+z)^n / (1+z^k)^m with coefficients a_j, let D* be the least j with a_j <= 0 and,
for j < D*, X_j the least integer X >= j with binom(X, j) >= a_j.  The thin-closure endpoint asks
for level sizes at most binom(X, j) with X about 2K for j just below a cutoff K; if the levels of a
closure equalled the a_j, it would hold at K exactly when X_j <= 2j(1 + o(1)) there.  Output per
case: n, k, m, D*, the mode of a_j, log2(max a_j)/n, and for sampled j the ratio X_j / (2j); also
the least j0 with X_j <= 2j + slack for all j0 <= j < D* (slack given), i.e. the thin window.

Exact integer arithmetic.  Arguments: --out PATH, then cases n:k:m (m may be written as a multiple
of n ln 2 * 2^k with the suffix 't', e.g. 1024:2:1.0t for the unsatisfiability threshold density).
"""
import argparse
import json
import math


def series(n, k, m, upto):
    a = [math.comb(n, j) for j in range(upto + 1)]
    # divide by (1+z^k)^m: m passes of a_j -= a_{j-k}
    for _ in range(m):
        for j in range(k, upto + 1):
            a[j] -= a[j - k]
        # stop early once the first non-positive index is stable below upto
    return a


def kk_dimension(a, j):
    if j == 0:
        return 0
    x = j
    while math.comb(x, j) < a:
        x += 1
    return x


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--out', required=True)
    ap.add_argument('--slack', type=int, default=2)
    ap.add_argument('cases', nargs='+')
    args = ap.parse_args()
    rows = []
    for case in args.cases:
        n, k, m = case.split(':')
        n, k = int(n), int(k)
        m = math.ceil(float(m[:-1]) * math.log(2) * 2 ** k * n) if m.endswith('t') else int(m)
        upto = n // 2
        a = series(n, k, m, upto)
        dstar = next((j for j, v in enumerate(a) if v <= 0), None)
        top = dstar if dstar is not None else upto + 1
        mode = max(range(top), key=lambda j: a[j])
        xs = [kk_dimension(a[j], j) for j in range(top)]
        j0 = top
        while j0 > 1 and xs[j0 - 1] <= 2 * (j0 - 1) + args.slack:
            j0 -= 1
        step = max(1, top // 12)
        sample = [[j, xs[j], round(xs[j] / (2 * j), 4)] for j in range(1, top) if j % step == 0 or j >= top - 4]
        rows.append({'n': n, 'k': k, 'm': m, 'first_nonpositive': dstar, 'mode': mode,
                     'log2_max_over_n': round(math.log2(a[mode]) / n, 4),
                     'thin_window_from': j0, 'thin_window_length': top - j0, 'slack': args.slack,
                     'sample_j_X_ratio': sample,
                     'last_coefficients_log2': [round(math.log2(a[j]), 1) for j in range(max(0, top - 6), top)]})
        print(json.dumps(rows[-1]))
    with open(args.out, 'w') as f:
        json.dump(rows, f, indent=1)


if __name__ == '__main__':
    main()
