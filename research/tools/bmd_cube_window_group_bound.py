"""Dominant-root Cauchy-Binet lower bounds for far-near product windows (29 September 2026; cycle
bmd-20260929-zj).

Rows (i, j), i = 1..F far, j = 1..n near: the coefficient of S^e in (1+s_i/S)^(-l)(1+t_j S)^(-l) is
sum_{b-a=e} beta_a beta_b s_i^a t_j^b. The far constants s_i have valuations {1..F}, the near t_j {1..n}.

Grouping the rows by near root j, row(i,j) = sum_a [beta_a s_i^a] T_j(a, e) with T_j(a, e) = beta_(e+a)
t_j^(e+a), and Cauchy-Binet as in thm:cube-caterpillar-minimality gives, for a column set E,
    val P_E >= n val Vand(s) + min over partitions of E into groups C_j (|C_j| = F) of sum_j cost_j(C_j),
    cost_j(C) = min_K [ sum_t (k_t - (F - t)) sigma_t + tau_j (sum C + sum K) ],
with K = {k_1 > ... > k_F >= 0} matched to C = {c_1 < ... < c_F} by k_t >= -c_t, sigma_t = t (the
dominant Schur monomial) and tau_j = j. Grouping by far root gives the mirror bound (E -> -E, F <-> n).

Tested statement: whether max(bound_near, bound_far) equals the measured minimal valuation and picks the
measured minimizing windows (2x2 tie at 6; 2x3 {-2..3} at 15; 2x4 {-3..4} at 32; 3x3 {-4..4} at 38).
Prints both bounds for every window of length Fn containing {-(F-1)..n-1}.
"""
import argparse
import itertools
from math import comb


def cost(C, F, tau):
    c = sorted(C)
    k = [0] * F
    for t in range(F - 1, -1, -1):
        need = max(0, -c[t])
        k[t] = need if t == F - 1 else max(k[t + 1] + 1, need)
    # k is descending (k[0] largest, matched to c[0] smallest)
    schur = sum((k[t] - (F - 1 - t)) * (t + 1) for t in range(F))
    return schur + tau * (sum(c) + sum(k))


def bound(E, F, n):
    base = n * comb(F + 1, 3)
    best = None

    def rec(rem, j, acc):
        nonlocal best
        if best is not None and acc >= best:
            return
        if j > n:
            best = acc
            return
        first = rem[0]
        # assign groups in order; group j takes any F-subset (labelled groups, so no symmetry cut)
        for S in itertools.combinations(rem, F):
            rest = [x for x in rem if x not in S]
            rec(rest, j + 1, acc + cost(S, F, j))

    rec(sorted(E), 1, 0)
    return base + best


def both(E, F, n):
    return bound(E, F, n), bound([-e for e in E], n, F)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out")
    args = ap.parse_args()
    lines = []
    for F, n in [(2, 2), (2, 3), (3, 2), (2, 4), (4, 2), (3, 3)]:
        L = F * n
        lines.append(f"{F}x{n}:")
        for p in range(F - 1, F * n - n + 1):
            E = list(range(-p, -p + L))
            bn, bf = both(E, F, n)
            lines.append(f"  window [{-p},{-p + L - 1}]: near-group bound {bn}, far-group bound {bf}, max {max(bn, bf)}")
    text = "\n".join(lines)
    print(text)
    if args.out:
        with open(args.out, "w") as f:
            f.write(text + "\n")


if __name__ == "__main__":
    main()
