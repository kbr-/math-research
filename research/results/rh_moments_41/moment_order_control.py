#!/usr/bin/env python3
"""Numerical control for entry endpoint-moment-order (flat window, complete grid, equal delta).

Statement tested.  Off-axis points gamma_j - i delta, multiplicities m_j > 0, M = sum m_j, bandwidth Lam,
b = delta Lam, theta_j = Lam (gamma_j - gamma_0), w_j = m_j exp(-i Lam gamma_j), nu_r = sum_j w_j theta_j^r,
k the least r with nu_r != 0, c = sum_j m_j |theta_j|^(k+1).  Then

   | sqrt2 b (2b)^k ||B_Lam||_HS e^(-b)  -  |nu_k| sqrt((2k+1)!) / k! |
        <=  c sqrt((2k+3)!) / ((k+1)! 2b)  +  sqrt2 b (2b)^k M e^(-b)  +  tail,

where tail = |nu_k| (sqrt((2k+1)!) - sqrt(gamma(2k+2, 2b))) / k! is below 1e-9 for b >= 30.
||B_Lam||_HS is the registered closed form (reused from research/results/rh_cluster_05/bandwidth_scan.py); it uses
nothing proved in the entry.

EXPECTED, WRITTEN BEFORE THE RUN:
 - the inequality HOLDS in every case below at b = 30, 60, 120;
 - the relative size of the allowed band shrinks like 1/b, and at b = 120 it is a few percent, so a wrong
   constant would be seen: the control replaces sqrt((2k+1)!) by sqrt((2k)!) in the main term and must FAIL
   in every case at b = 120;
 - the cases with k >= 1 are exactly: two simple points at gap pi/Lam (k = 1); three points at gaps pi/Lam with
   multiplicities 1, 2, 1 (k = 2); four simple points at theta = 0, pi, 3 pi, 4 pi (k = 2); four points at gaps
   pi/Lam with multiplicities 1, 3, 3, 1 (k = 3).  A solitary point, three simple points at gaps pi/Lam, and a
   narrow cluster of width 1/Lam have k = 0.
"""
import argparse
import json
import sys
from math import factorial, sqrt
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'rh_cluster_05'))
from bandwidth_scan import scaled_norm  # noqa: E402

CASES = [('solitary', [0.0], [1.0], 0),
         ('two at gap pi', [0.0, np.pi], [1.0, 1.0], 1),
         ('three simple at gaps pi', [0.0, np.pi, 2 * np.pi], [1.0, 1.0, 1.0], 0),
         ('binomial 1 2 1', [0.0, np.pi, 2 * np.pi], [1.0, 2.0, 1.0], 2),
         ('subset sums of 1 and 3', [0.0, np.pi, 3 * np.pi, 4 * np.pi], [1.0, 1.0, 1.0, 1.0], 2),
         ('binomial 1 3 3 1', [0.0, np.pi, 2 * np.pi, 3 * np.pi], [1.0, 3.0, 3.0, 1.0], 3),
         ('narrow cluster', [0.0, 0.3, 0.55, 1.0], [1.0, 2.0, 1.0, 1.0], 0)]


def order(theta, m):
    w = m * np.exp(-1j * theta)                      # exp(-i Lam gamma_j) with gamma_0 = 0
    for r in range(len(theta)):
        nu = np.sum(w * theta**r)
        if abs(nu) > 1e-9 * np.sum(m * np.abs(theta) ** r + (r == 0)):
            return r, abs(nu)
    raise AssertionError('all moments vanish')


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--out', required=True)
    args = ap.parse_args()
    lam, out = 100.0, []
    for name, theta, m, kexp in CASES:
        theta, m = np.array(theta), np.array(m)
        k, nu = order(theta, m)
        assert k == kexp, (name, k, kexp)
        c, M = float(np.sum(m * np.abs(theta) ** (k + 1))), float(np.sum(m))
        for b in (30.0, 60.0, 120.0):
            delta = b / lam
            sn = float(scaled_norm(theta / lam, np.full(len(theta), delta), m, np.array([lam]))[0])
            lhs_q = sqrt(2) * b * (2 * b) ** k * sn
            band = c * sqrt(factorial(2 * k + 3)) / (factorial(k + 1) * 2 * b) + sqrt(2) * b * (2 * b) ** k * M * np.exp(-b) + 1e-9
            main_term = nu * sqrt(factorial(2 * k + 1)) / factorial(k)
            wrong = nu * sqrt(factorial(2 * k)) / factorial(k)
            out.append({'case': name, 'k': k, 'b': b, 'scaled_norm_times_factor': lhs_q, 'main_term': main_term,
                        'band': band, 'holds': bool(abs(lhs_q - main_term) <= band),
                        'relative_band': band / main_term, 'relative_deviation': abs(lhs_q - main_term) / main_term,
                        'control_wrong_constant_holds': bool(abs(lhs_q - wrong) <= band)})
    Path(args.out).write_text(json.dumps(out, indent=1) + '\n')


if __name__ == '__main__':
    main()
