#!/usr/bin/env python3
"""Numerical control for entry one-sided-half-plane-equivalence (finite configurations, Fejer kernel).

Objects.  K_L(w) = 2 (1 - cos L w)/(L w^2).  Off-line pairs gamma_j +- i delta_j with multiplicities m_j;
D_off(tau) = sum_j 2 m_j Re K_L(tau - gamma_j - i delta_j).

Statements tested.
 A (lower bound)   D_off(tau) >= - sum_j m_j e^{delta_j L} min(2 L, 8/(L ((tau - gamma_j)^2 + delta_j^2))).
 B (recurrence)    with delta* the largest distance, tau generic, c_j = m_j/(tau - gamma_j - i delta*)^2 over the
                   pairs at distance delta*, q = sum |c_j|^2 / (2 sum |c_j|): the function
                   F(L) = L e^{-delta* L} D_off(tau) takes a value <= -q + r somewhere in every long window of L,
                   r the remainder from the other terms.
 C (product range) for every a > 0, I(a) = (1/a) int_a^{2a} log|2 cos u| du >= -1.3; equivalently for
                   P(y) = prod_i (1 + e^{-i y eta_i}) the mean of log|P| over [L_0, 2 L_0] is at least -1.3 n.

D_off is computed from the closed form of K_L at complex arguments by numpy, which uses none of the bounds.

EXPECTED, WRITTEN BEFORE THE RUN (every number is computed and printed by the script):
 - A holds at every sampled (configuration, L, tau): 60 random configurations of 1 to 6 pairs with distances in
   (0.02, 0.5), L in {4, 10, 25, 60}, 400 values of tau.  The script prints the least ratio (bound + D_off)/bound,
   expected in [0, 1].
 - Negative control NA: the bound with e^{delta_j L/2} in place of e^{delta_j L}.  It is applied only to
   single-pair configurations with delta L >= 8 at tau = gamma + pi/L, where the pair's value is about
   -0.84 e^{b} m/(L delta^2) and the altered bound is larger than that (asserted in the script from the two
   numbers); expected to fail there in every such case.
 - B: for 20 random configurations whose top distance is attained by 1 to 3 pairs (other pairs at most 0.6 of it),
   the minimum of F over L in [40/delta*, 40/delta* + 400] on a grid of step 0.01 is at most -q + r with
   r = 0.05 q; expected in all 20.  This is a finite window for an asymptotic statement, so a failure would not
   refute the lemma; the script prints min F / q for each case.
 - Negative control NB: the same with 3 q in place of q.  Since |Q| <= 2 sum |c_j| and q <= sum|c_j|/2, the altered
   statement can fail only where min F > -3 q + r; the script counts those cases and reports them; expected to
   exist (for a single top pair, min F is about -2|c| = -4 q, so it holds there; for several it may fail).
 - C: the minimum of I(a) over a grid of a in (0.01, 60) is printed, expected between -1.3 and -0.3, and I(a) for
   a = 50 is expected within 0.05 of 0.
"""
import argparse
import json
from pathlib import Path

import numpy as np


def kernel(L, w):
    return 2 * (1 - np.cos(L * w)) / (L * w * w)


def d_off(L, tau, gam, dlt, mul):
    w = tau[:, None] - gam[None, :] - 1j * dlt[None, :]
    return (2 * mul[None, :] * kernel(L, w).real).sum(axis=1)


