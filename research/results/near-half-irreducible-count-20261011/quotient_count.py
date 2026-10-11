"""The graded dimension of the pigeonhole principle's degree-d quotient against its product series.

Statement tested.  For PHP with m pigeons and n holes (pigeon sums as linear axioms, hole and functionality
products, multilinear ring) and d <= (n+1)/2, the irreducible terms of degree e are the partial injections on e
pigeons whose pigeon dance completes (source: the 1998 paper on polynomial calculus lower bounds, Section 3.2
and Claim 3.11).  Their number on a fixed set of e pigeons is claimed to be
    a_e = sum_j (-1)^(e-j) C(e,j) n(n-1)...(n-j+1) = e! [y^e] exp(-y) (1+y)^n,
since the irreducible terms on a set I of pigeons are a basis of the functions on the injections I -> [n].
Checks: (1) a_e against a brute-force count of dance-completing arrangements, under two readings of "free
hole" (a vacated hole is or is not free again), for n <= 7, e <= (n+1)/2; (2) for m = n+1, the graded count
H_e = C(n+1,e) a_e against the coefficients c_e of (1+z)^N (1 - (z/(1+z))^2)^M, N = n^2 - 1, M the number of
hole and functionality clauses.  Exact integers.  One-off job of 11 October 2026.

Usage: python3 quotient_count.py OUT.json
"""
import json
import sys
from itertools import permutations
from math import comb, factorial


def falling(n, j):
    out = 1
    for i in range(j):
        out *= n - i
    return out


def a_formula(n, e):
    return sum((-1) ** (e - j) * comb(e, j) * falling(n, j) for j in range(e + 1))


def dance_completes(holes, n, reuse):
    """Pigeons in order fly to the nearest free hole to the right; lazy play, which the source says is best."""
    occupied = set(holes)
    for j in holes:
        if reuse:
            occupied.discard(j)
        target = next((h for h in range(j + 1, n + 1) if h not in occupied), None)
        if target is None:
            return False
        occupied.add(target)
    return True


def a_dance(n, e, reuse):
    return sum(dance_completes(p, n, reuse) for p in permutations(range(1, n + 1), e))


def series(n, dmax):
    big_n = n * n - 1
    m = n * comb(n + 1, 2) + (n + 1) * comb(n, 2)
    k_exp = 2 * m - big_n
    return [sum(comb(m, j) * 2 ** j * (-1) ** (d - j) * comb(k_exp + d - j - 1, d - j) for j in range(d + 1))
            for d in range(dmax + 1)]


def main(out):
    dance = []
    for n in range(2, 8):
        for e in range(0, (n + 1) // 2 + 1):
            dance.append({'n': n, 'e': e, 'formula': a_formula(n, e),
                          'dance_vacated_reusable': a_dance(n, e, True),
                          'dance_vacated_blocked': a_dance(n, e, False)})
    compare = []
    for n in (10, 20, 40, 100):
        top = (n + 1) // 2
        c = series(n, top)
        h = [comb(n + 1, e) * a_formula(n, e) for e in range(top + 1)]
        assert all(x > 0 for x in h)
        graded = next((d for d in range(top + 1) if c[d] <= 0), None)
        total, cumulative = 0, None
        for d in range(top + 1):
            total += c[d]
            if total <= 0:
                cumulative = d
                break
        compare.append({'n': n, 'top_degree': top, 'series_graded_index': graded,
                        'series_cumulative_index': cumulative,
                        'h2_minus_c2': h[2] - c[2], 'free_dimension': n * n - 1,
                        'ratio_h_over_c_at_3_4_5': [round(h[e] / c[e], 4) if c[e] > 0 else None for e in (3, 4, 5)],
                        'log10_h_at_top': len(str(h[top])) - 1})
    with open(out, 'w') as handle:
        json.dump({'dance': dance, 'compare': compare}, handle, indent=1)
    print(len(dance), 'dance rows and', len(compare), 'comparisons written;', factorial(3) and 'ok')


if __name__ == '__main__':
    main(sys.argv[1])
