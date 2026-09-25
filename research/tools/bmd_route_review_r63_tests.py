#!/usr/bin/env python3
"""Cheap test of the cohomology-and-base-change lead (route review bmd-r63).

Statement tested: the solutions at m are the dual of Q = coker(tau_m: V -> R^{m+1}) over R = F[[s,t]] at a double
point P. If Q were free of rank rho at P, some local solution would not vanish at P. Its fibre dimension is
dim Q (x) k(P) = m + 1 - rank A_m(P), and the jump h(P) = m + 1 - rank A_m(P) - rho must be >= 1 whenever every
solution vanishes at P (window lemma: rho <= d - 1). Exact rational ranks of the truncations of the specialized
basis T^Q z^r (2Q + |r| <= d) at y = (1, 1, 0), for d <= 6 and every rho = 1..d.
"""
import argparse
import itertools
import json
from fractions import Fraction
from math import comb


def cat(j):
    return comb(2 * j, j) // (j + 1)


def rank(rows):
    m = [r[:] for r in rows]
    rk, col, ncol = 0, 0, len(m[0])
    while rk < len(m) and col < ncol:
        piv = next((i for i in range(rk, len(m)) if m[i][col] != 0), None)
        if piv is None:
            col += 1
            continue
        m[rk], m[piv] = m[piv], m[rk]
        for i in range(len(m)):
            if i != rk and m[i][col] != 0:
                f = m[i][col] / m[rk][col]
                m[i] = [a - f * b for a, b in zip(m[i], m[rk])]
        rk += 1
        col += 1
    return rk


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--out', required=True)
    a = ap.parse_args()
    out = []
    for d in range(2, 7):
        for rho in range(1, d + 1):
            m = 4 * d + rho - 1
            prec = m + 1
            z = [Fraction(0)] + [Fraction((-1) ** j * cat(j - 1)) for j in range(1, prec)]  # r0(T) at y = 1

            def mul(x, y):
                o = [Fraction(0)] * prec
                for i, xi in enumerate(x):
                    if xi:
                        for j in range(prec - i):
                            o[i + j] += xi * y[j]
                return o
            rows = []
            for r in itertools.product((0, 1), repeat=3):
                for Q in range(d + 1):
                    if 2 * Q + sum(r) > d or r[2]:  # z_3 = r0(0 * T) = 0
                        continue
                    f = [Fraction(0)] * prec
                    f[Q] = Fraction(1)
                    for i in range(2):
                        if r[i]:
                            f = mul(f, z)
                    rows.append(f)
            rk = rank(rows)
            out.append({'d': d, 'rho': rho, 'm': m, 'rank_at_P': rk, 'jump': m + 1 - rk - rho})
            print(out[-1], flush=True)
    with open(a.out, 'w') as fh:
        json.dump(out, fh, indent=1)


if __name__ == '__main__':
    main()
