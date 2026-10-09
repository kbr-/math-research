#!/usr/bin/env python3
"""Exact polynomial-calculus degree of small parity 2-clause systems by truncated completion.

Statement tested: for m = 3n products of two random nonzero distinct affine forms (generator of
research/results/near-half-quadratic-consistency-20261009, random.Random(1000*n + seed)), the
exact PC refutation degree over F_2, computed by tools/truncated_buchberger.py, equals the value
found by the static span test with multipliers |T| <= D-2 (3 at n = 12).  A smaller exact degree
would show the static value overestimates; equality certifies a lower bound for those instances.
Sizes: n = 8, 10, 12, three seeds, cutoffs up to 3 or 4; a few hundred leading monomials.
"""
import argparse
import json
import os
import random
import sys
import time

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", "tools"))
import truncated_buchberger as tb  # noqa: E402


def affine(n, rng):
    while True:
        mask = rng.getrandbits(n)
        if mask:
            return mask, rng.getrandbits(1)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--sizes", default="8:4,10:4,12:3", help="comma list of n:max_degree")
    args = ap.parse_args()
    with open(args.out, "a") as out:
        for n, maxd in (tuple(map(int, c.split(":"))) for c in args.sizes.split(",")):
            for seed in (1, 2, 3):
                rng = random.Random(1000 * n + seed)
                axioms = []
                for _ in range(3 * n):
                    f = affine(n, rng)
                    g = affine(n, rng)
                    while g[0] == f[0]:
                        g = affine(n, rng)
                    assert f[0] and g[0] and f[0] != g[0]
                    axioms.append(tb.affine_product(n, [f, g]))
                t0 = time.time()
                d = tb.pc_degree(axioms, n, maxd)
                rec = {"n": n, "m": 3 * n, "seed": seed, "pc_degree": d, "max_degree": maxd,
                       "seconds": round(time.time() - t0, 2)}
                out.write(json.dumps(rec) + "\n")
                out.flush()
                print(json.dumps(rec), flush=True)


if __name__ == "__main__":
    main()
