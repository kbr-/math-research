#!/usr/bin/env python3
"""Numerical control for entry short-resonance-free-range (flat window, complete grid, equal delta).

Off-axis points gamma_j - i delta, multiplicities m_j, M = sum m_j, S^2 = sum m_j^2, m_* = max m_j, least gap g.
||B_Lam||_HS is the registered closed form (reused from research/results/rh_cluster_05/bandwidth_scan.py).

Statements tested.
 B (equal distance): some Lam in [Lam1, Lam1 + H], H = 2 pi sqrt(8/3)/g, has
       ||B_Lam|| >= (sqrt2/4) S e^{delta Lam}/(delta Lam) - M.
 A (general, here with Fejer multiplicities): the same with H = 2 pi sqrt(8/3) S/(g m_*) and m_* in place of S.
 C (necessity): heights j g with g = pi/(2 Lam1), t = (p+1) ln N / delta; for every Lam in [Lam1 + t, 3 Lam1]
       ||B_Lam||^2 (delta Lam)^2 e^{-2 delta Lam} <= (K + N^{-2}(2(p+1) ln N + 1))/2 + 3 M^2 (delta Lam)^2 e^{-2 delta Lam},
   with (K, p) = (2, 1) for N simple points and (4, 2) for 2N-1 points with multiplicities N - |j|.

EXPECTED, WRITTEN BEFORE THE RUN (delta = 0.4, Lam1 = 40, g = pi/80):
 - simple, N = 12: on [Lam1 + t, 3 Lam1] the scaled square stays below the bound of C, about 1.01, hence below
   S^2/8 = 1.5, so B's inequality FAILS at every grid point there; on B's full interval (length about 261) the
   largest value of ||B|| minus B's lower bound is POSITIVE.
 - Fejer, N = 6 (11 points, m_* = 6, S^2 = 146): on [Lam1 + t, 3 Lam1] the scaled square stays below about
   2.03, hence below m_*^2/8 = 4.5, so A's inequality FAILS there; on A's interval (length about 526) the largest
   value of ||B|| minus A's lower bound is POSITIVE.
 A positive maximum on a grid confirms existence; a violation of C's bound at a grid point would refute C.
"""
import argparse
import json
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'rh_cluster_05'))
from bandwidth_scan import scaled_norm  # noqa: E402


def case(name, gam, mult, delta, lam1, bench, hfac, K, p, N):
    g = float(np.min(np.diff(np.sort(gam))))
    M, S = float(np.sum(mult)), float(np.sqrt(np.sum(mult**2)))
    mstar = float(np.max(mult))
    assert abs(g - np.pi / (2 * lam1)) < 1e-12 and lam1 >= 1 / delta
    dl = np.full(len(gam), delta)
    b = S if bench == 'S' else mstar
    H = 2 * np.pi * np.sqrt(8 / 3) * hfac / g
    lams = np.arange(lam1, lam1 + H, 0.02)
    sn = scaled_norm(gam, dl, mult, lams)                      # ||B|| e^{-delta Lam}
    lower = (np.sqrt(2) / 4) * b / (delta * lams) - M * np.exp(-delta * lams)
    t = (p + 1) * np.log(N) / delta
    assert lam1 + t < 3 * lam1
    sub = (lams >= lam1 + t) & (lams <= 3 * lam1)
    scaled_sq = (sn * delta * lams) ** 2
    cbound = (K + N**-2.0 * (2 * (p + 1) * np.log(N) + 1)) / 2 + 3 * M**2 * (delta * lams) ** 2 * np.exp(-2 * delta * lams)
    return {'case': name, 'points': len(gam), 'g': g, 'M': M, 'S2': S * S, 'm_star': mstar, 'H': H, 't': t,
            'grid': len(lams), 'max_margin_scaled': float(np.max(sn - lower)),
            'argmax_lam': float(lams[int(np.argmax(sn - lower))]),
            'sub_points': int(np.sum(sub)), 'sub_max_scaled_square': float(np.max(scaled_sq[sub])),
            'sub_max_C_bound': float(np.max(cbound[sub])),
            'C_violations': int(np.sum(scaled_sq[sub] > cbound[sub] * (1 + 1e-9))),
            'benchmark_square_over_8': b * b / 8,
            'sub_points_where_inequality_holds': int(np.sum((sn - lower)[sub] > 0))}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--out', required=True)
    args = ap.parse_args()
    delta, lam1 = 0.4, 40.0
    g = np.pi / (2 * lam1)
    out = []
    N = 12
    out.append(case('simple', g * np.arange(N), np.ones(N), delta, lam1, 'S', 1.0, 2, 1, N))
    N = 6
    j = np.arange(-(N - 1), N)
    m = (N - np.abs(j)).astype(float)
    S, mstar = float(np.sqrt(np.sum(m**2))), float(np.max(m))
    out.append(case('fejer', g * j, m, delta, lam1, 'mstar', S / mstar, 4, 2, N))
    Path(args.out).write_text(json.dumps(out, indent=1) + '\n')


if __name__ == '__main__':
    main()
