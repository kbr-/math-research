#!/usr/bin/env python3
"""Thresholds for the level count of a relaxation by groups.

Statement evaluated: for N groups of g variables with at most one variable of a group set, the number of
squarefree monomials of degree j with at most one variable per group is C(N, j) g^j.  The thin window of
thm:thin-kernel-source-exclusion asks C(N, j) g^j <= C(X, j) for K - Delta < j <= K with
X = 2(K - Delta) + 1 + (K - Delta + 1)/Delta (taken as its integer part here, which only strengthens the
test).  The script (1) solves alpha H(1/alpha) = 2 - log2 g for the leading-order threshold N = alpha K,
g = 1, 2, 3, and (2) for given (g, K, Delta) finds by exact integer arithmetic the largest N for which the
window inequality holds at every j, and checks N >= K.
"""
import argparse
import math


def entropy(p):
    return 0.0 if p in (0.0, 1.0) else -p * math.log2(p) - (1 - p) * math.log2(1 - p)


def alpha(g):
    target = 2 - math.log2(g)
    lo, hi = 1.0, 2.0
    for _ in range(80):
        mid = (lo + hi) / 2
        if mid * entropy(1 / mid) < target:
            lo = mid
        else:
            hi = mid
    return lo


def largest_n(g, k, delta):
    x = 2 * (k - delta) + 1 + (k - delta + 1) // delta
    right = {j: math.comb(x, j) for j in range(k - delta + 1, k + 1)}

    def holds(n):
        return all(math.comb(n, j) * g ** j <= right[j] for j in right)

    if not holds(k):
        return x, None
    lo, hi = k, x + 1          # the inequality is monotone in n and fails at n = x + 1 for g >= 1
    while hi - lo > 1:
        mid = (lo + hi) // 2
        if holds(mid):
            lo = mid
        else:
            hi = mid
    return x, lo


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    args = ap.parse_args()
    with open(args.out, "w") as fh:
        for g in (1, 2, 3):
            a = alpha(g)
            fh.write(f"g={g} alpha={a:.4f} K/N={1 / a:.4f} K/v={1 / (a * g):.4f}\n")
        for g, k, delta in ((1, 1000, 10), (2, 1000, 10), (3, 1000, 10), (4, 1000, 10), (2, 4000, 12),
                            (3, 4000, 12), (4, 4000, 12)):
            x, best = largest_n(g, k, delta)
            fh.write(f"g={g} K={k} Delta={delta} X={x} largest_N={best}"
                     + ("" if best is None else f" N/K={best / k:.4f}") + "\n")
    print("done")


if __name__ == "__main__":
    main()
