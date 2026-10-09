#!/usr/bin/env python3
"""Best-case budget of expansion-and-immunity degree bounds for parity-defined rows.

Heuristic first-moment evaluation, not a theorem and not an experiment.

Model.  n free variables; m rows, each a relation on k independent uniform linear
forms forbidding a fraction phi = 2^(-beta*k) of the 2^k value tuples.
  * Unsatisfiability by the first moment needs m = n*ln(2)/phi rows.
  * A set of r = rho*n rows has dependent forms with probability about 2^(k*r - n);
    rho is the largest value (grid 0.0005) with
        log2 binom(m, r) + k*r - n <= 0,
    so that below it every set of r rows is expected to have independent forms
    (ideal expansion c = s = k in the sense of Alekhnovich-Razborov, if their
    theorems extend from variables to linear forms, which is NOT established).
  * Immunity of a generic predicate with that forbidden fraction: l = lam*k with
    lam >= 1/2 the solution of H(lam) = 1 - beta (lam = 1 for a single forbidden
    tuple, beta = 1).  This is an asymptotic value in k.
Columns (all as fractions of n):
  rk       = rho*k               forms in the largest independent set of rows
  T313     = rho*k/2             Theorem 3.13 (single forbidden tuple only; beta = 1)
  T38      = rho*lam*k/4         Theorem 3.8 with s = c
  hyp_half = rho*lam*k/2         a hypothetical bound r*l/2
  hyp_full = rho*lam*k           a hypothetical bound r*l
The target of the route is 1/2.

Second table: the dimension-count ceiling for balanced generic predicates (beta = 0,
m about n rows) of width k = c*log2(n).  The degree-(alpha*n) multiples of one row
fill about 2^(-k*D(1/2 || alpha)) of the space, D the binary relative entropy, and the
count reaches the whole space when n * 2^(-k*D) = 1, i.e. D(1/2 || alpha) = 1/c:
    alpha(c) = 1/2 - sqrt(1 - 4^(-1/c))/2.
Heuristic (assumes the multiples are as independent as their number allows).
"""
from math import log, log2, sqrt


def H(x):
    if x <= 0 or x >= 1:
        return 0.0
    return -x * log2(x) - (1 - x) * log2(1 - x)


def lam_of(beta):
    if beta >= 1:
        return 1.0
    lo, hi = 0.5, 1.0
    for _ in range(60):
        mid = (lo + hi) / 2
        if H(mid) > 1 - beta:
            lo = mid
        else:
            hi = mid
    return (lo + hi) / 2


def rho_of(k, beta):
    mu = log(2) * 2 ** (beta * k)          # m / n
    best = 0.0
    rho = 0.0005
    while rho < min(mu, 1.0 / k):
        if mu * H(rho / mu) + k * rho - 1 <= 0:
            best = rho
        rho += 0.0005
    return best


if __name__ == "__main__":
    print("k beta m/n rk lam T313 T38 hyp_half hyp_full")
    for k in (3, 5, 10, 20, 40):
        for beta in (1.0, 0.5, 0.25, 0.1):
            rho = rho_of(k, beta)
            lam = lam_of(beta)
            rk = rho * k
            t313 = f"{rk / 2:.3f}" if beta >= 1 else "-"
            print(k, beta, f"{log(2) * 2 ** (beta * k):.2f}", f"{rk:.3f}", f"{lam:.3f}", t313,
                  f"{rk * lam / 4:.3f}", f"{rk * lam / 2:.3f}", f"{rk * lam:.3f}")
    print("c alpha_count_ceiling")
    for c in (1, 4, 16, 100, 1000):
        print(c, f"{0.5 - sqrt(1 - 4 ** (-1.0 / c)) / 2:.4f}")
