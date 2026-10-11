#!/usr/bin/env python3
"""Numerical control of the many-pair statements of entry-2026-10-11-many-pair-bound.

Flat window on [-Lam/2, Lam/2], grid 2 pi k / Lam cut at |k| <= K, v_z(k) = 2 sin(w Lam/2)/w with
w = z - alpha_k, normalization Lam^2.  Off-axis points z_j = gamma_j - i delta_j (delta_j > 0,
distinct), multiplicities m_j >= 1, B = sum_j m_j (v_j v_j^T + conj) / Lam^2, G = B + on-line atoms.
With h_jl = sinc((z_j - conj z_l) Lam/2), kappa_j = h_jj, R_jl = h_jl^2/(kappa_j kappa_l),
rho = lambda_min(R), g_jl = sinc((z_j - z_l) Lam/2):

1. ||B||_HS^2 = 2 sum m_j m_l h_jl^2 + 2 Re sum m_j m_l g_jl^2  (identity);
2. R is Hermitian positive semidefinite with unit diagonal;
3. ||B||_HS^2 >= 2 rho sum m_j^2 kappa_j^2 - sum m_j m_l (1 + kappa(delta_j - delta_l));
4. lambda_max(G) >= lambda_max(B) >= ||B||_HS / (2n)^(3/2);
5. separated case: if all delta_j Lam >= 1, delta_j <= Delta and heights are tau-separated with
   tau >= 8 Delta, then |R_jl| <= (7/4)/(1 + t^2/(delta_j+delta_l)^2) and rho >= 3/5.

6. for the whole configuration Z (off-axis pairs and real points), ||G||_HS^2 =
   Lam^-2 int_{-Lam}^{Lam} (Lam - |s|) |S_Z(s)|^2 ds with S_Z(s) = sum_{z in Z} m_z e^{-isz}
   (trapezoid rule on 400001 nodes against the grid sum);
7. for the real points alone, with at most M_loc of them in each cell of length 2 pi/Lam starting
   at the smallest and K cells, lambda_max(P) <= M_loc (3 + (2/pi)(1 + ln K)).

Configurations: clustered (heights within a window of width about delta) and separated; the
clustered ones are where rho is small, the separated ones where item 5 applies.  Hypotheses are
asserted in code.  The grid truncation error is O(1/K) relative and the tolerances allow for it.
"""
import argparse
import json

import numpy as np


def vec(z, lam, kmax):
    alpha = 2 * np.pi * np.arange(-kmax, kmax + 1) / lam
    w = z - alpha
    return 2 * np.sin(w * lam / 2) / w


def sinc(x):
    x = np.asarray(x, dtype=complex)
    out = np.ones_like(x)
    nz = np.abs(x) > 1e-14
    out[nz] = np.sin(x[nz]) / x[nz]
    return out


def kappa(d, lam):
    b = abs(d) * lam
    return 1.0 if b < 1e-12 else float(np.sinh(b) / b)


