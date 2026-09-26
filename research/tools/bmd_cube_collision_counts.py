"""Arithmetic identities behind the exact collision exponents (bmd-r103).

For the cube {0,1}^n, the boundary system has basis T^Q w^r with 2Q+|r| <= d,
N = N_{2,n}(d) elements, and every entry (Q,r;c) of the constraint matrix is
homogeneous of degree c - Q in y. So deg Delta_{n,d} = sum_{c<N} c - sum Q.
The collision exponent is E_n(d) = sum over P = T^Q z^r' in V_{n-1,d-1} of
(d - 2Q - |r'|).  This script checks, from these definitions:
  E_n(d) = sum_k C(n-1,k) floor((d-k+1)^2/4) over 0 <= k <= min(n-1,d),
  E_4(d) = d^2 + (d-1)^2, deg Delta_{4,d} = 30d^2 - 30d + 5 (d >= 2),
  deg Delta_{4,d} - 10 E_4(d) = 10d^2 - 10d - 5 (d >= 2),
  E_3(d) = d^2 and deg Delta_{3,d} - 6 E_3(d) = d^2 - 1,
and records deg Delta_{n,d} - C(n+1,2) E_n(d) for small n, d.
"""
import argparse
import itertools
import json
from math import comb


def basis(n, d):
    return [(Q, r) for r in itertools.product((0, 1), repeat=n)
            for Q in range(d + 1) if 2 * Q + sum(r) <= d]


def E(n, d):
    return sum(d - 2 * Q - sum(r) for Q, r in basis(n - 1, d - 1))


def deg_delta(n, d):
    B = basis(n, d)
    N = len(B)
    return N * (N - 1) // 2 - sum(Q for Q, _ in B)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--out', required=True)
    ap.add_argument('--dmax', type=int, default=40)
    a = ap.parse_args()
    for n in range(2, 8):
        for d in range(1, a.dmax + 1):
            f = sum(comb(n - 1, k) * ((d - k + 1) ** 2 // 4)
                    for k in range(0, min(n - 1, d) + 1))
            assert E(n, d) == f, (n, d)
    for d in range(1, a.dmax + 1):
        assert E(3, d) == d * d and deg_delta(3, d) - 6 * E(3, d) == d * d - 1
        assert E(4, d) == d * d + (d - 1) ** 2
        if d >= 2:
            assert len(basis(4, d)) == 8 * d - 4
            assert deg_delta(4, d) == 30 * d * d - 30 * d + 5
            assert deg_delta(4, d) - 10 * E(4, d) == 10 * d * d - 10 * d - 5
    table = {n: [deg_delta(n, d) - comb(n + 1, 2) * E(n, d) for d in range(1, 11)]
             for n in range(3, 7)}
    res = {'dmax': a.dmax, 'identities': 'all asserted',
           'deg_Delta_minus_collision_part_d1_to_10': table}
    with open(a.out, 'w') as fh:
        json.dump(res, fh, indent=1)
    print(json.dumps(res))


if __name__ == '__main__':
    main()
