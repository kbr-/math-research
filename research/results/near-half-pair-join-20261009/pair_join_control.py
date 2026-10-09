#!/usr/bin/env python3
"""Exact binary controls for the pair-join degree drop.

Tested statement.  Let two Boolean modular rows over an odd prime q have even
widths 2h, nonzero coefficients, and meet in exactly one variable x.  For all
h-subsets S_a, S_b of the two scopes avoiding x, the monomial x_{S_a}x_{S_b}
(degree 2h) agrees on the join of the two allowed relations with a binary
polynomial of degree at most 2h-1.  Prediction: every tested case reduces.

Controls (predicted irreducible).
  single: on one paired central row, the monomial on its L half (degree h) has
          no representative of degree at most h-1.
  shared-selected: two paired central rows meeting in an L variable x; the
          monomial on all L variables of the union (degree 2h-1, x included)
          has no representative of degree at most 2h-2.

Hypotheses are asserted in code: odd prime modulus, nonzero coefficients,
exactly one shared variable, and nonempty relations.  All arithmetic is exact
over F_2 with integer bitsets; sizes are at most 2^11 points.
"""
import argparse
import itertools
import json
import random


def row_points(coeffs, target, q):
    k = len(coeffs)
    pts = []
    for bits in itertools.product((0, 1), repeat=k):
        if sum(c * b for c, b in zip(coeffs, bits)) % q == target % q:
            pts.append(bits)
    return pts


def paired_row(h, q, rng, central=True):
    """Variables ordered L_1..L_h, R_1..R_h; pair j is (L_j, R_j)."""
    a = [rng.randrange(1, q) for _ in range(h)]
    eps = [rng.choice((1, -1)) for _ in range(h)]
    coeffs = a + [(e * c) % q for e, c in zip(eps, a)]
    inv2 = pow(2, -1, q)
    target = (sum(coeffs) * inv2) % q
    if not central:
        target = (target + rng.randrange(1, q)) % q
    return coeffs, target


def generic_row(h, q, rng, central):
    inv2 = pow(2, -1, q)
    while True:  # resample until the relation is nonempty
        coeffs = [rng.randrange(1, q) for _ in range(2 * h)]
        target = (sum(coeffs) * inv2) % q
        if not central:
            target = (target + rng.randrange(1, q)) % q
        if row_points(coeffs, target, q):
            return coeffs, target


def in_low_degree_span(points, nvars, mono, maxdeg):
    """Is the evaluation vector of `mono` on `points` in the F_2 span of the
    evaluations of all monomials of degree at most maxdeg?"""
    def vec(subset):
        v = 0
        for i, p in enumerate(points):
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
    for d in range(maxdeg + 1):
        for subset in itertools.combinations(range(nvars), d):
            v, top = reduce(vec(subset))
            if v:
                basis[top] = v
    v, _ = reduce(vec(mono))
    return v == 0


