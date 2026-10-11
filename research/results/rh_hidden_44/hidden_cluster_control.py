#!/usr/bin/env python3
"""Numerical control for entry hidden-cluster-length (Fejer kernel, off-line pairs at one distance delta = 1/2).

Objects as in research/results/rh_onesided_43/one_sided_control.py: K_L(w) = 2 (1 - cos(L w)) / (L w^2),
D_off(tau) = sum_j m_j 2 Re K_L(tau - gamma_j + i delta), G(tau) = sum_j m_j e^{-i L (tau - gamma_j)} /
(tau - gamma_j + i delta)^2, b = delta L, P(y) = sum_j m_j e^{-i y gamma_j}.

Statements tested.
 A (lattice saturation)  N simple pairs at heights j pi/L:
       sup |G| <= (1/delta^2) (1 + 3 pi^2/(2 b^2) + N (1 + b/2) e^{-b/2}).
 B (binomial cluster)    k+1 pairs at heights j pi/L with multiplicities C(k, j):
       sup |G| <= (k+1)! (pi/b)^k / delta^2.
 C (hiding)              for the binomial cluster, min D_off >= -(2 e^b/L) (k+1)! (pi/b)^k / delta^2
                         - 6 * 2^k / (L delta^2); a real lattice of spacing s <= 2 pi/L adds exactly 2 pi/s.
 P (Poisson)             sum_j K_L(tau - j s) = 2 pi / s for s <= 2 pi / L (checked by a truncated sum).
 D (sampled lower bound, Turan's Theorem 8.1 as recorded in the notebook) for n pairs, h = 1/(n delta),
       m = ceil(n (b - 2)):  max_{m < nu <= m+n} |P(nu h)| >= 2 (8 e b)^{-n} max m_j.

The control does not share the entry's method: G and D_off are evaluated from their definitions on a grid in tau,
the lattice sum by direct summation, P at the sample points directly.

EXPECTED, WRITTEN BEFORE THE RUN (numbers are computed and printed by the script, none typed here):
 - A, B, C, D hold in every case; P holds to the truncation bound printed with it.
 - B is nearly sharp for b large against k: the ratio sup|G| / bound is at least 0.3 whenever b >= 2 pi (k+1).
 - Negative control NB: the bound of B with k+1 in place of k (one more vanishing moment claimed).  It is applied
   only where the altered bound is smaller than the true bound, which the script asserts, and there it MUST FAIL
   whenever b >= 2 pi (k+2); in the other cases its outcome is reported without a prediction.
 - D has a very large margin (the bound is far from sharp) and is not expected to be able to fail on these cases.
"""
import argparse
import json
from math import comb, factorial, ceil
from pathlib import Path

import numpy as np

DELTA = 0.5


def sup_G_and_min_D(L, gam, m):
    tau = np.arange(gam.min() - 60.0, gam.max() + 60.0, 0.0005)
    w = tau[:, None] - gam[None, :] + 1j * DELTA
    G = (m * np.exp(-1j * L * (tau[:, None] - gam[None, :])) / w**2).sum(axis=1)
    D = (m * 2 * (2 * (1 - np.cos(L * w)) / (L * w**2)).real).sum(axis=1)
    return float(np.abs(G).max()), float(D.min())


def turan_sample(L, gam, m):
    n, b = len(gam), DELTA * L
    h, m0 = 1 / (n * DELTA), ceil(n * (b - 2))
    nu = np.arange(m0 + 1, m0 + n + 1)
    P = (m[None, :] * np.exp(-1j * (nu * h)[:, None] * gam[None, :])).sum(axis=1)
    return float(np.abs(P).max()), float(2 * (8 * np.e * b) ** (-n) * m.max())


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--out', required=True)
    args = ap.parse_args()
    out = {'A': [], 'B': [], 'P': []}
    for L in (24.0, 40.0, 60.0):
        b, s = DELTA * L, np.pi / L
        for N in (2, 5, 40):
            gam, m = s * np.arange(N), np.ones(N)
            sup, _ = sup_G_and_min_D(L, gam, m)
            bound = (1 + 3 * np.pi**2 / (2 * b**2) + N * (1 + b / 2) * np.exp(-b / 2)) / DELTA**2
            smax, sbound = turan_sample(L, gam, m)
            out['A'].append({'b': b, 'N': N, 'sup_abs_G': sup, 'bound': float(bound), 'holds': bool(sup <= bound),
                             'D_sample_max': smax, 'D_bound': sbound, 'D_holds': bool(smax >= sbound)})
        for k in (1, 3, 6, 8):
            gam, m = s * np.arange(k + 1), np.array([comb(k, j) for j in range(k + 1)], dtype=float)
            sup, dmin = sup_G_and_min_D(L, gam, m)
            F = factorial(k + 1) * (np.pi / b) ** k
            bound = F / DELTA**2
            F1 = factorial(k + 2) * (np.pi / b) ** (k + 1)
            hide = 2 * np.exp(b) / L * F / DELTA**2 + 6 * 2**k / (L * DELTA**2)
            smax, sbound = turan_sample(L, gam, m)
            row = {'b': b, 'k': k, 'sup_abs_G': sup, 'bound': float(bound), 'holds': bool(sup <= bound * (1 + 1e-9)),
                   'ratio': sup / bound, 'sharp_expected': bool(b >= 2 * np.pi * (k + 1)),
                   'min_D_off': dmin, 'hiding_density_bound': float(hide), 'C_holds': bool(dmin >= -hide),
                   'solitary_pair_min_D_off_scale': float(2 * np.exp(b) / (L * DELTA**2)),
                   'D_sample_max': smax, 'D_bound': sbound, 'D_holds': bool(smax >= sbound)}
            altered = F1 / DELTA**2
            row['NB_applied'] = bool(altered < bound)
            if row['NB_applied']:
                row['NB_altered_bound'] = float(altered)
                row['NB_holds'] = bool(sup <= altered)
                row['NB_must_fail'] = bool(b >= 2 * np.pi * (k + 2))
            out['B'].append(row)
        sp = 2 * np.pi / L / 3
        J = 400000
        j = np.arange(-J, J + 1)
        for tau in (0.0, 0.37 * sp, 0.5 * sp):
            t = tau - j * sp
            Kv = np.where(np.abs(t) < 1e-12, L, 2 * (1 - np.cos(L * t)) / (L * np.maximum(t * t, 1e-300)))
            out['P'].append({'b': b, 'tau_over_s': tau / sp, 'sum': float(Kv.sum()), 'two_pi_over_s': float(2 * np.pi / sp),
                             'truncation_bound': float(8 / (L * sp * sp * J))})
    Path(args.out).write_text(json.dumps(out, indent=1) + '\n')


if __name__ == '__main__':
    main()
