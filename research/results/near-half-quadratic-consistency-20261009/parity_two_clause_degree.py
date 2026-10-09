#!/usr/bin/env python3
"""Static refutation degree of random parity 2-clause systems over F_2.

Statement tested.  For m = 3n rows, each the product (l1 + b1)(l2 + b2) of two
independent uniform nonzero affine forms on n Boolean variables, the least D such
that 1 lies in the F_2-span of the multilinear products  x_T * f_i  of degree at
most D (static Nullstellensatz degree, an upper bound for the polynomial-calculus
refutation degree) equals the index of regularity of (1+t)^n / (1+t^2)^m, the
semi-regular prediction, and is far below n/2.

Hypotheses asserted in code: forms nonzero and distinct within a row; products
reduced multilinearly; arithmetic exact over F_2 (Python integers as bit sets).
Convention: multipliers x_T with |T| <= D-2 only; products with |T| = D-1 whose
degree drops are not used, so the value reported can exceed the true static degree
and never falls below it.  Outcome of the run of 9 October 2026: the stated equality
with the index failed at n = 20 (4 against 3); see results.json.
Sizes: n = 12, 16, 20 and D <= 4, at most 6196 columns and 12660 rows, a few
seconds.  A found certificate proves unsatisfiability; "none<=4" means no static
certificate through degree 4 (the system may be satisfiable).
"""
import argparse
import itertools
import json
import random
from math import comb


def series_index(n, m, k=2, maxd=40):
    """Least d with non-positive coefficient of (1+t)^n / (1+t^k)^m."""
    inv = [0] * (maxd + 1)
    for j in range(0, maxd // k + 1):
        inv[k * j] = (-1) ** j * comb(m + j - 1, j)
    for d in range(maxd + 1):
        c = sum(comb(n, d - e) * inv[e] for e in range(d + 1))
        if c <= 0:
            return d
    return None


def affine(n, rng):
    while True:
        mask = rng.getrandbits(n)
        if mask:
            return mask, rng.getrandbits(1)


def product_poly(n, f, g):
    """Multilinear product of two affine forms as a set of monomial bitmasks."""
    def terms(form):
        mask, const = form
        t = [1 << i for i in range(n) if mask >> i & 1]
        if const:
            t.append(0)
        return t
    poly = set()
    for a in terms(f):
        for b in terms(g):
            poly ^= {a | b}
    return poly


def static_degree(n, rows, maxdeg):
    for D in range(2, maxdeg + 1):
        monos = [sum(1 << i for i in c) for d in range(D + 1) for c in itertools.combinations(range(n), d)]
        index = {mono: j for j, mono in enumerate(monos)}
        pivots = {}
        target = 1 << index[0]
        mult = [mono for mono in monos if bin(mono).count("1") <= D - 2]

        def reduce(v):
            while v:
                h = v.bit_length() - 1
                p = pivots.get(h)
                if p is None:
                    return v, h
                v ^= p
            return 0, None

        for poly in rows:
            for mono in mult:
                acc = set()
                for t in poly:
                    acc ^= {t | mono}
                v = 0
                for t in acc:
                    v |= 1 << index[t]
                v, h = reduce(v)
                if v:
                    pivots[h] = v
        v, _ = reduce(target)
        if v == 0:
            return D, len(monos), len(rows) * len(mult)
    return None, None, None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    args = ap.parse_args()
    results = []
    for n in (12, 16, 20):
        m = 3 * n
        for seed in (1, 2, 3):
            rng = random.Random(1000 * n + seed)
            rows = []
            for _ in range(m):
                f = affine(n, rng)
                g = affine(n, rng)
                while g[0] == f[0]:
                    g = affine(n, rng)
                assert f[0] and g[0] and f[0] != g[0]
                rows.append(product_poly(n, f, g))
            D, cols, nrows = static_degree(n, rows, 4)
            rec = {"n": n, "m": m, "seed": seed, "static_degree": D if D else "none<=4",
                   "series_index": series_index(n, m), "half": n // 2, "columns": cols, "products": nrows}
            results.append(rec)
            print(json.dumps(rec), flush=True)
    with open(args.out, "w") as fh:
        json.dump(results, fh, indent=1)


if __name__ == "__main__":
    main()
