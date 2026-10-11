#!/usr/bin/env python3
"""Numerical control for entry narrow-window-negativity (Fejer kernel, off-line pairs at one distance delta = 1/2).

Objects.  b = delta L, heights gamma_j, multiplicities m_j > 0, M = sum m_j,
P(y) = sum m_j e^{-i y gamma_j}, Phi(z) = sum m_j e^{i z gamma_j} (so P(x - L) = Phi(L - x)),
h(x) = x e^{-delta x} P(x - L) for x > 0, G(tau) = sum m_j e^{-i L (tau - gamma_j)} / (tau - gamma_j + i delta)^2.

Statements tested.
 F (Fourier relation)   int Re G(tau) e^{-i (x - L) tau} d tau = -pi [ h(x) + conj h(2L - x) ]   for 0 < x < 2L.
 J (majorant)           for heights in [0, c delta] and v > 0:
                        log(Phi(iv)/M) <= (1/pi) int v/(t^2 + v^2) log(|Phi(t)|/M) dt, and Phi(iv) >= M e^{-v c delta}.
 N (narrow window)      for heights in [0, c delta], with
                        Lam(beta, b) = log((1 - 1/b)/(1 - beta)) + (1 - beta)/(1 - 1/b) - 1
                        and beta the least value (bisection) with Lam(beta, b) > pi c:
                        (i) some x in [1/delta, beta L] has |P(x - L)| > M e^{-beta b} e^{delta x}/(delta x);
                        (ii) sup Re G >= (pi^2/100) (e^{-beta b} - 4 b e^{-b})^2 M / delta^2.

The control does not share the entry's method: G, h and Phi are evaluated from their definitions.  F is a trapezoid
sum over |tau| <= 4000, which loses at most 2 M / 4000.  J is a midpoint sum in phi with t = v tan(phi), 4e6 points;
near phi = +-pi/2 the integrand oscillates faster than the grid and the sum is there a sampling average.

EXPECTED, WRITTEN BEFORE THE RUN (numbers are computed and printed by the script, none typed here):
 - F is tested at L = 8 on three pairs with heights 0, 0.4, 1.0 and multiplicities 1, 2, 1, at x = 2, 6, 7, 8, 9, 12:
   it holds within the truncation bound at every x.
   Negative control NF: the right side with h(2L - x) not conjugated.  It is applied only at the x where the
   altered right side differs from the true one by more than ten times the truncation bound, which the script
   checks, and there the relation MUST FAIL.
 - J holds in every configuration at v = 0.5, 2, 8 with a tolerance of 5e-3 for the sampling; equality within
   that tolerance is expected wherever Phi has no zero in the upper half-plane, which the script does not test.
 - N (i) and N (ii) hold in every configuration, both with a large margin; they are not expected to be able to
   fail on configurations of this size.
"""
import argparse
import json
from math import ceil, comb
from pathlib import Path

import numpy as np

DELTA = 0.5


def lam_fun(beta, b):
    return np.log((1 - 1 / b) / (1 - beta)) + (1 - beta) / (1 - 1 / b) - 1


def least_beta(c, b):
    lo, hi = 1 / b, 1 - 1e-12
    for _ in range(200):
        mid = (lo + hi) / 2
        if lam_fun(mid, b) > np.pi * c:
            hi = mid
        else:
            lo = mid
    return hi


def configs(c, L, rng):
    w = c * DELTA
    k = max(1, int(w * L / np.pi))
    return [('binomial on the resonant lattice, k=%d' % k, np.arange(k + 1) * np.pi / L,
             np.array([comb(k, j) for j in range(k + 1)], dtype=float)),
            ('six random pairs', np.sort(rng.uniform(0, w, 6)), rng.integers(1, 6, 6).astype(float)),
            ('two pairs at the window ends', np.array([0.0, w]), np.array([1.0, 1.0]))]


def P_of(gam, m, y):
    return (m[None, :] * np.exp(-1j * np.atleast_1d(y)[:, None] * gam[None, :])).sum(axis=1)


