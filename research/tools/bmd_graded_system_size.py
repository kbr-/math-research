"""Size of the graded threshold systems of the dimension-four bounded kernel (5 October 2026; cycle bmd-20261005-z).

A kernel element of order <= m and leading excess l has entries in columns 0..m of weighted degree l + (m - c) in
e_1..e_4 (weights 1, 2, 3, 4); the number of unknowns is sum_{j <= m} M(l + j), M(k) the number of monomials of weighted
degree k.  Checked against the d = 2 order-14 excess-9 system (1070 unknowns, cycle bmd-20261005-y)."""
from functools import lru_cache


@lru_cache(None)
def monomials(k):
    return sum(1 for d in range(k // 4 + 1) for c in range((k - 4 * d) // 3 + 1) for b in range((k - 4 * d - 3 * c) // 2 + 1))


def unknowns(m, l):
    return sum(monomials(l + j) for j in range(m + 1))


if __name__ == '__main__':
    assert unknowns(14, 9) == 1070
    print('d=2 m=14 excess=9 unknowns=%d (control)' % unknowns(14, 9))
    for m, l in [(20, 55), (21, 50), (21, 46), (25, 40), (30, 30), (38, 10)]:
        print('d=3 m=%d excess=%d unknowns=%d dense_GB=%.1f' % (m, l, unknowns(m, l), unknowns(m, l) ** 2 * 8 / 1e9))
