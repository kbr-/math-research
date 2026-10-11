#!/usr/bin/env python3
"""Numerical control for the family mean count of entry sum-function-zero-count.

Objects.  F(z) = prod (z - z_j) without real zeros, u zeros above the real line and l below, n = u + l;
F#(z) = conj F(conj z);  A_theta = F + e^{i theta} F#;  N(theta) = number of real zeros of A_theta;
a_j(x) = Im z_j / |x - z_j|^2, so that (arg F)'(x) = sum_j a_j(x).

Statement tested.
 M (mean count)  (1/(2 pi)) int_{-pi}^{pi} N(theta) d theta = (1/pi) int_R |sum_j a_j(x)| dx, and this is n exactly
                 when min(u, l) = 0 and less than n otherwise.

The two sides are computed by unrelated routes: the left by the zeros of A_theta from numpy's companion-matrix
routine on a grid of theta (midpoints, so that theta = pi is not a grid point), the right by the trapezoid rule
after the substitution x = tan t.  A zero counts as real when |Im| <= 1e-6 (1 + |Re|); the script counts the grid
points with a zero whose |Im| is between that and 1e-3 (1 + |Re|) (ambiguous) and prints their share.

EXPECTED, WRITTEN BEFORE THE RUN (the numbers are computed and printed by the script):
 - M: in each of 24 random configurations, n from 2 to 8, the two sides differ by at most TOL = 0.02, which the
   script prints beside the smaller of the two quantities compared (expected to be of order 1 or more, so that
   the tolerance is the smaller wherever the row counts as a check; rows where it is not are counted and reported
   as testing nothing).
 - One-sided configurations (6 of the 24 are generated one-sided): both sides equal n within TOL.
 - Negative control NC: the altered statement "the mean count is n".  It differs from M exactly on the two-sided
   configurations where n minus the right side exceeds 2 TOL; the script asserts that this set is nonempty and
   reports on how many of its members the altered statement fails (expected: all of them).
 - The example F = (z - i)(z - T + i eps), (T, eps) = (5, 0.1): N(0) = 2 and the mean is below 2; the script
   prints the mean.
"""
import argparse
import json
from pathlib import Path

import numpy as np

TOL = 0.02
GRID = 4000
QUAD = 2_000_001


def mean_real_count(z):
    F = np.poly(z)
    Fs = np.poly(z.conj())
    thetas = -np.pi + (np.arange(GRID) + 0.5) * (2 * np.pi / GRID)
    total, ambiguous = 0, 0
    for th in thetas:
        r = np.roots(F + np.exp(1j * th) * Fs)
        scale = 1 + np.abs(r.real)
        real = np.abs(r.imag) <= 1e-6 * scale
        ambiguous += int(np.any((~real) & (np.abs(r.imag) <= 1e-3 * scale)))
        total += int(real.sum())
    return total / GRID, ambiguous / GRID


def variation_over_pi(z):
    t = np.linspace(-np.pi / 2, np.pi / 2, QUAD)[1:-1]
    x = np.tan(t)
    s = np.zeros_like(x)
    for zj in z:
        s += zj.imag / ((x - zj.real) ** 2 + zj.imag ** 2)
    integrand = np.abs(s) / np.cos(t) ** 2
    h = t[1] - t[0]
    return float(np.sum(integrand) * h / np.pi)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--out', required=True)
    args = ap.parse_args()
    rng = np.random.default_rng(4802)
    rows = []
    for k in range(24):
        n = int(rng.integers(2, 9))
        re = rng.uniform(-2, 2, n)
        sign = np.ones(n) if k < 6 else rng.choice([-1.0, 1.0], n)
        im = rng.uniform(0.1, 1.5, n) * sign
        z = re + 1j * im
        u, low = int((im > 0).sum()), int((im < 0).sum())
        left, amb = mean_real_count(z)
        right = variation_over_pi(z)
        rows.append({'n': n, 'u': u, 'l': low, 'mean_real_count': left, 'variation_over_pi': right,
                     'difference': abs(left - right), 'tolerance': TOL, 'smaller_quantity': min(left, right),
                     'counts_as_check': bool(TOL < min(left, right)), 'ambiguous_share': amb,
                     'M_holds': bool(abs(left - right) <= TOL)})
    checks = [r for r in rows if r['counts_as_check']]
    one_sided = [r for r in rows if min(r['u'], r['l']) == 0]
    differing = [r for r in rows if min(r['u'], r['l']) > 0 and r['n'] - r['variation_over_pi'] > 2 * TOL]
    assert differing, 'negative control has no case where the altered statement differs'
    z = np.array([1j, 5.0 - 0.1j])
    ex_mean, ex_amb = mean_real_count(z)
    ex_zero = np.roots(np.poly(z) + np.poly(z.conj()))
    summary = {
        'rows': len(rows), 'rows_counting_as_check': len(checks), 'rows_testing_nothing': len(rows) - len(checks),
        'M_holds_in_checks': sum(r['M_holds'] for r in checks),
        'largest_difference': max(r['difference'] for r in rows),
        'one_sided_rows': len(one_sided),
        'one_sided_both_equal_n': sum(abs(r['mean_real_count'] - r['n']) <= TOL and abs(r['variation_over_pi'] - r['n']) <= TOL
                                      for r in one_sided),
        'two_sided_rows': len(rows) - len(one_sided),
        'NC_differs_on': len(differing),
        'NC_fails_on': sum(abs(r['mean_real_count'] - r['n']) > TOL for r in differing),
        'least_deficit_n_minus_mean_two_sided': min(r['n'] - r['mean_real_count'] for r in rows if min(r['u'], r['l']) > 0),
        'example': {'T': 5.0, 'eps': 0.1, 'real_zeros_at_theta_0': int(np.sum(np.abs(ex_zero.imag) < 1e-9)),
                    'mean_real_count': ex_mean, 'variation_over_pi': variation_over_pi(z), 'ambiguous_share': ex_amb},
    }
    Path(args.out).write_text(json.dumps({'summary': summary, 'rows': rows}, indent=1) + '\n')


if __name__ == '__main__':
    main()