def G_of(gam, m, L, tau):
    wz = tau[:, None] - gam[None, :] + 1j * DELTA
    return (m * np.exp(-1j * L * (tau[:, None] - gam[None, :])) / wz**2).sum(axis=1)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--out', required=True)
    args = ap.parse_args()
    rng = np.random.default_rng(46)
    out = {'F': [], 'NF': [], 'J': [], 'N': []}

    # F and NF
    L, gam, m = 8.0, np.array([0.0, 0.4, 1.0]), np.array([1.0, 2.0, 1.0])
    M = m.sum()

    def h(x):
        return complex(x * np.exp(-DELTA * x) * P_of(gam, m, x - L)[0]) if x > 0 else 0j

    tw = np.arange(-4000.0, 4001.0, 0.002)
    Gw = G_of(gam, m, L, tw)
    trunc = 2 * M / 4000.0
    for x in (2.0, 6.0, 7.0, 8.0, 9.0, 12.0):
        lhs = complex(np.sum(Gw.real * np.exp(-1j * (x - L) * tw)) * 0.002)
        true = -np.pi * (h(x) + np.conj(h(2 * L - x)))
        alt = -np.pi * (h(x) + h(2 * L - x))
        out['F'].append({'x': x, 'lhs_abs': abs(lhs), 'deviation': abs(lhs - true), 'truncation_bound': trunc,
                         'holds': bool(abs(lhs - true) <= trunc)})
        applied = bool(abs(alt - true) > 10 * trunc)
        out['NF'].append({'x': x, 'applied': applied, 'altered_differs_by': abs(alt - true),
                          'holds': bool(abs(lhs - alt) <= trunc) if applied else None})

    # J and N
    phi = (np.arange(4_000_000) + 0.5) / 4_000_000 * np.pi - np.pi / 2
    tanphi = np.tan(phi)
    for c, L in ((0.05, 160.0), (0.05, 240.0), (0.02, 400.0)):
        b = DELTA * L
        beta = least_beta(c, b)
        for name, gam, m in configs(c, L, rng):
            assert gam.min() >= 0 and gam.max() <= c * DELTA + 1e-12
            M = m.sum()
            xs = np.linspace(1 / DELTA, beta * L, 20001)
            prof = np.abs(P_of(gam, m, xs - L)) * DELTA * xs * np.exp(-DELTA * xs) / M
            tau = np.arange(gam.min() - 40.0, gam.max() + 40.0, 0.0005)
            sup_re = float(G_of(gam, m, L, tau).real.max())
            low = np.pi**2 / 100 * (np.exp(-beta * b) - 4 * b * np.exp(-b)) ** 2 * M / DELTA**2
            out['N'].append({'c': c, 'b': b, 'case': name, 'n': int(len(gam)), 'beta': float(beta), 'two_beta': float(2 * beta),
                             'profile_max': float(prof.max()), 'profile_threshold': float(np.exp(-beta * b)),
                             'N_i_holds': bool(prof.max() > np.exp(-beta * b)),
                             'sup_Re_G_delta2_over_M': sup_re * DELTA**2 / M,
                             'lower_bound_delta2_over_M': float(low * DELTA**2 / M), 'N_ii_holds': bool(sup_re >= low)})
            for v in (0.5, 2.0, 8.0):
                acc = np.zeros(len(phi), dtype=complex)
                for g, mj in zip(gam, m):
                    acc += mj * np.exp(1j * v * tanphi * g)
                rhs = float(np.mean(np.log(np.maximum(np.abs(acc), 1e-300) / M)))
                phiv = float((m * np.exp(-v * gam)).sum())
                out['J'].append({'c': c, 'b': b, 'case': name, 'v': v, 'lhs': float(np.log(phiv / M)), 'rhs': rhs,
                                 'holds': bool(np.log(phiv / M) <= rhs + 5e-3),
                                 'lower_bound_on_Phi_holds': bool(phiv >= M * np.exp(-v * c * DELTA) * (1 - 1e-12))})
    Path(args.out).write_text(json.dumps(out, indent=1) + '\n')


if __name__ == '__main__':
    main()
