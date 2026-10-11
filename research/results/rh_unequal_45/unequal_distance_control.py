#!/usr/bin/env python3
"""Numerical control for entry complex-moment-order (flat window, complete grid, off-axis points at unequal distances).

Statements tested.  Points gamma_j - i delta_j, multiplicities m_j > 0, M = sum m_j, bandwidth Lam,
delta_* = max delta_j, b = delta_* Lam, eta_j = delta_* - delta_j >= 0,
vartheta_j = Lam (gamma_j - gamma_0) - i Lam eta_j, w_j = m_j e^{-eta_j Lam} e^{-i Lam gamma_j},
nu_r = sum_j w_j vartheta_j^r, k the least r with nu_r != 0.

 G (complex moment order)
    | sqrt2 b (2b)^k ||B_Lam||_HS e^{-b} - |nu_k| sqrt((2k+1)!)/k! |
        <= sqrt((2k+3)!)/((k+1)! 2b) * sum_j m_j e^{-eta_j Lam} |vartheta_j|^{k+1} (delta_*/delta_j)^{k+2}
           + sqrt2 b (2b)^k M e^{-b} + tail,          tail below 1e-9 for b >= 30.
 T (top sub-cluster)  with k, nu, c computed from the points at delta_* only (real theta_j):
    | sqrt2 b (2b)^k ||B_Lam||_HS e^{-b} - |nu_k| sqrt((2k+1)!)/k! |
        <= c sqrt((2k+3)!)/((k+1)! 2b) + (2b)^k sum_lower m_j (delta_*/delta_j) e^{-eta_j Lam}
           + sqrt2 b (2b)^k M e^{-b} + tail.
 H (collision order of the Gram matrix)  for n heights of span W and H_jl = 2/(2 delta + i (gamma_j - gamma_l))^3:
    lambda_min(H) <= (2n)! W^{2(n-1)} / (n ((n-1)!)^2 (2 delta)^{2n+1}).

||B_Lam||_HS is the registered closed form (research/results/rh_cluster_05/bandwidth_scan.py, which allows unequal
distances); it uses nothing proved in the entry.  lambda_min is computed by numpy's Hermitian eigenvalue routine.

EXPECTED, WRITTEN BEFORE THE RUN (numbers are computed and printed by the script, none typed here):
 - G holds in every configuration at b = 30, 60, 120; T holds in the configuration where it is applied.
 - The configurations have k = 0, 0, 1, 2, 2 in the order U1, U2, U3, U4, E1 for statement G (asserted), and the
   top sub-cluster of U2 has k = 1 (asserted).
 - Negative control NG: U3 with the lower point's multiplicity set to 1, tested against the main term and k of
   U3.  The script asserts that the altered configuration has nu_0 != 0, so the statement with k = 1 is not the
   true one for it; the inequality MUST FAIL for it at b = 30, 60 and 120.
 - H holds for n = 2, 3, 4 at W/delta = 0.3, 0.1, 0.03, and lambda_min scales between W/delta = 0.1 and 0.03 with
   an exponent within 0.3 of 2(n-1) (an expectation about the examples; the entry proves only the upper bound).
"""
import argparse
import json
import sys
from math import factorial, sqrt
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'rh_cluster_05'))
from bandwidth_scan import scaled_norm  # noqa: E402

LAM = 100.0
PI = np.pi
# (name, theta = Lam (gamma - gamma_0), eta Lam, multiplicities, expected k)
CASES = [('U1 lower point near the top pair', [0.0, PI, 1.3], [0.0, 0.0, 1.0], [1.0, 1.0, 1.0], 0),
         ('U2 lower point far below the top pair', [0.0, PI, 1.3], [0.0, 0.0, 14.0], [1.0, 1.0, 1.0], 0),
         ('U3 lower point cancelling the top one', [0.0, PI], [0.0, 0.7], [1.0, float(np.exp(0.7))], 1),
         ('U4 three distances, binomial weights', [0.0, PI, 2 * PI], [0.0, 0.5, 1.0],
          [1.0, float(2 * np.exp(0.5)), float(np.exp(1.0))], 2),
         ('E1 equal distances 1 2 1', [0.0, PI, 2 * PI], [0.0, 0.0, 0.0], [1.0, 2.0, 1.0], 2)]


def moments(theta, etal, m):
    vth = theta - 1j * etal
    w = m * np.exp(-etal) * np.exp(-1j * theta)
    for r in range(len(theta) + 1):
        nu = np.sum(w * vth**r)
        if abs(nu) > 1e-9 * (np.sum(np.abs(w) * np.abs(vth) ** r) + 1e-300):
            return r, abs(nu), vth
    raise AssertionError('all moments vanish')


