"""Wronskian exponent count for relations of the confluent tie window (8 October 2026; cycle bmd-20261008-i).

A left-kernel relation of the window rows on the columns T^d..T^(d+M-1) (d = binom(m,2)) is
G = g1 + g2 + g3 + g4 + g5 = O(T^(d+M)) with
  g1 = P (1+T)^(-5/2), deg P < 2m;      g2 = Q (1+cT)^(-3/2), deg Q < m;   g3 = alpha (1+T)^(-3);
  g4 = u (1+T)^(-5/2) (1+cT)^(-3/2), deg u <= 1;   g5 = -L, deg L < d (the part below T^d).
The nonzero g_i (set S, k = |S|) are linearly independent over C, so their Wronskian W is nonzero, and
sum over z in P^1 of ord_z W = 0.  At z in {0, -1, -1/c} ord_z W >= (sum of the span's distinct exponents) - k(k-1)/2;
at oo (in t = 1/T) ord >= sum + k(k-1)/2; elsewhere ord >= 0.  Hence 0 >= B(S) := sum of the minimal distinct
exponents over the four points - k(k-1), and B(S) > 0 excludes S.
Minimal exponents (class = residue mod 1):
  z = 0: the span contains G of order >= d+M; the other k-1 exponents >= 0, 1, ..., k-2.
  z = -1:   g1 -5/2, g2 0, g3 -3, g4 -5/2, g5 0;
  z = -1/c: g1 0, g2 -3/2, g3 0, g4 -3/2, g5 0;
  z = oo:   g1 5/2-(2m-1), g2 3/2-(m-1), g3 3, g4 4-1, g5 -(d-1).
Within a class, exponents of a span are distinct, so sorted minimal values e_1 <= e_2 <= ... are raised to
e'_j = max(e_j, e'_(j-1) + 1).  For each m and each nonempty S, prints the least B(S) for M = 3m+5 (the window) and
M = 3m+6, and the subsets attaining it.  For g5 the degree bound d-1 needs d >= 1 (m >= 2); for m = 1, g5 = 0.

Usage: python3 bmd_tie_exponent_count.py --out PATH
"""
import argparse
import itertools
from fractions import Fraction as Fr


def distinct_sum(vals):
    tot = Fr(0)
    for cls in set(v % 1 for v in vals):
        es = sorted(v for v in vals if v % 1 == cls)
        prev = None
        for e in es:
            e2 = e if prev is None else max(e, prev + 1)
            tot += e2
            prev = e2
    return tot


def bound(m, S, M):
    d = m * (m - 1) // 2
    k = len(S)
    ex = {
        -1: {1: Fr(-5, 2), 2: Fr(0), 3: Fr(-3), 4: Fr(-5, 2), 5: Fr(0)},
        'c': {1: Fr(0), 2: Fr(-3, 2), 3: Fr(0), 4: Fr(-3, 2), 5: Fr(0)},
        'oo': {1: Fr(5, 2) - (2 * m - 1), 2: Fr(3, 2) - (m - 1), 3: Fr(3), 4: Fr(3), 5: Fr(-(d - 1))},
    }
    tot = Fr(sum(range(k - 1))) + d + M
    for z in ex:
        tot += distinct_sum([ex[z][i] for i in S])
    return tot - k * (k - 1)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--out', required=True)
    args = ap.parse_args()
    lines = []
    for m in range(1, 41):
        funcs = [1, 2, 3, 4] + ([5] if m >= 2 else [])
        subsets = [S for r in range(1, len(funcs) + 1) for S in itertools.combinations(funcs, r)]
        row = [f"m = {m}:"]
        for M in (3 * m + 5, 3 * m + 6):
            vals = {S: bound(m, S, M) for S in subsets}
            lo = min(vals.values())
            att = [S for S in subsets if vals[S] == lo]
            row.append(f"M = {M}: least B = {lo} at {att}")
        lines.append("  ".join(row))
    with open(args.out, 'w') as fh:
        fh.write("\n".join(lines) + "\n")
    print("\n".join(lines[:6] + lines[-2:]))


if __name__ == '__main__':
    main()
