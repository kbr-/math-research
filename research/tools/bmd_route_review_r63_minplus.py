#!/usr/bin/env python3
"""Route review bmd-r63: is the recorded order mu(d, rho) the rho-fold min-plus convolution of psi(p) = floor(p^2/2)?

mu_rec(d, rho) = sum floor(p_i^2/2) over the balanced partition of j+q into q = min(rho, j) parts, j = d - rho
(conj:cube-double-point-sharp-order). mu_min(d, rho) = min over partitions of d into exactly rho positive parts
of sum floor(p_i^2/2), by dynamic programming. The same comparison for B = sum (p_i^2 - 1).
"""
import json
import sys

INF = 10 ** 9
D = 60


def psi(p):
    return p * p // 2


def beta(p):
    return p * p - 1


def conv(f):
    """g[r][d] = min over partitions of d into exactly r positive parts of sum f(p_i)."""
    g = [[INF] * (D + 1) for _ in range(D + 1)]
    g[0][0] = 0
    for r in range(1, D + 1):
        for d in range(r, D + 1):
            g[r][d] = min(g[r - 1][d - p] + f(p) for p in range(1, d - r + 2))
    return g


def balanced(d, rho):
    j = d - rho
    if j == 0:
        return []
    q = min(rho, j)
    n = j + q
    return [n // q + (1 if i < n % q else 0) for i in range(q)]


def main():
    gm, gb = conv(psi), conv(beta)
    bad = []
    for d in range(1, D + 1):
        for rho in range(1, d + 1):
            parts = balanced(d, rho)
            if sum(psi(p) for p in parts) != gm[rho][d] or sum(beta(p) for p in parts) != gb[rho][d]:
                bad.append((d, rho))
    res = {'range': '1 <= rho <= d <= %d' % D, 'mismatches': bad[:20], 'count': len(bad)}
    with open(sys.argv[1], 'w') as fh:
        json.dump(res, fh, indent=1)
    print(res)


if __name__ == '__main__':
    main()
