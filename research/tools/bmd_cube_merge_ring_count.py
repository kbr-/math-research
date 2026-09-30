#!/usr/bin/env python3
"""Ring count of a single merge (cycle bmd-20261001-v).

Exponent sets (consecutive within each character, generic points) of V(n; p_0; p_1..p_k), d = 2 + C + kn + binom(k,2),
C = binom(n,2), B = binom(d,2):
  at a single p_j: half-integral 1/2 + {0..n+k-2}; integral 0..d-n-k;
  at p_0: half-integral 1/2-(n-1) + {0..kn-1}; integral -C..1+binom(k,2);
  at infinity: not assumed; T below is the sum of E_x - B over all non-branch points, infinity included
  (which contributes negatively, since z has a pole there).
Far space F(n,k) at w = infinity (thm:cube-merge-far-count): integral -(1+P)..C+n, half -(k-2)n-1/2 .. n+k-5/2.
Hurwitz in the near chart at p_0 (near limit V(n+1; p_0; p_2..p_k)) and in the far chart at w = infinity give
  ring1 = (E_p0(n+1,k-1) - B) - (E_p0(n,k) - B) - (E_p1(n,k) - B) - far(n,k)
  ring2 = (E_inf(F(n,k)) - B) - (k-1) (E_pj(n,k) - B) - T(n+1,k-1)
(roots strictly between the far scale |z-p_0| ~ eps and the near scale).  Also the total weight
  T(n,k) = (k-1) B - E_p0 - k E_pj, and T(n,k) - T(n+1,k-1) - far(n,k) = ring.
The script checks ring1 = ring2 = T(n,k) - T(n+1,k-1) - far(n,k) symbolically and factors the ring count.
"""
import argparse

import sympy as sp

n, k, i = sp.symbols("n k i", integer=True, positive=True)
half = sp.Rational(1, 2)


def s(a, b):
    return sp.summation(i, (i, a, b))


def dims(nn, kk):
    C = nn * (nn - 1) / 2
    return C, 2 + C + kk * nn + kk * (kk - 1) / 2


def e_single(nn, kk):
    C, d = dims(nn, kk)
    return s(0, d - nn - kk) + sp.summation(half + i, (i, 0, nn + kk - 2))


def e_p0(nn, kk):
    C, d = dims(nn, kk)
    return s(-C, 1 + kk * (kk - 1) / 2) + sp.summation(half - (nn - 1) + i, (i, 0, kk * nn - 1))


def total(nn, kk):
    C, d = dims(nn, kk)
    B = d * (d - 1) / 2
    return (kk - 1) * B - e_p0(nn, kk) - kk * e_single(nn, kk)


def far_count(nn, kk):
    return (kk - 1) * ((3 * nn - 2) * kk + nn ** 2 - 7 * nn + 4) / 2


def far_einf(nn, kk):
    C = nn * (nn - 1) / 2
    P = (kk - 1) * (kk - 2) / 2
    return s(-(1 + P), C + nn) + sp.summation(-(kk - 2) * nn - half + i, (i, 0, (kk - 1) * nn + kk - 2))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    C, d = dims(n, k)
    B = d * (d - 1) / 2
    ring1 = sp.expand((e_p0(n + 1, k - 1) - B) - (e_p0(n, k) - B) - (e_single(n, k) - B) - far_count(n, k))
    # in the far chart w = infinity absorbs every root at scale >> eps: the rings, the points p_2..p_k (forced
    # orders) and all non-branch points of the near limit V(n+1; p_0; p_2..p_k), T(n+1,k-1) of them
    ring2 = sp.expand((far_einf(n, k) - B) - (k - 1) * (e_single(n, k) - B) - total(n + 1, k - 1))
    ring3 = sp.expand(total(n, k) - total(n + 1, k - 1) - far_count(n, k))
    lines = [
        f"total weight T(n,k) = {sp.factor(sp.expand(total(n, k)))}",
        f"ring count (near chart) = {sp.factor(ring1)}",
        f"ring count (far chart)  = {sp.factor(ring2)}",
        f"T(n,k) - T(n+1,k-1) - far = {sp.factor(ring3)}",
        f"near = far: {sp.simplify(ring1 - ring2) == 0}; near = identity: {sp.simplify(ring1 - ring3) == 0}",
        "values (n,k): " + ", ".join(f"({a},{b}):{ring1.subs({n: a, k: b})}" for a in range(1, 6) for b in range(2, 7)),
    ]
    open(a.out, "w").write("\n".join(lines) + "\n")
    print("\n".join(lines))


if __name__ == "__main__":
    main()
