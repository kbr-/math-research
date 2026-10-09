#!/usr/bin/env python3
"""First-moment thinness threshold for random k-CNF.

For m = Delta*v uniformly random k-clauses on v variables, the expected number of
(c v)-sets containing no clause scope is 2^{v (H(c) - Delta log2(e) c^k + o(1))}.
The central binomial binom(2cv, cv) is 2^{2cv - o(v)}.  The threshold c* is the
least c on a grid of step 0.0005 with H(c) - Delta log2(e) c^k <= 2c.  This is a
numerical evaluation of a closed formula, not an experiment.
"""
from math import e, log2


def H(c):
    return -c * log2(c) - (1 - c) * log2(1 - c)


def cstar(k, delta):
    c = 0.001
    while c < 0.5 and H(c) - delta * log2(e) * c ** k - 2 * c > 0:
        c += 0.0005
    return round(c, 4)


if __name__ == "__main__":
    for k, delta in [(3, 4.27), (3, 10), (3, 50), (4, 9.93), (4, 50), (5, 21.1), (7, 87.8), (10, 708)]:
        print(k, delta, cstar(k, delta))
