#!/usr/bin/env python3
"""Series index at the parameters of the cyclotomic orbit covers (side notebook near-half-pc-degree,
entry-2026-10-09-even-cover-indicator).

Statement tested: for n with n+1 prime and 2 a primitive root mod n+1, w = floor(log2(n+1)), the index D* of the
first non-positive coefficient of (1+z)^n / (1+z^w)^M (the semi-regular prediction for M rows of width w)
satisfies D*/n well below 1/2 for M = n(n+1) (one orbit) and M = 2n * n(n+1) (the proved covers), in
contrast with M = 2^w (covering sum one).  A property of power series only; it measures no polynomial system.
Also printed: static_span_bound, the least D with M * C(n-w, <=D-w) >= C(n, <=D); for D below it the span of
the multiples of M subspace rows of codimension w within degree D is proper (None: proper at every degree).
Reuses index() of research/results/near-half-fifth-review-20261009/series_index.py.  Usage: orbit_series.py N...
"""
import importlib.util
import json
import math
import sys

spec = importlib.util.spec_from_file_location(
    'series_index', 'research/results/near-half-fifth-review-20261009/series_index.py')
series_index = importlib.util.module_from_spec(spec)
spec.loader.exec_module(series_index)


def primitive(p):
    order, x = 1, 2 % p
    while x != 1:
        x, order = 2 * x % p, order + 1
    return order == p - 1


for arg in sys.argv[1:]:
    n = int(arg)
    p = n + 1
    assert all(p % q for q in range(2, int(p ** 0.5) + 1)) and primitive(p), n
    w = int(math.log2(p))
    for label, M in (('sum_one', 2 ** w), ('one_orbit', n * p), ('proved_cover', 2 * n * n * p)):
        D = series_index.index(n, {w: M})
        # least D at which M * dim(multiples of one subspace row within degree D) reaches dim(P_D):
        # below it the static span of the rows' multiples is proper by dimension
        total = lambda N, d: sum(math.comb(N, j) for j in range(max(d, -1) + 1))
        S = next((d for d in range(w, n + 1) if M * total(n - w, d - w) >= total(n, d)), None)
        print(json.dumps({'n': n, 'w': w, 'profile': label, 'M': M, 'cover_sum': M / 2 ** w,
                          'index': D, 'index_over_n': None if D is None else round(D / n, 4),
                          'static_span_bound': S}), flush=True)