def join(row_a, row_b, h, pos_a, pos_b, q):
    """Join two rows identifying variable pos_a of a with pos_b of b.
    Returns points on the union ordered: a's variables, then b's without the
    shared one; plus index maps."""
    pa = row_points(*row_a, q)
    pb = row_points(*row_b, q)
    assert pa and pb, "relations must be nonempty"
    k = 2 * h
    idx_b = {}
    nxt = k
    for j in range(k):
        if j == pos_b:
            idx_b[j] = pos_a
        else:
            idx_b[j] = nxt
            nxt += 1
    pts = []
    by_val = {0: [], 1: []}
    for p in pb:
        by_val[p[pos_b]].append(p)
    for p in pa:
        for r in by_val[p[pos_a]]:
            full = list(p) + [r[j] for j in range(k) if j != pos_b]
            pts.append(tuple(full))
    return pts, nxt, idx_b


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--seed", type=int, default=20261009)
    args = ap.parse_args()
    rng = random.Random(args.seed)
    results = {"seed": args.seed, "drop": [], "single": [], "shared_selected": []}

    # Drop test: every pair of h-subsets avoiding the shared variable.
    cases = []
    for h, q, reps in ((2, 5, 6), (2, 7, 6), (2, 11, 4), (3, 5, 2), (3, 7, 2), (3, 11, 2)):
        cases += [(h, q, "paired-central", rep) for rep in range(reps)]
        cases += [(h, q, kind, 0) for kind in ("generic-central", "generic-noncentral")]
    for h, q, kind, rep in cases:
        results["drop"] += drop_case(h, q, kind, rep, rng)

    # Controls.
    controls = []
    for h, q, reps in ((2, 5, 6), (2, 7, 6), (3, 5, 4), (3, 7, 4), (3, 11, 4)):
        controls += [(h, q, rep) for rep in range(reps)]
    for h, q, rep in controls:
        ra, rb = paired_row(h, q, rng), paired_row(h, q, rng)
        k = 2 * h
        pa = row_points(*ra, q)
        red = in_low_degree_span(pa, k, tuple(range(h)), h - 1)
        results["single"].append({"h": h, "q": q, "rep": rep, "points": len(pa),
                                  "reducible": bool(red)})
        pts, n, idx_b = join(ra, rb, h, 0, 0, q)
        mono = tuple(range(h)) + tuple(idx_b[j] for j in range(1, h))
        assert len(set(mono)) == 2 * h - 1
        red = in_low_degree_span(pts, n, mono, 2 * h - 2)
        results["shared_selected"].append({"h": h, "q": q, "rep": rep,
                                           "points": len(pts), "reducible": bool(red)})

    summary = {
        "drop_cases": sum(r["tested"] for r in results["drop"]),
        "drop_reduced": sum(r["reduced"] for r in results["drop"]),
        "drop_instances": len(results["drop"]),
        "single_controls": len(results["single"]),
        "single_reducible": sum(r["reducible"] for r in results["single"]),
        "shared_selected_controls": len(results["shared_selected"]),
        "shared_selected_reducible": sum(r["reducible"] for r in results["shared_selected"]),
    }
    results["summary"] = summary
    with open(args.out, "w") as f:
        json.dump(results, f, indent=1)
    print(json.dumps(summary))


def drop_case(h, q, kind, rep, rng):
    if kind == "paired-central":
        ra, rb = paired_row(h, q, rng), paired_row(h, q, rng)
    else:
        c = kind == "generic-central"
        ra, rb = generic_row(h, q, rng, c), generic_row(h, q, rng, c)
    assert q % 2 == 1 and all(x % q for x in ra[0] + rb[0])
    k = 2 * h
    out = []
    for pos, label in ((k - 1, "R-R"), (0, "L-L")):
        pts, n, idx_b = join(ra, rb, h, pos, pos, q)
        assert n == 4 * h - 1
        tested, reduced = drop_all(pts, n, k, h, pos, pos, idx_b)
        out.append({"h": h, "q": q, "kind": kind, "shared": label, "rep": rep,
                    "points": len(pts), "tested": tested, "reduced": reduced})
    return out


def drop_all(pts, n, k, h, pos_a, pos_b, idx_b):
    """Test every pair of h-subsets avoiding the shared variable against one
    echelon basis of the degree<=2h-1 evaluations."""
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
    for d in range(2 * h):
        for subset in itertools.combinations(range(n), d):
            v, top = reduce(vec(subset))
            if v:
                basis[top] = v
    tested = reduced = 0
    for sa in itertools.combinations([j for j in range(k) if j != pos_a], h):
        for sb in itertools.combinations([j for j in range(k) if j != pos_b], h):
            mono = tuple(sa) + tuple(idx_b[j] for j in sb)
            tested += 1
            if reduce(vec(mono))[0] == 0:
                reduced += 1
    return tested, reduced


if __name__ == "__main__":
    main()
