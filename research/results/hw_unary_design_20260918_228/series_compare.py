#!/usr/bin/env python3
"""First nonpositive coefficient of (1+t)^k (1+t^l)^(-m) against (1+t)^k (1 - t^l/(1+t)^l)^m.

Sixteen holes: l = 4, m = C(17,2) = 136 collision flats; k = 20, 40. Output: k, degree for the
generic-polynomial yardstick of cycle 223, degree for the clause series of cycle 228."""
from fractions import Fraction
from math import comb
def mul(a, b, D):
    c = [0] * (D + 1)
    for i, x in enumerate(a):
        if x == 0: continue
        for j, y in enumerate(b):
            if i + j <= D: c[i + j] += x * y
    return c
def inv(a, D):
    b = [0] * (D + 1); b[0] = Fraction(1, a[0])
    for n in range(1, D + 1):
        b[n] = -sum(a[i] * b[n - i] for i in range(1, min(n, len(a) - 1) + 1)) / a[0]
    return b
def power(a, m, D):
    r = [1] + [0] * D
    for _ in range(m): r = mul(r, a, D)
    return r
D, l, m = 20, 4, 136
first = lambda s: next((i for i, x in enumerate(s) if x <= 0), None)
for k in (20, 40):
    base = [comb(k, i) for i in range(D + 1)]
    s1 = mul(base, power(inv([1] + [0] * (l - 1) + [1], D), m, D), D)
    u = mul([0] * l + [1], inv(power([1, 1], l, D), D), D)
    s2 = mul(base, power([(1 if i == 0 else 0) - u[i] for i in range(D + 1)], m, D), D)
    print(k, first(s1), first(s2))
