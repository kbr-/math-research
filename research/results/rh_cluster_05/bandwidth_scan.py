#!/usr/bin/env python3
"""Numerical control of the two statements of entry-2026-10-11-resonance-free-bandwidth.

Flat window, complete grid.  For off-axis points z_j = gamma_j - i delta_j (distinct heights, min gap g),
multiplicities m_j, M = sum m_j, delta_* = max delta_j attained by a pair of multiplicity m_*, the off-axis
part B_Lam of the Gram form at bandwidth Lam has (registered norm identity, prop:many-pair-norm-bound)
    ||B_Lam||_HS^2 = 2 sum m_j m_l sinc((z_j - conj z_l) Lam/2)^2 + 2 Re sum m_j m_l sinc((z_j - z_l) Lam/2)^2.

1. Subset-sum resonance: equal delta, n = 2^k simple points at heights sum_{i in S} q_i pi / Lam0 (q_i odd,
   distinct subset sums), b = delta Lam0:
       ||B_Lam0||_HS^2 <= (e^{2b} / (2 b^2)) (2k+1)! prod_i (q_i pi / (2b))^2 + 3 n^2.
2. Resonance-free bandwidth: for Lam1 >= 1/delta_* and H >= 4 M^2 / (g m_*^2) (any H >= 0 when n = 1),
   some Lam in [Lam1, Lam1 + H] has ||B_Lam||_HS >= (sqrt(2)/2) m_* kappa_Lam(delta_*) - M,
   kappa_Lam(d) = sinh(d Lam)/(d Lam).

For 2 the scan takes 4001 values of Lam in the interval and reports the largest value of
(||B_Lam||_HS - ((sqrt 2 / 2) m_* kappa - M)) e^{-delta_* Lam}, the scaling avoiding overflow; the statement predicts a positive maximum (a grid can only miss a
maximum, so a positive grid maximum confirms existence; a negative one would not refute it).  The minimum of
the ratio ||B_Lam||_HS / (m_* kappa) over the scan is reported to show that resonances do occur inside the
interval.  Hypotheses are asserted in code.
"""
import argparse
import json
from itertools import combinations
from math import factorial

import numpy as np


def sinc(x):
    x = np.asarray(x, dtype=complex)
    out = np.ones_like(x)
    nz = np.abs(x) > 1e-14
    out[nz] = np.sin(x[nz]) / x[nz]
    return out


def hs2(gam, dlt, mult, lams):
    """||B_Lam||_HS^2 for each Lam in lams (closed form)."""
    z = gam - 1j * dlt
    dh = z[:, None] - np.conj(z)[None, :]
    dg = z[:, None] - z[None, :]
    mm = np.outer(mult, mult)
    out = np.empty(len(lams))
    for i, lam in enumerate(lams):
        out[i] = (2 * np.sum(mm * sinc(dh * lam / 2) ** 2) + 2 * np.sum(mm * sinc(dg * lam / 2) ** 2)).real
    return out


def kappa(d, lam):
    return np.sinh(d * lam) / (d * lam)


def scaled_norm(gam, dlt, mult, lams):
    """||B_Lam||_HS e^{-c} with c = delta_* Lam, computed without overflow: sin(x) e^{-c} is formed from
    exponentials whose exponents have real part <= 0, since |Im x| <= c for every argument that occurs."""
    z = gam - 1j * dlt
    dh = z[:, None] - np.conj(z)[None, :]
    dg = z[:, None] - z[None, :]
    mm = np.outer(mult, mult)
    dstar = float(np.max(dlt))
    out = np.empty(len(lams))
    for i, lam in enumerate(lams):
        c = dstar * lam
        total = 0.0
        for d in (dh, dg):
            x = d * lam / 2
            small = np.abs(x) < 1e-14
            xs = np.where(small, 1.0, x)
            s = (np.exp(1j * xs - c) - np.exp(-1j * xs - c)) / (2j * xs)
            s = np.where(small, np.exp(-c), s)
            total += 2 * np.sum(mm * s**2).real
        out[i] = np.sqrt(max(total, 0.0))
    return out


def scaled_kappa(d, lam):
    """kappa_Lam(d) e^{-d Lam}."""
    c = d * lam
    return (1 - np.exp(-2 * c)) / (2 * c)


def subset_family(k, delta, lam0):
    q = [3**i for i in range(k)]
    heights = sorted({sum(c) * np.pi / lam0 for r in range(k + 1) for c in combinations(q, r)})
    assert len(heights) == 2**k
    return q, np.array(heights)


