#!/usr/bin/env python3
"""Cheap tests of the leads and bridges of the route review bmd-r58 (all exact, all small).

1. Riemann-Roch lead. For n >= 3, the fibre curve w_i^2 = 1 + 4 y_i T (distinct nonzero y_i) has genus
   g_n = 1 + 2^(n-2) (n-3), and V_{n,d} (basis T^Q z^r, 2Q + |r| <= d) lies in L(d H_inf) with
   deg H_inf = 2^(n-1). Test: N_{2,n}(d) = dim V_{n,d} against the Riemann-Roch value 2^(n-1) d + 1 - g_n,
   which it must equal whenever V_{n,d} is the complete space and 2^(n-1) d > 2 g_n - 2.
2. Chebyshev-Pell bridge. Delta_{3,d}(y) = 0 iff d c = 0 on v^2 = x(x-y1)(x-y2)(x-y3) (torsion criterion);
   by Abel-Chebyshev this is a Pell solution P^2 - D Q^2 = 1 with deg P = d. For d = 2 that locus is
   y_i = y_j + y_k; for d = 3 it is sqrt(y1) +- sqrt(y2) +- sqrt(y3) = 0 and its translates. Test: the
   4d x 4d coefficient matrix [T^c] T^Q z^r (c < 4d) is singular at points of these loci and regular at
   nearby control points.
3. List-decoding bridge. The Guruswami-Sudan parameter count: a nonzero trivariate polynomial of degree D
   with multiplicity >= k at the 7 nonzero points of {0,1}^3 exists once C(D+3,3) > 7 C(k+2,3). Compare
   the least such D with the proved value min_l delta(3,k,l) <= 2k - floor(k/5) and the lower bound
   2k - floor(k/4).
"""
import argparse
import itertools
import json
from fractions import Fraction
from math import comb


def n_count(n, d):
    return sum(1 for r in itertools.product((0, 1), repeat=n) for Q in range(d + 1) if 2 * Q + sum(r) <= d)


def rr_value(n, d):
    g = 1 + 2 ** (n - 2) * (n - 3)
    return 2 ** (n - 1) * d + 1 - g, g


def catalan(j):
    return comb(2 * j, j) // (j + 1)


def z_series(y, prec):
    """z = r0(yT) = sum_{j>=1} (-1)^j C_{j-1} y^j T^j, truncated below T^prec."""
    return [Fraction(0)] + [Fraction((-1) ** j * catalan(j - 1)) * Fraction(y) ** j for j in range(1, prec)]


def mul(a, b, prec):
    out = [Fraction(0)] * prec
    for i, ai in enumerate(a):
        if ai:
            for j in range(prec - i):
                out[i + j] += ai * b[j]
    return out


def boundary_rank(y, d):
    prec = 4 * d
    zs = [z_series(v, prec) for v in y]
    rows = []
    for r in itertools.product((0, 1), repeat=3):
        for Q in range(d + 1):
            if 2 * Q + sum(r) > d:
                continue
            f = [Fraction(0)] * prec
            if Q < prec:
                f[Q] = Fraction(1)
            for i in range(3):
                if r[i]:
                    f = mul(f, zs[i], prec)
            rows.append(f)
    assert len(rows) == 4 * d
    # exact rank by fraction Gaussian elimination (4d <= 16)
    m = [row[:] for row in rows]
    rank, col = 0, 0
    while rank < len(m) and col < prec:
        piv = next((i for i in range(rank, len(m)) if m[i][col] != 0), None)
        if piv is None:
            col += 1
            continue
        m[rank], m[piv] = m[piv], m[rank]
        for i in range(len(m)):
            if i != rank and m[i][col] != 0:
                fac = m[i][col] / m[rank][col]
                m[i] = [a - fac * b for a, b in zip(m[i], m[rank])]
        rank += 1
        col += 1
    return rank


def gs_degree(k):
    D = 0
    while comb(D + 3, 3) <= 7 * comb(k + 2, 3):
        D += 1
    return D


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--out', required=True)
    args = ap.parse_args()
    res = {'riemann_roch': [], 'pell': [], 'guruswami_sudan': []}
    for n in range(3, 7):
        for d in range(1, 41):
            N = n_count(n, d)
            rr, g = rr_value(n, d)
            res['riemann_roch'].append({'n': n, 'd': d, 'N': N, 'rr': rr, 'genus': g,
                                        'above_2g_minus_2': 2 ** (n - 1) * d > 2 * g - 2})
    cases = [  # (d, y, on_locus)
        (2, (1, 2, 3), True), (2, (2, 7, 5), True), (2, (1, 2, 4), False), (2, (2, 7, 6), False),
        (3, (1, 4, 9), True), (3, (4, 9, 25), True), (3, (1, 9, 4), True), (3, (1, 4, 10), False),
        (3, (4, 9, 26), False),
        # translate of the d = 3 locus: the root y1 paired with the double root, i.e. the roots
        # -y1, y2-y1, y3-y1 satisfy e1^2 = 4 e2 after x -> x + y1; (y1,y2,y3) = (-1, 3, 8) gives 1, 4, 9.
        (3, (-1, 3, 8), True), (3, (-1, 3, 9), False),
    ]
    for d, y, on in cases:
        rank = boundary_rank(y, d)
        res['pell'].append({'d': d, 'y': y, 'predicted_on_locus': on, 'rank': rank, 'size': 4 * d,
                            'singular': rank < 4 * d, 'agrees': (rank < 4 * d) == on})
    for k in range(2, 201):
        res['guruswami_sudan'].append({'k': k, 'count_degree': gs_degree(k), 'upper_value': 2 * k - k // 5,
                                       'dkss_lower': 2 * k - k // 4})
    rrs = res['riemann_roch']
    summary = {
        'rr_equal_whenever_above': all(r['N'] == r['rr'] for r in rrs if r['above_2g_minus_2']),
        'rr_mismatches_above': [(r['n'], r['d'], r['N'], r['rr']) for r in rrs
                                if r['above_2g_minus_2'] and r['N'] != r['rr']][:20],
        'rr_first_equal_d': {n: min((r['d'] for r in rrs if r['n'] == n and r['N'] == r['rr']), default=None)
                             for n in range(3, 7)},
        'pell_all_agree': all(p['agrees'] for p in res['pell']),
        'gs_below_upper': [g['k'] for g in res['guruswami_sudan'] if g['count_degree'] < g['upper_value']],
        'gs_ratio_k200': res['guruswami_sudan'][-1]['count_degree'] / 200,
    }
    res['summary'] = summary
    with open(args.out, 'w') as fh:
        json.dump(res, fh, indent=1)
    print(json.dumps(summary, indent=1), flush=True)


if __name__ == '__main__':
    main()
