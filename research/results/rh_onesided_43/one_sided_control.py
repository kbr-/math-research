#!/usr/bin/env python3
"""Numerical control for entry one-sided-cluster-negativity (flat window, off-line pairs at one distance delta).

Objects.  K_L(w) = 2 (1 - cos(L w)) / (L w^2).  Off-line pairs gamma_j -+ i delta with multiplicities m_j > 0,
M = sum m_j, S^2 = sum m_j^2, b = delta L.  D_off(tau) = sum_j m_j 2 Re K_L(tau - gamma_j + i delta),
G(tau) = sum_j m_j exp(-i L (tau - gamma_j)) / (tau - gamma_j + i delta)^2,
Y(tau) = sum_j m_j / ((tau - gamma_j)^2 + delta^2).

Statements tested.
 S1 (decomposition)  | D_off(tau) + (2 e^b / L) Re G(tau) | <= 6 Y(tau) / L          at every grid point.
 S2 (Plancherel)     int |G|^2 d tau = 2 pi J,  J = a^* H^T a,  a_j = m_j e^{i L gamma_j},
                     (the first run, kept as one_sided_control_first_run.json, had J = a^* H a, which is wrong
                     when the a_j are not real up to a common phase; S2 showed it: the two other values of J
                     agreed with each other and not with the matrix value in the two non-resonant
                     configurations.  The expectations below were written before that run and are unchanged.)
                     H_jl = 2 / (2 delta + i (gamma_j - gamma_l))^3; also J by direct quadrature of
                     int_0^inf x^2 e^{-2 delta x} |sum a_j e^{-i x gamma_j}|^2 dx.
 S3 (cluster)        sup Re G >= c := (A1/4 - eps/2) / (W + 16 M / A1),  A1 = pi delta^2 J / M,
                     eps = 2 pi L e^{-b} M,  W = span of the heights.
 S4 (inherited loss) sup |G| <= (k+1) c_k / (delta^2 b^k), k = number of vanishing moments of
                     m_j e^{i L gamma_j} against theta_j = L (gamma_j - gamma_1), c_k = sum m_j |theta_j|^k.
 S5 (separated pair) if b >= 2 pi and every other height is at least 8 delta sqrt(m'/m_j) from gamma_j
                     (m' the largest other multiplicity), then Re G(gamma_j + pi/L) >= 0.42 m_j / delta^2.

The control does not share the entry's method: D_off is evaluated from the complex cosine, G from its closed
form, J three ways (the matrix H, quadrature in x, and the tau-integral of |G|^2).

EXPECTED, WRITTEN BEFORE THE RUN (numbers are computed and printed by the script, none typed here):
 - S1, S3, S4 hold in every configuration at every L; S5 holds in the separated configuration at each pair.
 - S2: the three values of J agree to 2 percent; the tau-integral is truncated at distance 400 from the heights,
   which loses at most 2 M^2 / (3 * 400^3), printed by the script relative to 2 pi J.
 - S3 is far from sharp: the ratio sup Re G / c is expected between 10 and 10^4.
 - Negative control N3: in the resonant configurations (k >= 1) at b = 30, replace J in S3 by the non-interacting
   value S^2/(4 delta^3).  The script first asserts that the altered constant c' exceeds the S4 bound for sup |G|,
   in which case S3 with c' MUST FAIL; where the assertion does not hold the control is not applied and is
   reported as not applicable.
"""
import argparse
import json
from pathlib import Path

import numpy as np

DELTA = 0.5


def configs(L):
    s = np.pi / L
    return [('solitary', [0.0], [1.0]),
            ('two at gap pi/L', [0.0, s], [1.0, 1.0]),
            ('binomial 1 2 1 at gaps pi/L', [0.0, s, 2 * s], [1.0, 2.0, 1.0]),
            ('binomial 1 3 3 1 at gaps pi/L', [0.0, s, 2 * s, 3 * s], [1.0, 3.0, 3.0, 1.0]),
            ('narrow cluster', [0.0, 0.11, 0.3, 0.37, 0.6], [1.0, 2.0, 1.0, 1.0, 3.0]),
            ('separated', [0.0, 4.3, 9.1, 15.0], [1.0, 1.0, 1.0, 1.0])]


