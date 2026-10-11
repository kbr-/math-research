"""The reach of the onto graph pigeonhole degree theorem against the product-series index, in one explicit class.

Class.  Bipartite graphs with n pigeons, each of degree d, and n - 1 holes, of which n - 1 - d have degree d and
d have degree d + 1 (so the edges number d n on both sides).  System over F_2: the graph onto pigeonhole formula
(pigeon clauses of width d, hole clauses of width two, onto clauses); a hole's onto clause with its hole clauses
is equivalent to the affine row "the hole's variables sum to one" with those hole clauses, so the free dimension
is N = d n - (n - 1), the rows of width two number M = (n - 1 - d) C(d,2) + d C(d+1,2), and there are n rows of
width d.  Product series: (1+z)^N (1 - u^2)^M (1 - u^d)^n, u = z/(1+z).

Statement tested.  The theorem read in its source gives degree > delta s/2 - xi when every set of at most s
pigeons has boundary at least delta |U'| - xi (and a matching).  For any such graph the least boundary of an
s-set is at most the average over s-sets, E(s) = sum_h r_h C(n - r_h, s - 1)/C(n, s), so the theorem's bound is
at most reach = max_s E(s)/2, whatever the graph of the class.  Question: is reach below the cumulative index
of the series (first degree with non-positive partial sum)?  Both outcomes are possible a priori: reach/n tends
to (1 - 1/d)^(d-1)/2 (0.222 at d = 3, 0.201 at d = 6), and the width-two heuristic for the index is
(d-1) n/(4d) (0.167 at d = 3, 0.208 at d = 6).  Exact integers and rationals.  One-off job of 11 October 2026.

Usage: python3 onto_index.py OUT.json
"""
import json
import sys
from fractions import Fraction
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


def first_nonpositive_partial_sum(coefficients):
    total = 0
    for degree, value in enumerate(coefficients):
        total += value
        if total <= 0:
            return degree
    return None


def case(d, n):
    length = n // 2 + 2
    holes = [(d, n - 1 - d), (d + 1, d)]
    assert sum(r * count for r, count in holes) == d * n and n - 1 - d > 0
    big_n = d * n - (n - 1)
    m = sum(comb(r, 2) * count for r, count in holes)
    k = 2 * m - big_n                                   # (1+z)^N (1-u^2)^M = (1+z)^(-k) (1+2z)^M, k > 0
    assert k > 0
    inverse = [(-1) ** e * comb(k + e - 1, e) for e in range(length)]
    two = [comb(m, e) * 2 ** e for e in range(length)]
    width_two = mul(inverse, two, length)
    assert width_two[1] == big_n and width_two[2] == comb(big_n, 2) - m
    # (1 - u^d)^n = ((1+z)^d - z^d)^n (1+z)^(-d n)
    bracket = [comb(d, e) for e in range(d)] + [0] * max(0, length - d)
    pigeon = mul(power(bracket[:length], n, length),
                 [(-1) ** e * comb(d * n + e - 1, e) for e in range(length)], length)
    assert pigeon[0] == 1 and all(v == 0 for v in pigeon[1:d]) and pigeon[d] == -n
    full = mul(width_two, pigeon, length)
    # Second convention (the reviewer's): a hole's affine row and hole clauses cut its variables to the r points
    # of weight one, graded 1 + (r-1) z in the r-1 free variables; of the C(r,2) hole clauses the r-1 through the
    # eliminated variable are sums of the others, so the all-rows count above includes redundant rows.
    exact_holes = [1] + [0] * (length - 1)
    for r, count in holes:
        exact_holes = mul(exact_holes, power(([1, r - 1] + [0] * length)[:length], count, length), length)
    exact = mul(exact_holes, pigeon, length)
    reach, at = max((sum(Fraction(r * comb(n - r, s - 1) * count, comb(n, s)) for r, count in holes) / 2, s)
                    for s in range(1, n + 1))
    index = first_nonpositive_partial_sum(full)
    return {'d': d, 'n': n, 'free_dimension': big_n, 'width_two_rows': m,
            'index_width_two_rows_only': first_nonpositive_partial_sum(width_two),
            'index_full_series': index,
            'index_exact_hole_factor': first_nonpositive_partial_sum(exact), 'reach': float(reach), 'reach_at_s': at,
            'guaranteed_degree_at_most': int(reach) + 1,
            'index_over_n': round(index / n, 4) if index is not None else None,
            'reach_over_n': round(float(reach) / n, 4), 'truncated_at': length - 1}


def main(out):
    cases = [(d, n) for d in (3, 4, 6, 8) for n in (60, 120, 240, 480)]
    rows = [case(d, n) for d, n in cases]
    with open(out, 'w') as handle:
        json.dump(rows, handle, indent=1)
    print(len(rows), 'cases written')


if __name__ == '__main__':
    main(sys.argv[1])
