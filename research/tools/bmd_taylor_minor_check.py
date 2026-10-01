"""Taylor minor of a 4-point configuration (7 October 2026; cycle bmd-20261007-i).

Tested statement: the cluster D = {0, 2, -3, 5} used in the M = 4 cherry-join Newton polygon run has vanishing
Taylor minor (columns 0..5 of its pair matrix, lambda = 3/2), which explains the x-exponent 28 instead of the
predicted 27 there; the control D = {0, 2, -3, 7} has a nonzero Taylor minor.  Exact rational arithmetic.
"""
from fractions import Fraction as F
from itertools import combinations


def beta(k):
    r = F(1)
    for i in range(k):
        r *= F(-3, 2) - i
        r /= i + 1
    return r


def pair_coeff(x, y, k):
    return sum(beta(n) * beta(k - n) * F(x) ** n * F(y) ** (k - n) for n in range(k + 1))


def det(m):
    m = [r[:] for r in m]
    n, d = len(m), F(1)
    for c in range(n):
        p = next((r for r in range(c, n) if m[r][c] != 0), None)
        if p is None:
            return F(0)
        if p != c:
            m[c], m[p] = m[p], m[c]
            d = -d
        d *= m[c][c]
        for r in range(c + 1, n):
            f = m[r][c] / m[c][c]
            for k in range(c, n):
                m[r][k] -= f * m[c][k]
    return d


for D in ([0, 2, -3, 5], [0, 2, -3, 7]):
    rows = [[pair_coeff(D[i], D[j], k) for k in range(6)] for i, j in combinations(range(4), 2)]
    print(D, "Taylor minor (columns 0..5):", det(rows))
