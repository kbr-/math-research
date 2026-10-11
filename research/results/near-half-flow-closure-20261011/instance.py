#!/usr/bin/env python3
"""One explicit instance for the flow-system proposition: the complete bipartite graph K_{t,t}.

Statement evaluated: for the flow system modulo three on two-bit blocks over a connected graph with n_v
vertices, m edges, row width w = 2 r bits and edge expansion h, the closure is proper for w <= D < h n_v / 8,
and for a subgraph H of maximum degree below h/2 with M edges it has at least 2^j C(M, j) standard monomials
of each degree j <= D - 1.  The thin window of thm:thin-kernel-source-exclusion asks at most C(X, j) in each
degree K - Delta < j <= K, with K = D - ceil(v^(1/3)), v = 2 m, X = 2(K - Delta) + 1 + (K - Delta + 1)/Delta.

The script computes h for K_{t,t} exactly from the boundary formula t(a + b) - 2ab over 1 <= a + b <= t, takes
H as d = ceil(h/2) - 1 perfect matchings (M = d t), and for the least, a middle and the largest admissible D and several Delta checks
by exact integers whether 2^j C(M, j) > C(ceil(X), j) at every j of the window.
"""
import argparse
import math
from fractions import Fraction


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--t", type=int, default=32)
    args = ap.parse_args()
    t = args.t
    n_v, m, r = 2 * t, t * t, t
    h = min(Fraction(t * (a + b) - 2 * a * b, a + b)
            for a in range(t + 1) for b in range(t + 1) if 1 <= a + b <= t)
    w = 2 * r
    d_top = math.ceil(h * n_v / 8) - 1
    deg_h = math.ceil(h / 2) - 1
    big_m = deg_h * t
    v = 2 * m
    cube = math.ceil(round(v ** (1 / 3), 9))
    with open(args.out, "w") as fh:
        fh.write(f"t={t} n_v={n_v} m={m} bits={v} r={r} w={w} h={h} proper_for_D_in=[{w},{d_top}] "
                 f"H_max_degree={deg_h} M={big_m} ceil_cuberoot_v={cube}\n")
        for big_d in (w, (w + d_top) // 2, d_top):
            k = big_d - cube
            for delta in (2, 4, 8, 12):
                if k - delta < 1:
                    continue
                x = math.ceil(Fraction(2 * (k - delta) + 1) + Fraction(k - delta + 1, delta))
                ok = all(2 ** j * math.comb(big_m, j) > math.comb(x, j)
                         for j in range(k - delta + 1, k + 1) if j <= big_d - 1)
                fh.write(f"D={big_d} K={k} Delta={delta} X={x} count_exceeds_thin_at_every_window_level={ok}\n")
    print("done")


if __name__ == "__main__":
    main()
