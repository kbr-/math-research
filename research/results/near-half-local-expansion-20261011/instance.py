#!/usr/bin/env python3
"""The local-expansion form of the lemmas on flow systems, evaluated on the complete bipartite graph K_{t,t}.

Statement evaluated: for the flow system modulo three on two-bit blocks over a connected graph with n_v
vertices and edge expansion h, and w <= D < h n_v / 8: let sigma be the largest size of a vertex set U with
|U| < n_v / 2 and at most 2D boundary edges, and h_sigma the least ratio |boundary U| / |U| over non-empty U
of at most sigma vertices.  For a subgraph H of maximum degree below h_sigma / 2 with M edges, one bit from
each edge of H is a set of M variables shattered through degree D.  The thin window asks every shattered set
to have at most X = 2(K - Delta) + 1 + (K - Delta + 1)/Delta elements, K = D - ceil(v^(1/3)).

For K_{t,t} a set with a left and b right vertices has boundary t(a + b) - 2ab; the script computes sigma and
h_sigma exactly from that formula for the least, a middle and the largest admissible D, takes H as
ceil(h_sigma / 2) - 1 perfect matchings, and compares M with ceil(X) for several Delta.
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
    n_v, m, w = 2 * t, t * t, 2 * t
    sets = [(a, b) for a in range(t + 1) for b in range(t + 1) if 1 <= a + b]
    boundary = lambda a, b: t * (a + b) - 2 * a * b
    h = min(Fraction(boundary(a, b), a + b) for a, b in sets if a + b <= t)
    d_top = math.ceil(h * n_v / 8) - 1
    cube = math.ceil(round((2 * m) ** (1 / 3), 9))
    with open(args.out, "w") as fh:
        fh.write(f"t={t} n_v={n_v} m={m} bits={2 * m} w={w} h={h} range=[{w},{d_top}]\n")
        for big_d in (w, (w + d_top) // 2, d_top):
            small = [(a, b) for a, b in sets if a + b < t and boundary(a, b) <= 2 * big_d]
            sigma = max((a + b for a, b in small), default=0)
            h_sigma = min(Fraction(boundary(a, b), a + b) for a, b in sets if a + b <= sigma)
            deg_h = min(t, math.ceil(h_sigma / 2) - 1)
            big_m = deg_h * t
            k = big_d - cube
            for delta in (1, 2, 4, 8, 12):
                if k - delta < 1:
                    continue
                x = math.ceil(Fraction(2 * (k - delta) + 1) + Fraction(k - delta + 1, delta))
                fh.write(f"D={big_d} sigma={sigma} h_sigma={h_sigma} ({float(h_sigma):.3f}) H_max_degree={deg_h} "
                         f"M={big_m} K={k} Delta={delta} X={x} shattered_set_exceeds_X={big_m > x}\n")
    print("done")


if __name__ == "__main__":
    main()