def evaluate(theta, etal, m, b, k, nu, vth):
    dstar = b / LAM
    dlt = dstar - etal / LAM
    assert np.all(dlt > 0)
    sn = float(scaled_norm(theta / LAM, dlt, m, np.array([LAM]))[0])
    lhs = sqrt(2) * b * (2 * b) ** k * sn
    main = nu * sqrt(factorial(2 * k + 1)) / factorial(k)
    err = sqrt(factorial(2 * k + 3)) / (factorial(k + 1) * 2 * b) * float(
        np.sum(m * np.exp(-etal) * np.abs(vth) ** (k + 1) * (dstar / dlt) ** (k + 2)))
    floor = sqrt(2) * b * (2 * b) ** k * float(m.sum()) * np.exp(-b) + 1e-9
    return lhs, main, err + floor, dlt, dstar


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--out', required=True)
    args = ap.parse_args()
    out = {'G': [], 'T': [], 'NG': [], 'H': []}
    for name, theta, etal, m, kexp in CASES:
        theta, etal, m = np.array(theta), np.array(etal), np.array(m)
        k, nu, vth = moments(theta, etal, m)
        assert k == kexp, (name, k, kexp)
        for b in (30.0, 60.0, 120.0):
            lhs, main, band, dlt, dstar = evaluate(theta, etal, m, b, k, nu, vth)
            out['G'].append({'case': name, 'b': b, 'k': k, 'lhs': lhs, 'main': main, 'band': band,
                             'holds': bool(abs(lhs - main) <= band), 'relative_deviation': abs(lhs - main) / main,
                             'relative_band': band / main})
            if name.startswith('U2'):
                top = etal == 0
                kt, nut, _ = moments(theta[top], etal[top], m[top])
                assert kt == 1
                c = float(np.sum(m[top] * np.abs(theta[top]) ** (kt + 1)))
                sn = float(scaled_norm(theta / LAM, dlt, m, np.array([LAM]))[0])
                lhs_t = sqrt(2) * b * (2 * b) ** kt * sn
                main_t = nut * sqrt(factorial(2 * kt + 1)) / factorial(kt)
                band_t = (c * sqrt(factorial(2 * kt + 3)) / (factorial(kt + 1) * 2 * b)
                          + (2 * b) ** kt * float(np.sum(m[~top] * (dstar / dlt[~top]) * np.exp(-etal[~top])))
                          + sqrt(2) * b * (2 * b) ** kt * float(m.sum()) * np.exp(-b) + 1e-9)
                out['T'].append({'case': name, 'b': b, 'k_top': kt, 'lhs': lhs_t, 'main': main_t, 'band': band_t,
                                 'holds': bool(abs(lhs_t - main_t) <= band_t)})
            if name.startswith('U3'):
                m_alt = np.array([1.0, 1.0])
                k_alt, nu_alt, _ = moments(theta, etal, m_alt)
                assert k_alt == 0 and nu_alt > 1e-3            # the altered configuration differs: its order is 0
                lhs_a, _, band_a, _, _ = evaluate(theta, etal, m_alt, b, k, nu, vth)
                out['NG'].append({'b': b, 'lhs_altered': lhs_a, 'main_of_U3': main, 'band': band_a,
                                  'holds': bool(abs(lhs_a - main) <= band_a)})
    delta = 0.5
    for n in (2, 3, 4):
        prev = None
        for ratio in (0.3, 0.1, 0.03):
            W = ratio * delta
            gam = np.linspace(0.0, W, n)
            Hm = 2 / (2 * delta + 1j * (gam[:, None] - gam[None, :])) ** 3
            lam_min = float(np.linalg.eigvalsh(Hm)[0])
            bound = factorial(2 * n) * W ** (2 * (n - 1)) / (n * factorial(n - 1) ** 2 * (2 * delta) ** (2 * n + 1))
            row = {'n': n, 'W_over_delta': ratio, 'lambda_min': lam_min, 'bound': float(bound),
                   'holds': bool(lam_min <= bound)}
            if prev is not None:
                row['exponent_from_previous'] = float(np.log(prev[1] / lam_min) / np.log(prev[0] / ratio))
            prev = (ratio, lam_min)
            out['H'].append(row)
    # Statement R, added after the first run (kept as unequal_distance_control_first_run.json), with its
    # expectation written here before the run that includes it: for n pairs at one distance, heights of span W,
    # R_jl = h_jl^2 / kappa^2 with h_jl = sinc((gamma_j - gamma_l - 2 i delta) Lam / 2), kappa = sinh(b)/b
    # (the matrix R of the registered many-pair norm bound),
    #     lambda_min(R) <= (Lam W)^{2(n-1)} / (n ((n-1)!)^2).
    # EXPECTED: holds for n = 2, 3, 4 at Lam W = 1, 0.3, 0.1 with b = 3; exponent between Lam W = 0.3 and 0.1
    # within 0.3 of 2(n-1).
    out['R'] = []
    lam, dl = 1.0, 3.0
    kappa = np.sinh(dl * lam) / (dl * lam)
    for n in (2, 3, 4):
        prev = None
        for lw in (1.0, 0.3, 0.1):
            gam = np.linspace(0.0, lw / lam, n)
            x = (gam[:, None] - gam[None, :] - 2j * dl) * lam / 2
            Rm = (np.sin(x) / x) ** 2 / kappa**2
            assert np.allclose(Rm, Rm.conj().T) and np.allclose(np.diag(Rm), 1.0)
            lam_min = float(np.linalg.eigvalsh(Rm)[0])
            bound = lw ** (2 * (n - 1)) / (n * factorial(n - 1) ** 2)
            row = {'n': n, 'Lam_W': lw, 'lambda_min': lam_min, 'bound': float(bound), 'holds': bool(lam_min <= bound)}
            if prev is not None:
                row['exponent_from_previous'] = float(np.log(prev[1] / lam_min) / np.log(prev[0] / lw))
            prev = (lw, lam_min)
            out['R'].append(row)
    Path(args.out).write_text(json.dumps(out, indent=1) + '\n')


if __name__ == '__main__':
    main()