def scan(name, gam, dlt, mult, lam1, npts=4001):
    gam, dlt, mult = np.array(gam, float), np.array(dlt, float), np.array(mult, float)
    n = len(gam)
    assert np.all(dlt > 0) and np.all(mult >= 1)
    M = float(mult.sum())
    js = int(np.argmax(dlt))
    dstar, mstar = float(dlt[js]), float(mult[js])
    assert lam1 >= 1 / dstar
    if n > 1:
        gs = np.sort(gam)
        g = float(np.min(np.diff(gs)))
        assert g > 0, "heights must be distinct"
        H = 4 * M**2 / (g * mstar**2)
    else:
        g, H = float("inf"), 0.0
    lams = np.linspace(lam1, lam1 + H, npts) if H > 0 else np.array([lam1])
    # everything below is multiplied by e^{-delta_* Lam}, which does not change the sign of the margin
    norm = scaled_norm(gam, dlt, mult, lams)
    target = (np.sqrt(2) / 2) * mstar * scaled_kappa(dstar, lams) - M * np.exp(-dstar * lams)
    margin = norm - target
    ratio = norm / (mstar * scaled_kappa(dstar, lams))
    i = int(np.argmax(margin))
    return {"name": name, "n": n, "M": M, "gap": g, "delta_star": dstar, "m_star": mstar, "Lam1": lam1, "H": H,
            "max_scaled_margin": float(margin[i]), "Lam_at_max": float(lams[i]),
            "ratio_at_max": float(ratio[i]), "min_ratio_in_scan": float(ratio.min()),
            "max_ratio_in_scan": float(ratio.max()), "pass": bool(margin[i] > 0)}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    args = ap.parse_args()
    rng = np.random.default_rng(2026101105)
    res, scans = [], []
    delta = 0.4
    for k, lam0 in [(1, 30.0), (2, 30.0), (2, 60.0), (3, 60.0), (3, 120.0)]:
        q, heights = subset_family(k, delta, lam0)
        n = 2**k
        b = delta * lam0
        val = float(hs2(heights, np.full(n, delta), np.ones(n), [lam0])[0])
        bound = np.exp(2 * b) / (2 * b**2) * factorial(2 * k + 1) * np.prod([(qi * np.pi / (2 * b)) ** 2 for qi in q]) + 3 * n**2
        free = 2 * n * kappa(delta, lam0) ** 2
        res.append({"k": k, "n": n, "Lam0": lam0, "b": b, "hs2": val, "bound": float(bound),
                    "ratio_to_2n_kappa2": val / free, "bound_ratio": float(bound / free), "pass": bool(val <= bound * (1 + 1e-9))})
        # the same family, scanned over bandwidths from Lam0 on
        scans.append(scan(f"subset_k{k}_Lam0_{int(lam0)}", heights, np.full(n, delta), np.ones(n), lam0))
    for n in (1, 2, 4, 8):
        for rep in range(3):
            dlt = rng.uniform(0.15, 0.45, size=n)
            gam = np.cumsum(rng.uniform(0.02, 0.2, size=n))
            mult = rng.integers(1, 3, size=n)
            scans.append(scan(f"cluster_n{n}_{rep}", gam, dlt, mult, lam1=max(20.0, 1 / dlt.max())))
    # near-equal delta: the top two within 1e-3
    for rep in range(3):
        n = 5
        dlt = np.concatenate([[0.4, 0.4 - 1e-3], rng.uniform(0.3, 0.399, size=n - 2)])
        gam = np.cumsum(rng.uniform(0.02, 0.1, size=n))
        scans.append(scan(f"near_equal_{rep}", gam, dlt, np.ones(n), lam1=25.0))
    ok = all(r["pass"] for r in res) and all(s["pass"] for s in scans)
    with open(args.out, "w") as f:
        json.dump({"seed": 2026101105, "all_pass": ok, "resonance": res, "scans": scans}, f, indent=1)
    print("all_pass", ok)
    for r in res:
        print(f'resonance k={r["k"]} Lam0={r["Lam0"]:.0f} b={r["b"]:.0f} ratio {r["ratio_to_2n_kappa2"]:.3e} bound ratio {r["bound_ratio"]:.3e} {"" if r["pass"] else "FAIL"}')
    for s in scans:
        print(f'{s["name"]:22s} n={s["n"]} H={s["H"]:.4g} max scaled margin {s["max_scaled_margin"]:.4g} ratio at max {s["ratio_at_max"]:.3f} '
              f'min ratio {s["min_ratio_in_scan"]:.3e} max ratio {s["max_ratio_in_scan"]:.3f} {"" if s["pass"] else "FAIL"}')
    raise SystemExit(0 if ok else 1)


if __name__ == "__main__":
    main()
