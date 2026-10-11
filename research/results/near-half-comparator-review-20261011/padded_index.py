"""The product-series index of a clause system before and after padding with implied rows.

Statement tested (the reviewer's, at the blind stage of the review of 11 October 2026): the cumulative index of
the product series (1+z)^N prod_rows (1 - u^w), u = z/(1+z), depends on the presentation and not on the ideal.
Take M clauses of width k on N variables.  Each clause times one further literal is an implied row of width
k + 1, a multiple of an axiom; there are 2 (N - k) of them per clause.  Adding them changes neither the ideal
nor the degree-D closure for D >= k + 1, so the refutation degree is the same.  The check computes the index
of the series with the M rows and with the M + 2 M (N - k) rows.  If the index were a function of the system
the two would agree; the heuristic c_e ~ C(N,e) - M' C(N,e-k-1) predicts the padded index near
N / (2 M N)^(1/(k+1)), far below the unpadded one.  Exact integers.  One-off job.

Usage: python3 padded_index.py OUT.json
"""
import json
import sys
from math import comb


def mul(a, b, length):
    out = [0] * length
    for i, x in enumerate(a[:length]):
        if x:
            for j, y in enumerate(b[:length - i]):
                out[i + j] += x * y
    return out


def power(base, exponent, length):
    result = [1] + [0] * (length - 1)
    while exponent:
        if exponent & 1:
            result = mul(result, base, length)
        base = mul(base, base, length)
        exponent >>= 1
    return result


def row_factor(width, count, length):
    """(1 - u^width)^count = ((1+z)^width - z^width)^count (1+z)^(-width count), truncated."""
    bracket = ([comb(width, e) for e in range(width)] + [0] * length)[:length]
    inverse = [(-1) ** e * comb(width * count + e - 1, e) for e in range(length)]
    return mul(power(bracket, count, length), inverse, length)


def index(coefficients):
    total = 0
    for degree, value in enumerate(coefficients):
        total += value
        if total <= 0:
            return degree
    return None


def case(n, k, density):
    length = n // 2 + 2
    m = density * n
    padding = 2 * m * (n - k)
    cube = [comb(n, e) for e in range(length)]
    plain = mul(cube, row_factor(k, m, length), length)
    assert plain[k] == comb(n, k) - m
    padded = mul(plain, row_factor(k + 1, padding, length), length)
    assert padded[k + 1] == plain[k + 1] - padding
    return {'variables': n, 'width': k, 'clauses': m, 'implied_rows_added': padding,
            'index': index(plain), 'index_padded': index(padded),
            'heuristic_padded': round(n / (padding ** (1 / (k + 1))), 1), 'truncated_at': length - 1}


def main(out):
    cases = [(100, 3, 5), (200, 3, 5), (400, 3, 5), (200, 4, 10), (400, 4, 10)]
    rows = [case(*c) for c in cases]
    with open(out, 'w') as handle:
        json.dump(rows, handle, indent=1)
    print(len(rows), 'cases written')


if __name__ == '__main__':
    main(sys.argv[1])
