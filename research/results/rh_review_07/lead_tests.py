#!/usr/bin/env python3
"""Cheap tests of two items of the route review entry-2026-10-11-exclusion-route-review.

Test A (Hermite-Biehler lead).  Statement tested: for a real polynomial p with simple roots, all zeros of
p + i p' lie in the open lower half-plane when all roots of p are real, and some zero of p + i p' lies in
the closed upper half-plane when p has a pair of non-real roots.  Inputs: 200 random real-rooted
polynomials of degree 3..8 and 200 obtained from them by moving two roots to a conjugate pair.  A sign
error in the criterion or a failure of the "only if" direction on these samples shows as a count below 200.

Test B (harmonic-inversion bridge).  Statement tested: the exponents of S(s) = sum_w m_w e^{-i s w} over a
conjugation-closed set of n off-axis pairs (2n exponentials) are recovered by the matrix-pencil (Prony)
method from 4n equally spaced samples on a time span far shorter than 2 pi / (least height gap), exactly
in the noiseless case and with an error that grows quickly with n when relative noise 1e-9 is added.
The recovered quantity reported is the largest error in delta_j = |Im w|.  This tests whether the
structure of the signal can resolve a cluster that a mean square at one bandwidth cannot; it says nothing
about where the samples would come from.
"""
import argparse
import json

import numpy as np


def hb_test(rng, trials=200):
    real_ok = pair_ok = 0
    for _ in range(trials):
        deg = int(rng.integers(3, 9))
        roots = np.sort(rng.uniform(-3, 3, size=deg))
        assert np.min(np.diff(roots)) > 1e-6
        p = np.poly(roots)
        z = np.roots(np.polyadd(p, 1j * np.polyder(p)))
        real_ok += bool(np.all(z.imag < -1e-10))
        c = roots.astype(complex)
        mid, half = (roots[0] + roots[1]) / 2, rng.uniform(0.05, 1.0)
        c[0], c[1] = mid + 1j * half, mid - 1j * half
        q = np.poly(c).real
        zq = np.roots(np.polyadd(q, 1j * np.polyder(q)))
        pair_ok += bool(np.any(zq.imag > -1e-10))
    return {"trials": trials, "real_rooted_all_zeros_lower": real_ok, "with_pair_some_zero_not_lower": pair_ok}


def pencil(samples, order):
    m = len(samples) - order
    h0 = np.array([[samples[i + j] for j in range(order)] for i in range(m)])
    h1 = np.array([[samples[i + j + 1] for j in range(order)] for i in range(m)])
    return np.linalg.eigvals(np.linalg.pinv(h0) @ h1)


def inversion_test(rng):
    rows = []
    for n in (1, 2, 3, 4):
        gam = np.cumsum(rng.uniform(0.15, 0.3, size=n))
        dlt = rng.uniform(0.2, 0.45, size=n)
        w = np.concatenate([gam - 1j * dlt, gam + 1j * dlt])
        step = 0.5
        s = step * np.arange(4 * n)
        clean = np.exp(-1j * np.outer(s, w)).sum(axis=1)
        row = {"n": n, "span": float(s[-1]), "fourier_resolution": float(2 * np.pi / np.min(np.diff(gam))) if n > 1 else None}
        for label, sig in (("noiseless", clean),
                           ("noise_1e-9", clean * (1 + 1e-9 * rng.standard_normal(len(s))))):
            mu = pencil(sig, 2 * n)
            west = 1j * np.log(mu) / step
            err = max(float(np.min(np.abs(np.abs(west.imag) - d))) for d in dlt)
            row[label + "_max_delta_error"] = err
        rows.append(row)
    return rows


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    args = ap.parse_args()
    rng = np.random.default_rng(2026101107)
    out = {"seed": 2026101107, "hermite_biehler": hb_test(rng), "harmonic_inversion": inversion_test(rng)}
    with open(args.out, "w") as f:
        json.dump(out, f, indent=1)
    print(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()
