#!/usr/bin/env python3
"""Plucker count for the far space F(n,k) of a single merge (cycle bmd-20261001-u, thm:cube-merge-far-count).

With the consecutive exponent sets of F(n,k) at w = 0, 1, infinity (stated in the theorem), the number of non-branch
Weierstrass points is binom(d,2) - (E_0 + E_1 + E_inf).  This script evaluates the sums symbolically (sympy), checks
the closed form (k-1)((3n-2)k + n^2 - 7n + 4)/2, and compares with the degrees computed modulo p in
research/results/bmd-20261001-t/merge-far.txt.
"""
import argparse
import re

import sympy as sp


def plucker():
    n, k, i = sp.symbols("n k i", integer=True)
    half = sp.Rational(1, 2)

    def s(a, b):
        return sp.summation(i, (i, a, b))

    C = n * (n - 1) / 2
    P = (k - 1) * (k - 2) / 2
    d = C + P + k * n + k + 1
    L = C + P + 2
    M = (k - 1) * n
    e0 = s(-C, P + k) + sp.summation(-(n - 1) + half + i, (i, 0, k * n - 1))
    e1 = s(0, L + M - 1) + sp.summation(half + i, (i, 0, n + k - 2))
    einf = s(-(1 + P), C + n) + sp.summation(-(k - 2) * n - half + i, (i, 0, M + k - 2))
    cnt = sp.expand(d * (d - 1) / 2 - (e0 + e1 + einf))
    closed = (k - 1) * ((3 * n - 2) * k + n ** 2 - 7 * n + 4) / 2
    return n, k, cnt, sp.simplify(cnt - closed) == 0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--far", required=True)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    n, k, cnt, ok = plucker()
    lines = [f"Plucker count: {sp.factor(cnt)}; equals the closed form: {ok}"]
    bad = 0
    for line in open(a.far):
        m = re.match(r"\s*\(n,k\)=\[(\d+), (\d+)\]: \[(\d+), 1, 1, (\d+), (\d+),", line)
        if m:
            nn, kk, deg = int(m.group(1)), int(m.group(2)), int(m.group(4))
            val = cnt.subs({n: nn, k: kk})
            ok2 = val == deg and int(m.group(5)) == 0
            bad += not ok2
            lines.append(f"(n,k)=({nn},{kk}): count {val}, degree mod p {deg}, squarefree mod p: {m.group(5) == '0'}: {'ok' if ok2 else 'MISMATCH'}")
    lines.append(f"mismatches: {bad}")
    open(a.out, "w").write("\n".join(lines) + "\n")
    print("\n".join(lines[:1] + lines[-1:]))


if __name__ == "__main__":
    main()
