"""Convex-cost lower bound for every F x n far-near window, against the measured valuations (29 September 2026;
cycle bmd-20260929-zu; generalizes thm:cube-two-far-size-clause and thm:cube-two-far-dominance-clause).

Normalizing the far span as g_0..g_{F-1} (g_i = u^i + ..., coefficient of u^a of order a - i) gives the rows g_i h_b
level b - i. Near roots colliding (q of them) give each Schur coefficient T_kappa(t) order at least
V_t(q) = sum_j max(0, C_j - L_j) (cluster levels L sorted, lowest F q columns C of the window), i.e. the q smallest parts
of nu sum to at least V_t(q). The mirror S -> 1/S (far <-> near, window [-p, q] -> [-q, p]) gives V_s for kappa.
With |nu| - |kappa| = sum E - F binom(n,2) + n binom(F,2), the least weight is attained by the componentwise
smallest admissible partitions (greedy from the bottom part), extra size going to the first part (weight 1 each).
Predicted lower bound: n binom(F+1,3) + F binom(n+1,3) + least weight. Compared with the q-adic valuations of
cycles bmd-20260929-zj (all windows) at caterpillar weights (far 1..F, near 1..n).
"""
import argparse
from math import comb

MEASURED = {
    (2, 2): [6, 6], (2, 3): [19, 15, 17], (2, 4): [44, 34, 32, 36], (2, 5): [85, 67, 59, 59, 65],
    (2, 6): [146, 118, 102, 96, 98, 106], (2, 7): [231, 191, 165, 151, 147, 151, 161],
    (3, 2): [17, 15, 19], (3, 3): [48, 39, 38, 39, 48], (3, 4): [106, 87, 78, 72, 74, 80, 94],
    (4, 3): [94, 80, 74, 72, 78, 87, 106], (3, 5): [200, 168, 148, 132, 126, 125, 130, 141, 160],
    (4, 4): [200, 172, 154, 141, 138, 138, 141, 154, 172, 200],
}


def profile(F, n, lo, hi):
    """V(q), q = 1..n: order of the Schur coefficients when q near roots collide, window [lo, hi]."""
    E = list(range(lo, hi + 1))
    out = []
    for q in range(1, n + 1):
        L = sorted(b - i for b in range(q) for i in range(F))
        C = E[: F * q]
        out.append(sum(max(0, c - l) for c, l in zip(C, L)))
    return out


def least(V, parts):
    """Componentwise smallest partition (parts entries, bottom first) with bottom sums >= V; returns (size, weight)."""
    d, R, prev = [], 0, 0
    for q in range(1, parts + 1):
        dq = max(prev, V[q - 1] - R)
        d.append(dq)
        R += dq
        prev = dq
    nu = list(reversed(d))  # nu[0] is the top part
    return R, sum((j + 1) * x for j, x in enumerate(nu))


def predict(F, n, p):
    q = F * n - 1 - p
    Vt = profile(F, n, -p, q)
    Vs = profile(n, F, -q, p)
    Rn, wn = least(Vt, n)
    Rk, wk = least(Vs, F)
    SE = sum(range(-p, q + 1))
    D0 = SE - F * comb(n, 2) + n * comb(F, 2)
    k = max(Rk, Rn - D0)
    w = wk + (k - Rk) + wn + (k + D0 - Rn)
    return n * comb(F + 1, 3) + F * comb(n + 1, 3) + w


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out")
    a = ap.parse_args()
    lines = []
    for (F, n), vals in MEASURED.items():
        preds = [predict(F, n, p) for p in range(F - 1, F * n - n + 1)]
        ok = preds == vals
        lines.append(f"{F}x{n}: predicted {preds}, measured {vals}" + ("  [equal]" if ok else "  [DIFFER]"))
    text = "\n".join(lines)
    print(text)
    if a.out:
        open(a.out, "w").write(text + "\n")


if __name__ == "__main__":
    main()
