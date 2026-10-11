"""Graded and cumulative index of the product series (1+z)^N prod_w (1 - (z/(1+z))^w)^(M_w) for the rows of
PHP^{n+1}_n read as a cover of F_2^N: n+1 pigeon clauses of width n and n*C(n+1,2) hole clauses of width 2,
N = n(n+1).  Statement tested: the recorded degree lower bound, of order n/2, exceeds the cumulative index (the
first degree at which the partial sum of coefficients is not positive).  Exact rational arithmetic; one-off job
of 11 October 2026 for the review's Power paragraph.

Usage: python3 php_index.py OUT.json
"""
import json
import sys
from fractions import Fraction
from math import comb


def gbinom(a, k):
    """Generalized binomial C(a, k) for an integer a of either sign and k >= 0."""
    num = 1
    for i in range(k):
        num *= a - i
    den = 1
    for i in range(2, k + 1):
        den *= i
    return Fraction(num, den)


def indices(n, dmax, affine=False):
    """affine=True: the pigeon conditions as affine equations over F_2 (sum of a pigeon's variables is one),
    which lower the free dimension by n+1 and contribute no row; the hole clauses stay rows of width two."""
    big_n = n * (n + 1) - (n + 1 if affine else 0)
    holes = n * comb(n + 1, 2)
    pigeons = 0 if affine else n + 1
    a = [0] * (dmax + 1)                       # (1 - u^2)^holes, u = z/(1+z)
    for i in range(dmax // 2 + 1):
        a[2 * i] = (-1) ** i * comb(holes, i)
    c = [0] * (dmax + 1)                       # times (1 - u^n)^pigeons
    for t in range(dmax // n + 1):
        co = (-1) ** t * comb(pigeons, t)
        for j in range(dmax + 1 - t * n):
            c[j + t * n] += co * a[j]
    h = [sum(c[j] * gbinom(big_n - j, d - j) for j in range(d + 1)) for d in range(dmax + 1)]
    graded = next((d for d in range(dmax + 1) if h[d] <= 0), None)
    total, cumulative = 0, None
    for d in range(dmax + 1):
        total += h[d]
        if total <= 0:
            cumulative = d
            break
    return big_n, graded, cumulative, [str(x) for x in h[:6]]


def main(out):
    assert indices(2, 4)[0] == 6
    rows = []
    for n in range(4, 41, 2):
        big_n, graded, cumulative, head = indices(n, n + 2)
        free, graded_affine, cumulative_affine, _ = indices(n, n + 2, affine=True)
        rows.append({'n': n, 'variables': big_n, 'graded_index': graded, 'cumulative_index': cumulative,
                     'free_dimension_affine': free, 'graded_index_affine': graded_affine,
                     'cumulative_index_affine': cumulative_affine,
                     'half_holes_plus_one': n // 2 + 1, 'first_coefficients': head})
    with open(out, 'w') as handle:
        json.dump(rows, handle, indent=1)
    print(len(rows), 'sizes written')


if __name__ == '__main__':
    main(sys.argv[1])
