#!/usr/bin/env python3
"""Exact binary graded structure of one paired central modular row.

Question explored.  For a row sum_j a_j (x_{u_j} + eps_j x_{v_j}) = central target
mod q on h pairs, and each degree s <= h, compute over F_2:
  g(s)   = number of standard monomials of degree s (dimension of the degree-s
           graded piece of the function algebra of the allowed set R);
  pair(s)= number of degree-s monomials containing a full pair {u_j, v_j} that
           have NO representative of degree < s on R   (hypothesis H1 fails);
  swap(s)= number of (pair j, monomial m of degree s-1 avoiding pair j) for which
           x_{u_j} m + x_{v_j} m has NO representative of degree < s on R
           (hypothesis H2 fails).
Also the least support size w of a nonzero ternary solution of sum a_j y_j = 0
(the smallest signed zero-sum set of pair weights), found by enumeration.

Prediction tested: pair(s) = swap(s) = 0 for all s > h - w + 1, and g(s) =
binom(h, s) in that range.  Sizes: h <= 6, at most 4096 points; exact bitset
linear algebra.  Hypotheses asserted: odd prime q, distinct nonzero |a_j|.
"""
import argparse
import itertools
import json
import random
from math import comb


def build_row(h, q, rng):
    while True:
        a = [rng.randrange(1, q) for _ in range(h)]
        classes = {min(x, q - x) for x in a}
        if len(classes) == h:
            break
    eps = [rng.choice((1, -1)) for _ in range(h)]
    coeffs = a + [(e * c) % q for e, c in zip(eps, a)]
    target = (sum(coeffs) * pow(2, -1, q)) % q
    pts = [p for p in itertools.product((0, 1), repeat=2 * h)
           if sum(c * b for c, b in zip(coeffs, p)) % q == target]
    return a, eps, coeffs, pts


def min_block(a, q):
    """Least support size w of a nonzero y in {-1,0,1}^h with sum a_j y_j = 0 mod q
    (None if there is none): the smallest signed zero-sum set of pair weights."""
    h = len(a)
    for w in range(1, h + 1):
        for subset in itertools.combinations(range(h), w):
            sums = {a[subset[0]] % q}
            for i in subset[1:]:
                sums = {(x + a[i]) % q for x in sums} | {(x - a[i]) % q for x in sums}
            if 0 in sums:
                return w
    return None


def analyse(h, q, rng):
    a, eps, coeffs, pts = build_row(h, q, rng)
    k = 2 * h
    npts = len(pts)

    def vec(subset):
        v = 0
        for i, p in enumerate(pts):
            if all(p[j] for j in subset):
                v |= 1 << i
        return v

    basis = {}

    def reduce(v):
        while v:
            top = v.bit_length() - 1
            if top not in basis:
                return v, top
            v ^= basis[top]
        return 0, None

    out = {"h": h, "q": q, "points": npts, "min_block": min_block(a, q), "levels": []}
    for s in range(0, h + 1):
        # at this moment `basis` spans evaluations of all monomials of degree < s
        pair_fail = swap_fail = pair_total = swap_total = 0
        monos = list(itertools.combinations(range(k), s))
        for mono in monos:
            ms = set(mono)
            if any(j in ms and j + h in ms for j in range(h)):
                pair_total += 1
                if reduce(vec(mono))[0]:
                    pair_fail += 1
        if s >= 1:
            for j in range(h):
                others = [i for i in range(k) if i not in (j, j + h)]
                for m in itertools.combinations(others, s - 1):
                    swap_total += 1
                    if reduce(vec((j,) + m) ^ vec((j + h,) + m))[0]:
                        swap_fail += 1
        g = 0
        for mono in monos:
            v, top = reduce(vec(mono))
            if v:
                basis[top] = v
                g += 1
        out["levels"].append({"s": s, "g": g, "flat": comb(h, s), "monomials": len(monos),
                              "pair_fail": pair_fail, "pair_total": pair_total,
                              "swap_fail": swap_fail, "swap_total": swap_total})
    assert len(basis) == npts
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--seed", type=int, default=20261009)
    args = ap.parse_args()
    rng = random.Random(args.seed)
    cases = [(3, 7), (3, 13), (3, 31), (4, 11), (4, 31), (4, 61), (4, 127),
             (5, 13), (5, 31), (5, 61), (5, 127), (5, 251), (6, 31), (6, 127), (6, 509)]
    results = []
    with open(args.out, "w") as f:
        for h, q in cases:
            r = analyse(h, q, rng)
            results.append(r)
            f.seek(0)
            f.truncate()
            json.dump({"seed": args.seed, "results": results}, f, indent=1)
            f.flush()
    for r in results:
        w = r["min_block"]
        bad = [lv["s"] for lv in r["levels"] if lv["pair_fail"] or lv["swap_fail"] or lv["g"] != lv["flat"]]
        pred = [s for s in range(1, r["h"] + 1) if w is not None and s <= r["h"] - w + 2]
        print(r["h"], r["q"], r["points"], "w", w, "failing degrees", bad, "predicted", pred,
              "match", bad == pred)


if __name__ == "__main__":
    main()
