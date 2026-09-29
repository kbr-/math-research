"""Tropical proof test for the two-far window formula at caterpillar weights (29 September 2026; cycle bmd-20260929-zq;
conj:cube-two-far-window-valuations).

After the Kronecker normalization P_E = (det A)^n (det B)^2 [g_0 N + g_1 N]_E, with far span g_0 = 1 + sum_{a>=2} x_a u^a,
g_1 = u + sum_{a>=2} y_a u^a and near rows g_b = S^b + sum_{k>=n} gamma_(b,k) S^k, the caterpillar valuations are exact:
val x_a = a + 1, val y_a = a - 1 (a >= 2; y_1 = 1), val gamma_(b,k) = (k-n+1) + (n-b)(n-b+1)/2 - 1, val det A = 1,
val det B = binom(n+1,3). Entry (1,b),e = sum_k gamma_(b,k) x_(k-e) (k in {b} u [n,..), k-e in {0} u [2,..)),
entry (2,b),e = sum_k gamma_(b,k) y_(k-e) (k-e >= 1). Tested, for n = 2..8 and every r:
 (1) the min-cost assignment of the entry valuations equals T = v0 - n - 2 binom(n+1,3), where
     v0 = n^2 + 2 binom(n+1,3) - 2nr + r(r+1)(r+5)/3 is the conjectured window valuation;
 (2) the optimal assignment is unique, and in each of its entries the minimizing k is unique.
If (1) and (2) both held, the leading coefficient would be a product of nonzero leading coefficients and val P_E = v0.
(The run of 29 September 2026 finds (1) only for r <= 1 and (2) never.)
"""
import argparse
import itertools
import numpy as np
from scipy.optimize import linear_sum_assignment

BIG = 10**6


def entry_costs(n, r, kmax):
    m = n - r
    E = list(range(-m, n + r))
    g = lambda b, k: 0 if k == b else (k - n + 1) + (n - b) * (n - b + 1) // 2 - 1
    vx = lambda a: 0 if a == 0 else (a + 1 if a >= 2 else None)
    vy = lambda a: None if a < 1 else (0 if a == 1 else a - 1)
    C = np.full((2 * n, 2 * n), BIG, dtype=np.int64)
    U = np.zeros((2 * n, 2 * n), dtype=bool)
    for b in range(n):
        ks = [b] + list(range(n, kmax))
        for c, e in enumerate(E):
            for row, vf in ((b, vx), (n + b, vy)):
                vals = [g(b, k) + vf(k - e) for k in ks if k - e >= 0 and vf(k - e) is not None]
                if vals:
                    mn = min(vals)
                    C[row, c] = mn
                    U[row, c] = vals.count(mn) == 1
    return C, U


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out")
    a = ap.parse_args()
    lines = []
    for n in range(2, 9):
        for r in range(n):
            B = (n + 1) * n * (n - 1) // 6
            v0 = n * n + 2 * B - 2 * n * r + r * (r + 1) * (r + 5) // 3
            T = v0 - n - 2 * B
            C, U = entry_costs(n, r, n + r + 3 * n + 10)
            ri, ci = linear_sum_assignment(C)
            v = int(C[ri, ci].sum())
            uniq = True
            for x, y in zip(ri, ci):
                C2 = C.copy(); C2[x, y] = BIG
                r2, c2 = linear_sum_assignment(C2)
                if int(C2[r2, c2].sum()) == v:
                    uniq = False; break
            entries = all(U[x, y] for x, y in zip(ri, ci))
            lines.append(f"n={n} r={r}: tropical minimum {v}, target {T}, unique optimum {uniq}, unique k in entries {entries}"
                         + ("" if v == T and uniq and entries else "  <--"))
    text = "\n".join(lines)
    print(text)
    if a.out:
        open(a.out, "w").write(text + "\n")


if __name__ == "__main__":
    main()
