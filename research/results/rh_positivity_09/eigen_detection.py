#!/usr/bin/env python3
"""Numerical control of the statement of entry-2026-10-11-extreme-eigenvalue-detection.

Flat window on [-Lam/2, Lam/2], grid 2 pi k / Lam cut at |k| <= K, normalization Lam^2.  Configuration: one
off-axis pair z, conj z (z = gamma - i delta, multiplicity 1) and real points with multiplicities one.
G = G_on + B.  Tested statement (prop:extreme-eigenvalue-detection, solitary case):
    kappa + 1 <= lambda_max(G) <= kappa + 1 + lambda_max(G_on),
    -(kappa - 1) <= lambda_min(G) <= -(kappa - 1) + lambda_max(G_on),
with kappa = sinh(b)/b, b = delta Lam, and lambda_max(G_on) <= M_loc (3 + (2/pi)(1 + ln K_cells))
(lem:real-configuration-bound).  The real points are placed at density D per unit height around gamma, for
ratios theta = (Lam / 2 pi) / D of grid density to point density both below and above one, so that the
control covers the case where the real points outnumber the grid points near gamma.  All four inequalities
are equalities up to lambda_max(G_on), so a wrong sign or a missing term shows as a violation; the reported
slack is how far inside the interval the eigenvalue sits.  Truncation of the grid is O(1/K) relative.
"""
import argparse
import json

import numpy as np


def vec(z, lam, kmax):
    alpha = 2 * np.pi * np.arange(-kmax, kmax + 1) / lam
    w = z - alpha
    return 2 * np.sin(w * lam / 2) / w


def case(rng, lam, delta, theta, kmax, span=12.0):
    gamma = 0.31
    dens = lam / (2 * np.pi) / theta
    nreal = max(1, int(round(dens * 2 * span)))
    reals = np.sort(rng.uniform(gamma - span, gamma + span, size=nreal))
    z = gamma - 1j * delta
    pts = [z, np.conj(z)] + [complex(r) for r in reals]
    V = np.stack([vec(p, lam, kmax) for p in pts], axis=1)
    gram = (V.T @ V) / lam**2
    ev = np.linalg.eigvals(gram).real
    gon = (V[:, 2:].T @ V[:, 2:]).real / lam**2
    lam_on = float(np.max(np.linalg.eigvalsh(gon)))
    b = delta * lam
    kappa = float(np.sinh(b) / b)
    cell = 2 * np.pi / lam
    idx = np.floor((reals - reals[0]) / cell).astype(int)
    schur = int(np.bincount(idx).max()) * (3 + (2 / np.pi) * (1 + np.log(int(idx.max()) + 1)))
    lmax, lmin = float(ev.max()), float(ev.min())
    tol = 2e-4 * (kappa + 1) + 1e-3  # grid truncation is O(1/K) relative with K = 3e4; below lam_on at every row
    ok = (kappa + 1 - tol <= lmax <= kappa + 1 + lam_on + tol
          and -(kappa - 1) - tol <= lmin <= -(kappa - 1) + lam_on + tol and lam_on <= schur * (1 + 5e-3))
    return {"Lam": lam, "delta": delta, "theta": theta, "n_real": nreal, "kappa": kappa, "lambda_max": lmax,
            "lambda_min": lmin, "lambda_max_on": lam_on, "schur_bound": float(schur),
            "lmax_minus_kappa_plus_1": lmax - (kappa + 1), "lmin_plus_kappa_minus_1": lmin + (kappa - 1),
            "pass": bool(ok)}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--kmax", type=int, default=30000)
    args = ap.parse_args()
    rng = np.random.default_rng(2026101109)
    rows = [case(rng, lam, delta, theta, args.kmax)
            for lam in (16.0, 24.0) for delta in (0.1, 0.25, 0.45) for theta in (0.5, 1.0, 2.0)]
    ok = all(r["pass"] for r in rows)
    with open(args.out, "w") as f:
        json.dump({"seed": 2026101109, "kmax": args.kmax, "all_pass": ok, "rows": rows}, f, indent=1)
    print("all_pass", ok)
    for r in rows:
        print(f'Lam {r["Lam"]:.0f} delta {r["delta"]} theta {r["theta"]} n_real {r["n_real"]} kappa {r["kappa"]:.4g} '
              f'lmax-(k+1) {r["lmax_minus_kappa_plus_1"]:.4g} lmin+(k-1) {r["lmin_plus_kappa_minus_1"]:.4g} '
              f'lam_on {r["lambda_max_on"]:.4g} schur {r["schur_bound"]:.4g} {"" if r["pass"] else "FAIL"}')
    raise SystemExit(0 if ok else 1)


if __name__ == "__main__":
    main()
