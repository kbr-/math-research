#!/usr/bin/env python3
"""Write parity 2-clause instances and the predictions of the two hypotheses.

Instances use the same generator as research/results/near-half-quadratic-consistency-20261009/
parity_two_clause_degree.py (random.Random(1000*n + seed), m = 3n rows, two nonzero distinct
affine forms per row), so the compiled kernel can be validated on identical systems.

File format: first line "n m"; then m lines "mask1 const1 mask2 const2" (decimal masks).
Predictions (printed and saved): the index of regularity of (1+t)^n/(1+t^2)^m, and the two
forms of the competing lower bound discussed in the notebook, n/2 - sqrt(2n) and n/2 - sqrt(n/2).
"""
import argparse
import json
import os
import random
from math import comb, sqrt


def series_index(n, m, k=2, maxd=60):
    inv = [0] * (maxd + 1)
    for j in range(0, maxd // k + 1):
        inv[k * j] = (-1) ** j * comb(m + j - 1, j)
    for d in range(maxd + 1):
        if sum(comb(n, d - e) * inv[e] for e in range(d + 1)) <= 0:
            return d
    return None


def affine(n, rng):
    while True:
        mask = rng.getrandbits(n)
        if mask:
            return mask, rng.getrandbits(1)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dir", required=True)
    args = ap.parse_args()
    preds = []
    for n in (12, 16, 20, 24, 28, 32):
        m = 3 * n
        for seed in (1, 2, 3):
            rng = random.Random(1000 * n + seed)
            lines = [f"{n} {m}"]
            for _ in range(m):
                f = affine(n, rng)
                g = affine(n, rng)
                while g[0] == f[0]:
                    g = affine(n, rng)
                lines.append(f"{f[0]} {f[1]} {g[0]} {g[1]}")
            with open(os.path.join(args.dir, f"inst_n{n}_s{seed}.txt"), "w") as fh:
                fh.write("\n".join(lines) + "\n")
        preds.append({"n": n, "m": m, "series_index": series_index(n, m),
                      "half_minus_sqrt_2n": round(n / 2 - sqrt(2 * n), 2),
                      "half_minus_sqrt_half_n": round(n / 2 - sqrt(n / 2), 2)})
    with open(os.path.join(args.dir, "predictions.json"), "w") as fh:
        json.dump(preds, fh, indent=1)
    for p in preds:
        print(json.dumps(p))


if __name__ == "__main__":
    main()
