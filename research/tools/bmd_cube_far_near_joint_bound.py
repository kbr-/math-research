"""Joint-collision convex-cost lower bound for every F x n far-near window (29 September 2026; cycle bmd-20260929-zu).

For a cluster of F' far roots and n' near roots shrinking together (far s_i -> eta s_i, near t_j -> eta t_j), normalize
the far cluster span (g_i = u^i + sum_{a>=F'} x_a u^a, ord x_a = a - i) and the near cluster span (h_b = S^b +
sum_{k>=n'} gamma_(b,k) S^k, ord gamma = k - b); the other roots keep order-0 coefficients. The normalizations account
exactly for the eta-orders of Delta(s)^n and Delta(t)^F, so every double Schur coefficient pair (kappa, nu) in the
support satisfies: (sum of the F' smallest parts of kappa) + (sum of the n' smallest parts of nu) >= V(F', n'), the
min-cost assignment of the entry-order lower bounds (by the product-dominance maximal-violator argument).
Minimizing the caterpillar weight sum i kappa_i + sum j nu_j under all these constraints and the size relation gives a
lower bound for the window valuation (plus n binom(F+1,3) + F binom(n+1,3)). Compared with the measured valuations.
"""
import argparse
from functools import lru_cache
from math import comb
import numpy as np
from scipy.optimize import linear_sum_assignment

BIG = 10**6
MEASURED = {
    (2, 3): [19, 15, 17], (2, 4): [44, 34, 32, 36], (2, 5): [85, 67, 59, 59, 65],
    (3, 3): [48, 39, 38, 39, 48], (3, 4): [106, 87, 78, 72, 74, 80, 94], (4, 3): [94, 80, 74, 72, 78, 87, 106],
    (3, 5): [200, 168, 148, 132, 126, 125, 130, 141, 160], (4, 4): [200, 172, 154, 141, 138, 138, 141, 154, 172, 200],
}


def V(F, n, Fc, nc, E):
    """Min-cost assignment of entry-order lower bounds. Far rows: cluster i < Fc (u^i, u^a for a >= Fc with order
    a - i) and, separately normalized, the other F - Fc roots i' (u^i', u^a for a >= F - Fc, order 0). Near rows alike:
    cluster b < nc (S^b, S^k for k >= nc with order k - b) and the other n - nc roots b' (S^b', S^k for k >= n - nc)."""
    A = 3 * len(E) + F + n + 10
    far = [("c", i) for i in range(Fc)] + [("o", i) for i in range(F - Fc)]
    near = [("c", b) for b in range(nc)] + [("o", b) for b in range(n - nc)]
    def of(row, a):
        kind, i = row
        if a == i:
            return 0
        if kind == "c":
            return a - i if a >= Fc else None
        return 0 if a >= F - Fc else None
    def on(row, k):
        kind, b = row
        if k == b:
            return 0
        if kind == "c":
            return k - b if k >= nc else None
        return 0 if k >= n - nc else None
    C = np.full((F * n, F * n), BIG, dtype=np.int64)
    for x, fr in enumerate(far):
        for y, nr in enumerate(near):
            r = x * n + y
            for c, e in enumerate(E):
                best = None
                for a in range(0, A):
                    k = e + a
                    if k < 0:
                        continue
                    o1, o2 = of(fr, a), on(nr, k)
                    if o1 is None or o2 is None:
                        continue
                    best = o1 + o2 if best is None else min(best, o1 + o2)
                if best is not None:
                    C[r, c] = best
    ri, ci = linear_sum_assignment(C)
    return int(C[ri, ci].sum())


def parts(size, maxparts):
    out = []
    def rec(rem, mx, cur):
        if len(cur) > maxparts:
            return
        if rem == 0:
            out.append(tuple(cur + [0] * (maxparts - len(cur))))
            return
        for x in range(min(rem, mx), 0, -1):
            rec(rem - x, x, cur + [x])
    rec(size, size, [])
    return out


@lru_cache(maxsize=None)
def least_nu(need, size, n):
    """Exact minimum of the near weight sum_j j nu_j = sum_g R(g) over partitions nu with at most n parts and
    |nu| = size whose bottom sums R(g) (sum of the g smallest parts) satisfy R(g) >= need[g]; None if infeasible.
    Dynamic program over the parts from the bottom (nondecreasing), state (last part, running sum)."""
    INF = float("inf")
    if need[0] > 0:  # far-only constraints V(F', 0) not met by kappa
        return None
    cur = {(0, 0): 0}
    for g in range(1, n + 1):
        nxt = {}
        for (last, R), cost in cur.items():
            for d in range(last, size - R + 1):
                R2 = R + d
                if R2 < need[g]:
                    continue
                if g == n and R2 != size:
                    continue
                key = (d, R2)
                c2 = cost + R2
                if c2 < nxt.get(key, INF):
                    nxt[key] = c2
        cur = nxt
    return min(cur.values()) if cur else None


def predict(F, n, p):
    q = F * n - 1 - p
    E = list(range(-p, q + 1))
    Vt = {(f, g): V(F, n, f, g, E) for f in range(F + 1) for g in range(n + 1) if f + g > 0}
    D0 = sum(E) - F * comb(n, 2) + n * comb(F, 2)
    best = None
    for ks in range(max(0, -D0), max(0, -D0) + 80):
        ns = ks + D0
        if best is not None and ks + ns > best:
            break
        for ka in parts(ks, F):
            wk = sum((i + 1) * x for i, x in enumerate(ka))
            ksm = [sum(sorted(ka)[:f]) for f in range(F + 1)]
            need = [max([0] + [Vt[(f, g)] - ksm[f] for f in range(F + 1) if (f, g) in Vt]) for g in range(n + 1)]
            wn = least_nu(tuple(need), ns, n)
            if wn is not None and (best is None or wk + wn < best):
                best = wk + wn
    return n * comb(F + 1, 3) + F * comb(n + 1, 3) + best


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out")
    a = ap.parse_args()
    lines = []
    for (F, n), vals in MEASURED.items():
        preds = [predict(F, n, p) for p in range(F - 1, F * n - n + 1)]
        lines.append(f"{F}x{n}: predicted {preds}, measured {vals}" + ("  [equal]" if preds == vals else "  [DIFFER]"))
        print(lines[-1], flush=True)
    if a.out:
        open(a.out, "w").write("\n".join(lines) + "\n")


if __name__ == "__main__":
    main()