def case(name, gam, dlt, mult, reals, lam, kmax, separated=None):
    gam, dlt, mult = np.array(gam, float), np.array(dlt, float), np.array(mult, float)
    n = len(gam)
    assert np.all(dlt > 0) and np.all(mult >= 1)
    z = gam - 1j * dlt
    assert len(set(np.round(z, 12))) == n, "points must be distinct"
    h = sinc((z[:, None] - np.conj(z)[None, :]) * lam / 2)
    g = sinc((z[:, None] - z[None, :]) * lam / 2)
    kap = h.diagonal().real
    R = h**2 / np.outer(kap, kap)
    assert np.max(np.abs(R - R.conj().T)) < 1e-9
    evR = np.linalg.eigvalsh((R + R.conj().T) / 2)
    rho = float(evR[0])
    mm = np.outer(mult, mult)
    hs_formula = float((2 * np.sum(mm * h**2) + 2 * np.sum(mm * g**2)).real)
    kd = np.array([[kappa(dlt[j] - dlt[l], lam) for l in range(n)] for j in range(n)])
    lower = 2 * rho * float(np.sum(mult**2 * kap**2)) - float(np.sum(mm * (1 + kd)))
    # spectrum from grid vectors
    pts = np.concatenate([z, np.conj(z)])
    wts = np.concatenate([mult, mult])
    V = np.stack([vec(p, lam, kmax) for p in pts], axis=1)
    gramB = (V.T @ V) / lam**2 * wts[None, :]  # eigenvalues of V W V^T = those of V^T V W
    evB = np.linalg.eigvals(gramB).real
    hs_grid = float(np.sum((np.sqrt(wts)[:, None] * (V.T @ V) / lam**2 * np.sqrt(wts)[None, :]) ** 2).real)
    lamB = float(np.max(evB))
    Vall = np.stack([vec(p, lam, kmax) for p in pts] + [vec(complex(p), lam, kmax) for p in reals], axis=1)
    wall = np.concatenate([wts, np.ones(len(reals))])
    evG = np.linalg.eigvals((Vall.T @ Vall) / lam**2 * wall[None, :]).real
    lamG = float(np.max(evG))
    # item 6: ||G||_HS^2 = Lam^-2 int_{-Lam}^{Lam} (Lam - |s|) |S_Z(s)|^2 ds, S_Z(s) = sum m_z e^{-isz}
    allpts = np.concatenate([pts, np.array(reals, dtype=complex)])
    gramG = (Vall.T @ Vall) / lam**2
    hsG_grid = float(np.sum(np.outer(wall, wall) * gramG**2).real)
    s = np.linspace(-lam, lam, 400001)
    S = (wall[:, None] * np.exp(-1j * allpts[:, None] * s[None, :])).sum(axis=0)
    f = (lam - np.abs(s)) * np.abs(S) ** 2
    hsG_quad = float((f[:-1] + f[1:]).sum() * (s[1] - s[0]) / 2 / lam**2)
    # item 7: on-line part alone, lambda_max(P) <= M_loc (3 + (2/pi)(1 + ln K))
    if len(reals):
        r = np.sort(np.array(reals, float))
        cell = 2 * np.pi / lam
        idx = np.floor((r - r[0]) / cell).astype(int)
        m_loc = int(np.bincount(idx).max())
        kcells = int(idx.max()) + 1
        Vr = Vall[:, len(pts):]
        lamP = float(np.max(np.linalg.eigvalsh((Vr.T @ Vr).real / lam**2)))
        schur = m_loc * (3 + (2 / np.pi) * (1 + np.log(kcells)))
    scale = max(1.0, hs_formula)
    checks = {
        "second_moment_identity": abs(hsG_grid - hsG_quad) < 5e-3 * max(1.0, hsG_quad),
        **({"online_schur_bound": lamP <= schur * (1 + 5e-3)} if len(reals) else {}),
        "identity": abs(hs_grid - hs_formula) < 5e-3 * scale + 1e-2,
        "R_psd_unit_diag": rho > -1e-9 and np.max(np.abs(R.diagonal() - 1)) < 1e-9,
        "hs_lower_bound": hs_formula >= lower - 1e-9 * scale,
        "lambda_chain": lamG >= lamB - 5e-3 * max(1.0, lamB)
        and lamB >= np.sqrt(max(hs_formula, 0.0)) / (2 * n) ** 1.5 - 5e-3 * max(1.0, lamB),
    }
    row = {"name": name, "n": n, "Lam": lam, "rho": rho, "kappa_max": float(kap.max()),
           "hs_formula": hs_formula, "hs_grid": hs_grid, "hs_lower_bound": lower,
           "lambda_max_B": lamB, "lambda_max_G": lamG,
           "hs_over_sum_kappa2": hs_formula / float(2 * np.sum(mult**2 * kap**2)),
           "hsG_grid": hsG_grid, "hsG_quadrature": hsG_quad}
    if len(reals):
        row.update({"lambda_max_P": lamP, "online_schur_bound": float(schur), "M_loc": m_loc, "cells": kcells})
    if separated is not None:
        Delta, tau = separated
        assert np.all(dlt * lam >= 1) and np.all(dlt <= Delta) and tau >= 8 * Delta
        gs = np.sort(gam)
        assert np.all(np.diff(gs) >= tau - 1e-12)
        t = gam[:, None] - gam[None, :]
        s = dlt[:, None] + dlt[None, :]
        bound = 1.75 / (1 + t**2 / s**2)
        off = ~np.eye(n, dtype=bool)
        checks["separated_entry_bound"] = bool(np.all(np.abs(R)[off] <= bound[off] + 1e-12))
        checks["separated_rho"] = rho >= 0.6
        M, ks = float(mult.sum()), float(kap.max())
        row["corollary_applies"] = bool(ks >= 5 * M**2 + 1)
        if row["corollary_applies"]:
            checks["corollary"] = lamG >= ks / (2 * n) ** 1.5 * (1 - 5e-3)
    row["checks"] = {k: bool(v) for k, v in checks.items()}
    return row


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--kmax", type=int, default=50000)
    args = ap.parse_args()
    rng = np.random.default_rng(2026101102)
    rows = []
    lam = 24.0
    # clustered: heights inside a window of width about delta
    for n in (2, 3, 5, 8):
        for rep in range(3):
            dlt = rng.uniform(0.2, 0.45, size=n)
            gam = rng.uniform(0.0, 0.4, size=n)
            mult = rng.integers(1, 3, size=n)
            reals = rng.uniform(-6, 6, size=30)
            rows.append(case(f"cluster_n{n}_{rep}", gam, dlt, mult, reals, lam, args.kmax))
    # equally spaced equal-delta clusters at step pi/Lam (the resonant spacing)
    for n in (2, 3, 4, 6):
        gam = np.arange(n) * np.pi / lam
        rows.append(case(f"resonant_n{n}", gam, np.full(n, 0.35), np.ones(n), [], lam, args.kmax))
    # separated: Delta = 0.45, tau = 4 >= 8 Delta
    for n in (2, 4, 8):
        for rep in range(2):
            dlt = rng.uniform(0.3, 0.45, size=n)
            gam = np.cumsum(rng.uniform(4.0, 6.0, size=n))
            mult = np.ones(n)
            reals = rng.uniform(0, gam[-1] + 4, size=40)
            rows.append(case(f"separated_n{n}_{rep}", gam, dlt, mult, reals, lam, args.kmax,
                             separated=(0.45, 4.0)))
    ok = all(all(r["checks"].values()) for r in rows)
    with open(args.out, "w") as f:
        json.dump({"kmax": args.kmax, "seed": 2026101102, "all_pass": ok, "rows": rows}, f, indent=1)
    print("all_pass", ok)
    for r in rows:
        bad = [k for k, v in r["checks"].items() if not v]
        print(f'{r["name"]:18s} rho {r["rho"]:.3e} kmax {r["kappa_max"]:.4g} hs {r["hs_formula"]:.5g} '
              f'lower {r["hs_lower_bound"]:.5g} lamB {r["lambda_max_B"]:.5g} lamG {r["lambda_max_G"]:.5g} '
              f'ratio {r["hs_over_sum_kappa2"]:.3e} {"FAIL " + ",".join(bad) if bad else ""}')
    raise SystemExit(0 if ok else 1)


if __name__ == "__main__":
    main()
