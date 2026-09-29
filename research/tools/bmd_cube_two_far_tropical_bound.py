"""Tropical (min-cost assignment) lower bound for the far-collision order of two-far windows (29 September 2026;
cycle bmd-20260929-zq; conj:cube-two-far-double-support).

After pulling out pi_01^n, the far span is g_0 = 1 + sum_{a>=2} x_a u^a, g_1 = u + sum_{a>=2} y_a u^a (u = 1/S) with
val x_a >= a, val y_a >= a - 1, and the near span has rows g_b = S^b + sum_{k>=n} gamma_(b,k) S^k (val gamma >= 0).
Row (1,b) = g_0 g_b and row (2,b) = g_1 g_b have entry valuations at column e bounded below by
  c1(b,e) = min{k - e : k in {b} u [n, inf), k - e in {0} u [2, inf)},
  c2(b,e) = min{k - e - 1 : k in {b} u [n, inf), k - e >= 1}.
The window E_r = [-m, n-1+r], m = n - r. Tested: the min-cost perfect assignment of these costs equals m(m-1), the
order predicted by the size clause (so that the clause would follow from a dual certificate, with no cancellation).
Uses scipy's linear_sum_assignment on (2n)x(2n) matrices.
"""
import argparse
import numpy as np
from scipy.optimize import linear_sum_assignment

BIG = 10**6


def costs(n, r, kmax):
    m = n - r
    E = list(range(-m, n + r))
    C = np.full((2 * n, 2 * n), BIG, dtype=np.int64)
    ks = lambda b: [b] + list(range(n, kmax))
    for b in range(n):
        for c, e in enumerate(E):
            v1 = [k - e for k in ks(b) if k - e == 0 or k - e >= 2]
            v2 = [k - e - 1 for k in ks(b) if k - e >= 1]
            if v1:
                C[b, c] = min(v1)
            if v2:
                C[n + b, c] = min(v2)
    return C


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out")
    a = ap.parse_args()
    lines = []
    for n in range(2, 9):
        for r in range(n):
            m = n - r
            C = costs(n, r, n + r + 5)
            ri, ci = linear_sum_assignment(C)
            v = int(C[ri, ci].sum())
            lines.append(f"n={n} r={r}: tropical minimum {v}, predicted m(m-1) = {m * (m - 1)}" + ("" if v == m * (m - 1) else "  MISMATCH"))
    text = "\n".join(lines)
    print(text)
    if a.out:
        open(a.out, "w").write(text + "\n")


if __name__ == "__main__":
    main()
