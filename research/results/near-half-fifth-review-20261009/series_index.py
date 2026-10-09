#!/usr/bin/env python3
"""Index of the first non-positive coefficient of (1+z)^n / prod_i (1+z^{k_i}).

Statement tested (the review's stage-one Option 1, a hand heuristic of the reviewer): for m rows of
degree k on n Boolean variables the semi-regular prediction D*(n) = least D with coefficient <= 0
satisfies D*/n bounded away from 1/2 (reviewer's estimate: near 1/3) at covering density
m = ceil(ln2 * 2^k * n) with fixed k, and D*/n -> 1/2 for "barely covering" profiles with
sum_i 2^{-k_i} = O(1), here m = c * 2^k rows of width k = round(log2 n) + j.

This computes a property of a power series only; it measures no polynomial system.  Exact integer
arithmetic; division by (1+z^k)^mult multiplies by sum_i (-1)^i C(mult+i-1, i) z^{ik}.  Sizes: n up to
1024.
"""
import argparse
import json
import math


def index(n, widths):
    """widths: dict k -> multiplicity.  Returns least D <= n with coefficient <= 0, or None."""
    coef = [math.comb(n, j) for j in range(n + 1)]
    for k, mult in sorted(widths.items()):
        # dividing by (1+z^k)^mult: multiply by sum_i (-1)^i C(mult+i-1, i) z^{ik}
        new = [0] * (n + 1)
        i, sign = 0, 1
        while i * k <= n:
            f = sign * math.comb(mult + i - 1, i)
            for j in range(n + 1 - i * k):
                new[j + i * k] += f * coef[j]
            i += 1
            sign = -sign
        coef = new
    for D, c in enumerate(coef):
        if c <= 0:
            return D
    return None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--mixed", action="store_true", help="mixed-width profiles of total cover 1")
    args = ap.parse_args()
    rows = []
    if args.mixed:
        # total cover sum 2^{-k_i} = 1, split equally between two widths
        for n in (256, 1024):
            k0 = round(math.log2(n))
            for a, b in ((k0 - 3, k0 + 3), (k0, 2 * k0), (k0 - 1, k0 + 1), (k0 + 4, k0 + 5)):
                w = {a: 2 ** (a - 1), b: 2 ** (b - 1)}
                rows.append({"profile": "mixed", "n": n, "widths": [a, b], "m": sum(w.values()),
                             "cover": 1, "index": index(n, w)})
    for n in (() if args.mixed else (64, 128, 256, 512, 1024)):
        for k in (2, 3, 4, 6):
            m = math.ceil(math.log(2) * 2 ** k * n)
            rows.append({"profile": "threshold", "n": n, "k": k, "m": m, "index": index(n, {k: m})})
        k0 = round(math.log2(n))
        for j in (0, 2):
            for c in (1, 4):
                k = k0 + j
                m = c * 2 ** k
                rows.append({"profile": "barely", "n": n, "k": k, "m": m, "cover": c,
                             "index": index(n, {k: m})})
    with open(args.out, "w") as fh:
        for r in rows:
            r["ratio"] = None if r["index"] is None else round(r["index"] / r["n"], 4)
            fh.write(json.dumps(r) + "\n")
            print(json.dumps(r), flush=True)


if __name__ == "__main__":
    main()
