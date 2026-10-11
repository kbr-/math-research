#!/usr/bin/env python3
"""Numerical control of the pair-atom statements of entry-2026-10-11-pair-atom-spectrum.

Tested statements, flat window phi = 1 on [-Lam/2, Lam/2], grid alpha_k = 2 pi k / Lam (k in Z),
v_z = (phihat(z - alpha_k))_k with phihat(w) = 2 sin(w Lam / 2) / w, normalized by Lam^2:

1. Bilinear Gram: v_z^T v_w / Lam^2 = sinc((z - w) Lam / 2), sinc(x) = sin(x) / x, also at
   complex arguments. In particular v^T v / Lam^2 = 1 and v^* v / Lam^2 = kappa =
   sinh(delta Lam) / (delta Lam) for z = gamma - i delta.
2. Pair atom: (v v^T + conj(v) conj(v)^T) / Lam^2 has nonzero eigenvalues kappa + 1, -(kappa - 1).
3. Solitary amplification: adding real points (on-line zeros) keeps lambda_max >= kappa + 1.
4. Two-pair identity: for z0 = -i delta, z1 = t - i delta and their conjugates,
   ||G||_HS^2 = 4 + 4 kappa^2 + 4 sinc^2(t Lam / 2) + 4 Re sinc^2((t + 2 i delta) Lam / 2);
   at t Lam = pi, with a = pi/2 and b = delta Lam, this equals
   4 + 16/pi^2 + 4 kappa^2 (3 a^2 b^2 + a^4)/(b^2 + a^2)^2 - 4 (b^2 - a^2)/(b^2 + a^2)^2
   <= 4 + 16/pi^2 + 3 pi^2 kappa^2 / b^2 (cancellation of the kappa^2 terms);
   at t Lam = 2 pi the terms reinforce (negative control, compared only for b >= 4).

The grid is truncated at |k| <= K; the flat window's tail is O(1/K) relative, which the
tolerances below allow for. Hypotheses (conjugation-closed point sets, delta > 0) are asserted.
"""
import argparse
import json

import numpy as np


def vec(z, lam, kmax):
    alpha = 2 * np.pi * np.arange(-kmax, kmax + 1) / lam
    w = z - alpha
    return 2 * np.sin(w * lam / 2) / w


def sinc(x):
    return np.sin(x) / x


def spectrum(points, lam, kmax):
    """Nonzero eigenvalues and HS norm squared of G = sum v v^T / Lam^2 over the point list."""
    pts = np.array(points, dtype=complex)
    conj_closed = all(np.min(np.abs(pts - np.conj(p))) < 1e-12 for p in pts)
    assert conj_closed, "point set must be closed under conjugation"
    v = np.stack([vec(p, lam, kmax) for p in pts], axis=1)
    gram = v.T @ v / lam**2  # bilinear Gram; shares nonzero eigenvalues with G = V V^T
    eig = np.linalg.eigvals(gram)
    assert np.max(np.abs(eig.imag)) < 1e-6 * max(1.0, np.max(np.abs(eig))), "G is real symmetric"
    return np.sort(eig.real), float(np.sum(gram * gram).real), gram


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--kmax", type=int, default=400000)
    args = ap.parse_args()
    rng = np.random.default_rng(20261011)
    rows = []
    ok = True
    for lam, delta in [(8.0, 0.25), (12.0, 0.4), (20.0, 0.3), (30.0, 0.15)]:
        assert delta > 0
        b = delta * lam
        kappa = np.sinh(b) / b
        tol = 2e-3 * (kappa + 1)
        gamma = 0.37
        z = gamma - 1j * delta
        eig, hs, gram = spectrum([z, np.conj(z)], lam, args.kmax)
        row = {"Lam": lam, "delta": delta, "kappa": kappa,
               "vTv": float(gram[0, 0].real), "vHv": float(gram[0, 1].real),
               "atom_eigs": eig.tolist(), "atom_pred": [-(kappa - 1), kappa + 1]}
        ok &= abs(gram[0, 0] - 1) < 2e-3 and abs(gram[0, 1] - kappa) < tol
        ok &= abs(eig[0] + (kappa - 1)) < tol and abs(eig[1] - (kappa + 1)) < tol
        # bilinear Gram at a generic complex difference
        w = 1.3 + 0.2j
        g01 = (vec(z, lam, args.kmax) @ vec(w, lam, args.kmax)) / lam**2
        pred = sinc((z - w) * lam / 2)
        row["gram_generic_err"] = float(abs(g01 - pred))
        ok &= abs(g01 - pred) < 2e-3 * max(1.0, abs(pred))
        # solitary amplification with 40 random real points nearby
        reals = list(rng.uniform(-10, 10, size=40))
        eig_s, _, _ = spectrum([z, np.conj(z)] + reals, lam, args.kmax)
        row["solitary_lambda_max"] = float(eig_s[-1])
        row["solitary_bound"] = kappa + 1
        ok &= eig_s[-1] >= kappa + 1 - tol
        # two-pair identity, cancellation at t Lam = pi and control at t Lam = 2 pi
        for name, tl in [("cancel_pi", np.pi), ("control_2pi", 2 * np.pi)]:
            t = tl / lam
            z1 = t - 1j * delta
            _, hs2, _ = spectrum([-1j * delta, 1j * delta, z1, np.conj(z1)], lam, args.kmax)
            formula = (4 + 4 * kappa**2 + 4 * sinc(t * lam / 2) ** 2
                       + 4 * (sinc((t + 2j * delta) * lam / 2) ** 2).real)
            row[name] = {"hs_numeric": hs2, "hs_formula": float(formula),
                         "ratio_to_4kappa2": float(formula / (4 * kappa**2))}
            ok &= abs(hs2 - formula) < 4e-3 * (4 * kappa**2 + 8)
        # exact closed form at t Lam = pi, with a = pi / 2
        a2 = (np.pi / 2) ** 2
        closed = (4 + 16 / np.pi**2 + 4 * kappa**2 * (3 * a2 * b**2 + a2**2) / (b**2 + a2) ** 2
                  - 4 * (b**2 - a2) / (b**2 + a2) ** 2)
        row["cancel_pi"]["hs_closed_form"] = float(closed)
        ok &= abs(closed - row["cancel_pi"]["hs_formula"]) < 1e-9 * closed
        ok &= closed <= 4 + 16 / np.pi**2 + 3 * np.pi**2 * kappa**2 / b**2
        if b >= 4:  # the comparison is asymptotic in b = delta Lam; small b is not claimed
            ok &= row["cancel_pi"]["hs_formula"] < row["control_2pi"]["hs_formula"]
        rows.append(row)
    out = {"kmax": args.kmax, "seed": 20261011, "all_pass": bool(ok), "rows": rows}
    with open(args.out, "w") as f:
        json.dump(out, f, indent=1)
    print("all_pass", bool(ok))
    for r in rows:
        print(r["Lam"], r["delta"], "kappa %.6g" % r["kappa"], "eigs", r["atom_eigs"],
              "cancel ratio %.4g" % r["cancel_pi"]["ratio_to_4kappa2"],
              "control ratio %.4g" % r["control_2pi"]["ratio_to_4kappa2"])
    raise SystemExit(0 if ok else 1)


if __name__ == "__main__":
    main()
