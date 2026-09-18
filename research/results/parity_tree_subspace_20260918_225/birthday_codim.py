#!/usr/bin/env python3
"""Least m at which the birthday subspace (distinct ceil(log2 m)-bit prefixes on m rows) boosts
S_1 (labelings of n rows with image size n-1) by beta_2 = (n+1)(3n-2)/(12n); exact formula
boost = (1 - C(m,2)/C(n,2)) * n^m (n-m)!/n!, evaluated in logarithms."""
from math import comb, log, exp, ceil, log2
for n in (8, 64, 2**10, 2**14, 2**20):
    beta = (n + 1) * (3 * n - 2) / (12 * n)
    m, lb = 2, -log(1 - 1 / n)
    while log(1 - comb(m, 2) / comb(n, 2)) + lb < log(beta):
        lb -= log(1 - m / n); m += 1
    print(f"n={n} beta_2={beta:.4f} m={m} codim={m * ceil(log2(m))} n/2+1={n // 2 + 1}")
