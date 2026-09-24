"""Compare the recursive lower bound B(n,c) for delta(n,c,0) with Phi(n,c,0).

B combines two proved mechanisms (entry-2026-09-25-hyperplane-dichotomy):
  step:       delta(n,c,0) >= delta(n-1,c,0) + 1                      (n >= 2)
  dichotomy:  delta(n,c,0) >= min(2c, 2^n - 1 + delta(n, c - 2^(n-1), 0))
with delta(n,c,0) = 0 for c <= 0 (constant 1) and delta(1,c,0) = c.
Phi(n,c,0) = n + sum_{j<n} floor((c-1)/2^j).  Prints the (n,c) where B < Phi.
Usage: bmd_dichotomy_bound.py NMAX CMAX
"""
import functools, sys


@functools.lru_cache(maxsize=None)
def B(n, c):
    if c <= 0:
        return 0
    if n == 1:
        return c
    rest = B(n, c - 2 ** (n - 1)) if c > 2 ** (n - 1) else 0
    return max(B(n - 1, c) + 1, min(2 * c, 2 ** n - 1 + rest))


def phi(n, c):
    return n + sum((c - 1) >> j for j in range(n))


nmax, cmax = int(sys.argv[1]), int(sys.argv[2])
sys.setrecursionlimit(100000)
gaps = [(n, c, B(n, c), phi(n, c)) for n in range(1, nmax + 1) for c in range(1, cmax + 1) if B(n, c) != phi(n, c)]
over = [g for g in gaps if g[2] > g[3]]
print(f'pairs {nmax * cmax}; B != Phi at {len(gaps)}; B > Phi (would refute) at {len(over)}')
print('first gaps (n, c, B, Phi):', gaps[:40])