def bound_a(L, tau, gam, dlt, mul, half=False):
    u2 = (tau[:, None] - gam[None, :]) ** 2 + dlt[None, :] ** 2
    grow = np.exp(dlt * L * (0.5 if half else 1.0))[None, :]
    return (mul[None, :] * grow * np.minimum(2 * L, 8 / (L * u2))).sum(axis=1)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--out', required=True)
    args = ap.parse_args()
    rng = np.random.default_rng(50)
    out = {}

    # A
    least, fails, samples = np.inf, 0, 0
    for _ in range(60):
        n = int(rng.integers(1, 7))
        gam = rng.uniform(-3, 3, n)
        dlt = rng.uniform(0.02, 0.5, n)
        mul = rng.integers(1, 4, n).astype(float)
        tau = np.concatenate([rng.uniform(-5, 5, 300), gam[0] + rng.uniform(-0.3, 0.3, 100)])
        for L in (4.0, 10.0, 25.0, 60.0):
            d = d_off(L, tau, gam, dlt, mul)
            b = bound_a(L, tau, gam, dlt, mul)
            ratio = (b + d) / b
            least = min(least, float(ratio.min()))
            fails += int((ratio < 0).sum())
            samples += len(tau)
    out['A'] = {'samples': samples, 'fails': fails, 'least_ratio': least}

    # NA
    na = []
    for _ in range(12):
        dl = float(rng.uniform(0.1, 0.5))
        L = float(rng.uniform(8, 20)) / dl
        gam, dlt, mul = np.array([0.0]), np.array([dl]), np.array([1.0])
        tau = np.array([np.pi / L])
        d = float(d_off(L, tau, gam, dlt, mul)[0])
        alt = float(bound_a(L, tau, gam, dlt, mul, half=True)[0])
        true = float(bound_a(L, tau, gam, dlt, mul)[0])
        assert -alt > -true, 'altered bound is not stronger'
        na.append({'b': dl * L, 'D_off': d, 'altered_bound': -alt, 'true_bound': -true, 'altered_fails': bool(d < -alt),
                   'predicted_pair_value': -0.84 * np.exp(dl * L) / (L * dl * dl)})
    out['NA'] = {'cases': len(na), 'altered_fails_in': sum(r['altered_fails'] for r in na), 'rows': na}

    # B and NB
    rows = []
    for _ in range(20):
        top = int(rng.integers(1, 4))
        low = int(rng.integers(0, 3))
        ds = float(rng.uniform(0.2, 0.5))
        gam = rng.uniform(-2, 2, top + low)
        dlt = np.concatenate([np.full(top, ds), rng.uniform(0.05, 0.6 * ds, low)])
        mul = rng.integers(1, 4, top + low).astype(float)
        tau0 = float(rng.uniform(-3, 3))
        c = mul[:top] / (tau0 - gam[:top] - 1j * ds) ** 2
        q = float((np.abs(c) ** 2).sum() / (2 * np.abs(c).sum()))
        Ls = 40 / ds + np.arange(0, 400, 0.01)
        w = tau0 - gam[None, :] - 1j * dlt[None, :]
        vals = (2 * mul[None, :] * (2 * (1 - np.cos(Ls[:, None] * w)) / (Ls[:, None] * w * w)).real).sum(axis=1)
        F = Ls * np.exp(-ds * Ls) * vals
        mn = float(F.min())
        rows.append({'top_pairs': top, 'lower_pairs': low, 'q': q, 'min_F': mn, 'min_F_over_q': mn / q,
                     'tolerance_r': 0.05 * q, 'B_holds': bool(mn <= -q + 0.05 * q),
                     'NB_differs': bool(mn > -3 * q + 0.05 * q)})
    out['B'] = {'cases': len(rows), 'B_holds_in': sum(r['B_holds'] for r in rows),
                'NB_differs_and_fails_in': sum(r['NB_differs'] for r in rows), 'rows': rows}

    # C
    u = np.linspace(0, 130, 13_000_001)[1:]
    f = np.log(np.abs(2 * np.cos(u)) + 1e-300)
    cum = np.concatenate([[0.0], np.cumsum((f[1:] + f[:-1]) / 2) * (u[1] - u[0])])
    def integral(a):
        i0, i1 = np.searchsorted(u, a), np.searchsorted(u, 2 * a)
        return (cum[i1] - cum[i0]) / a
    grid = np.concatenate([np.linspace(0.01, 5, 5000), np.linspace(5, 60, 5000)])
    vals = np.array([integral(a) for a in grid])
    k = int(vals.argmin())
    out['C'] = {'min_I': float(vals[k]), 'argmin_a': float(grid[k]), 'I_at_50': float(integral(50.0)),
                'I_at_0.01': float(integral(0.01)), 'log2': float(np.log(2)), 'quadrature_step': float(u[1] - u[0])}
    Path(args.out).write_text(json.dumps(out, indent=1) + '\n')


if __name__ == '__main__':
    main()