def order(theta, a):
    for r in range(len(theta)):
        nu = np.sum(a * theta**r)
        if abs(nu) > 1e-9 * (np.sum(np.abs(a) * np.abs(theta) ** r) + 1e-300):
            return r
    raise AssertionError('all moments vanish')


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--out', required=True)
    args = ap.parse_args()
    out = []
    for L in (20.0, 37.3, 60.0):
        b = DELTA * L
        for name, gam, m in configs(L):
            gam, m = np.array(gam), np.array(m)
            M, S2, W = m.sum(), (m**2).sum(), gam.max() - gam.min()
            tau = np.arange(gam.min() - 400.0, gam.max() + 400.0, 0.002)
            w = tau[:, None] - gam[None, :] + 1j * DELTA
            K = 2 * (1 - np.cos(L * w)) / (L * w**2)
            D = (m * 2 * K.real).sum(axis=1)
            G = (m * np.exp(-1j * L * (tau[:, None] - gam[None, :])) / w**2).sum(axis=1)
            Y = (m / ((tau[:, None] - gam[None, :]) ** 2 + DELTA**2)).sum(axis=1)
            s1 = float(np.max(np.abs(D + 2 * np.exp(b) / L * G.real) - 6 * Y / L))
            a = m * np.exp(1j * L * gam)
            H = 2 / (2 * DELTA + 1j * (gam[:, None] - gam[None, :])) ** 3
            J_mat = float((a.conj() @ H.T @ a).real)     # corrected after the first run: see the header's note
            x = np.arange(0.0, 80.0, 0.0005)
            P = (a[None, :] * np.exp(-1j * x[:, None] * gam[None, :])).sum(axis=1)
            J_quad = float(np.sum(x**2 * np.exp(-2 * DELTA * x) * np.abs(P) ** 2) * 0.0005)
            J_tau = float(np.sum(np.abs(G) ** 2) * 0.002 / (2 * np.pi))
            A1, eps = np.pi * DELTA**2 * J_mat / M, 2 * np.pi * L * np.exp(-b) * M
            c = (A1 / 4 - eps / 2) / (W + 16 * M / A1)
            sup_re, sup_abs = float(G.real.max()), float(np.abs(G).max())
            theta = L * (gam - gam[0])
            k = order(theta, a)
            ck = float(np.sum(m * np.abs(theta) ** k))
            s4 = (k + 1) * ck / (DELTA**2 * b**k)
            row = {'L': L, 'b': b, 'case': name, 'k': k, 'S1_max_excess': s1, 'S1_holds': bool(s1 <= 1e-9),
                   'J_matrix': J_mat, 'J_quadrature': J_quad, 'J_tau_integral': J_tau,
                   'S2_rel_dev_quadrature': abs(J_quad - J_mat) / J_mat, 'S2_rel_dev_tau': abs(J_tau - J_mat) / J_mat,
                   'S2_truncation_rel_bound': float(2 * M**2 / 400.0**3 / 3 / (2 * np.pi * J_mat)),
                   'c': float(c), 'sup_Re_G': sup_re, 'S3_holds': bool(sup_re >= c), 'S3_ratio': sup_re / c,
                   'sup_abs_G': sup_abs, 'S4_bound': float(s4), 'S4_holds': bool(sup_abs <= s4 * (1 + 1e-9))}
            if k >= 1 and L == 60.0:
                A1w = np.pi * DELTA**2 * (S2 / (4 * DELTA**3)) / M
                cw = (A1w / 4 - eps / 2) / (W + 16 * M / A1w)
                applicable = bool(cw > s4)
                row['N3_altered_c'] = float(cw)
                row['N3_applicable'] = applicable
                row['N3_holds_with_altered_c'] = bool(sup_re >= cw) if applicable else None
            if name == 'separated':
                s5 = []
                for j in range(len(gam)):
                    others = np.delete(gam, j)
                    mp = np.delete(m, j).max()
                    assert b >= 2 * np.pi and np.min(np.abs(others - gam[j])) >= 8 * DELTA * np.sqrt(mp / m[j])
                    wj = gam[j] + np.pi / L - gam + 1j * DELTA
                    val = float((m * np.exp(-1j * L * (gam[j] + np.pi / L - gam)) / wj**2).sum().real)
                    s5.append({'pair': j, 'Re_G': val, 'bound': 0.42 * m[j] / DELTA**2, 'holds': bool(val >= 0.42 * m[j] / DELTA**2)})
                row['S5'] = s5
            out.append(row)
    Path(args.out).write_text(json.dumps(out, indent=1) + '\n')


if __name__ == '__main__':
    main()
