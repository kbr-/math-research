"""Cumulative index of S(z) = (1+z)^(N-2M) (1+2z)^M, the product series (1+z)^N (1 - (z/(1+z))^2)^M of the
pigeonhole principle with n+1 pigeons, n holes, affine pigeon rows and hole clauses only: N = n^2 - 1,
M = n^2 (n+1)/2.  Statement tested: the first degree d at which the partial sum of coefficients is not positive
is asymptotically c n with c < 1/2; the Hermite heuristic predicts N^2/(8M + 4N), about n/4.  Exact integers.
One-off job of 11 October 2026.

Usage: python3 index_series.py OUT.json
"""
import json
import sys
from math import comb


def neg_binom(k_exp, r):
    """Coefficient of z^r in (1+z)^(-k_exp), k_exp > 0."""
    return (-1) ** r * comb(k_exp + r - 1, r)


def cumulative_index(n):
    big_n = n * n - 1
    m = n * n * (n + 1) // 2
    k_exp = 2 * m - big_n
    assert k_exp > 0
    total = 0
    d = 0
    while True:
        h = sum(comb(m, j) * 2 ** j * neg_binom(k_exp, d - j) for j in range(d + 1))
        total += h
        if total <= 0:
            return d
        d += 1


def krawtchouk(d, x, total):
    """Binary Krawtchouk polynomial K_d(x; total), the coefficient of w^d in (1-w)^x (1+w)^(total-x)."""
    return sum((-1) ** j * comb(x, j) * comb(total - x, d - j) for j in range(d + 1))


def check_identity(n, dmax):
    """Coefficient d of the series equals K_d(M - N + d - 1; 2M - N + d - 1)."""
    big_n = n * n - 1
    m = n * n * (n + 1) // 2
    k_exp = 2 * m - big_n
    for d in range(dmax + 1):
        h = sum(comb(m, j) * 2 ** j * neg_binom(k_exp, d - j) for j in range(d + 1))
        assert h == krawtchouk(d, m - big_n + d - 1, 2 * m - big_n + d - 1), (n, d)


def main(out):
    assert [cumulative_index(n) for n in (10, 14, 40)] == [6, 7, 15]     # the review's values
    for n in (4, 7, 12):
        check_identity(n, n + 3)
    rows = []
    for n in (20, 40, 60, 80, 100, 140, 180, 240, 300):
        d = cumulative_index(n)
        big_n = n * n - 1
        m = n * n * (n + 1) // 2
        rows.append({'n': n, 'cumulative_index': d, 'ratio_to_n': round(d / n, 4),
                     'hermite_estimate': round(big_n ** 2 / (8 * m + 4 * big_n), 2)})
    with open(out, 'w') as handle:
        json.dump(rows, handle, indent=1)
    print(len(rows), 'sizes written')


if __name__ == '__main__':
    main(sys.argv[1])
