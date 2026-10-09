#!/usr/bin/env python3
"""Typical extension cutoff for random k-CNF (evaluation of a closed formula).

For m = Delta*v uniformly random k-clauses and a fixed set S of c*v variables, a
variable x outside S cannot extend S to a scope-free set if some clause scope has
its other k-1 variables in S.  The expected number of clauses with exactly k-1
variables in S is Delta*v*k*c^(k-1)*(1-c), so a given outside variable is in none
of them with probability about exp(-Delta*k*c^(k-1)).  The expected number of
unblocked outside variables is (1-c)*v*exp(-Delta*k*c^(k-1)).  The cutoff c_ext is
the least grid point (step 0.0005) with (1-c)*exp(-Delta*k*c^(k-1)) <= c.

This concerns a FIXED set S, not the worst scope-free set and not the standard
monomials of any closure; it is a calibration, not a bound on extension counts.
The second column repeats the first-moment thinness threshold c* and the third the
first-moment scope-free ceiling alpha (least c with H(c) <= Delta*log2(e)*c^k).
"""
from math import e, exp, log2


def H(c):
    return -c * log2(c) - (1 - c) * log2(1 - c)


def first(pred):
    c = 0.001
    while c < 0.9995 and not pred(c):
        c += 0.0005
    return round(c, 4)


if __name__ == "__main__":
    print("k Delta c_ext c_star alpha")
    for k, d in [(3, 4.27), (3, 10), (4, 9.93), (5, 21.1), (7, 87.8), (10, 708)]:
        c_ext = first(lambda c: (1 - c) * exp(-d * k * c ** (k - 1)) <= c)
        c_star = first(lambda c: H(c) - d * log2(e) * c ** k - 2 * c <= 0)
        alpha = first(lambda c: c > 0.05 and H(c) - d * log2(e) * c ** k <= 0)
        print(k, d, c_ext, c_star, alpha)
