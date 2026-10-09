#!/usr/bin/env python3
"""Index of regularity of (1+t)^n/(1+t^k)^m for m = ln(2)*2^k*n (parity k-clause threshold density).

Evaluation of a closed formula (the semi-regular prediction), not an experiment.
Prints n, k, m, the index d and d/n.
"""
from math import comb, log, ceil


def series_index(n, m, k, maxd):
    inv = [0] * (maxd + 1)
    for j in range(0, maxd // k + 1):
        inv[k * j] = (-1) ** j * comb(m + j - 1, j)
    for d in range(maxd + 1):
        if sum(comb(n, d - e) * inv[e] for e in range(d + 1)) <= 0:
            return d
    return None


if __name__ == "__main__":
    for k in (2, 3, 4, 6):
        for n in (100, 400, 1600):
            m = ceil(log(2) * 2 ** k * n)
            d = series_index(n, m, k, n // 2 + 5)
            print(n, k, m, d, None if d is None else round(d / n, 4))
