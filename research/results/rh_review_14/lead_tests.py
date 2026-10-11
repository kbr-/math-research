"""Cheap tests of three translations named in the route review of 11 October 2026 (riemann notebook).

T1 (heat flow, de Bruijn).  For a real polynomial p with real roots and one conjugate pair at distance delta
    from the real axis, exp(-t D^2) p has only real roots for t >= delta^2/2.  Tested: the least such t on a
    grid, compared with delta^2/2; control: for negative t an all-real configuration acquires non-real roots.
T2 (power sums, Turan's second theorem as recalled, unread).  For z_1..z_N with max |z_j| = 1 and b_j = 1,
    max over nu in [m+1, m+N] of |sum z_j^nu| >= (N/(8e(m+N)))^N.  Tested on random configurations and on
    close conjugate pairs built to cancel; a violation would falsify the recalled statement.
T3 (truncation and stability).  For F with all zeros in the open lower half-plane (a shifted on-line
    configuration), is every Taylor section of F about 0 again zero-free in the upper half-plane?  A section
    with a zero in the closed upper half-plane falsifies the translation "stability survives truncation".
"""
import argparse
import json
import math

import numpy as np
from numpy.polynomial import polynomial as P


def heat(coeffs, t):
    """exp(-t D^2) applied to the polynomial with ascending coefficients."""
    out = np.array(coeffs, dtype=float)
    term = np.array(coeffs, dtype=float)
    k = 0
    while len(term) > 2:
        k += 1
        term = P.polyder(term, 2) * (-t) / k
        out[:len(term)] += term
    return out


def all_real(coeffs, tol=1e-6):
    return bool(np.all(np.abs(P.polyroots(coeffs).imag) < tol))


def test_heat():
    rows = []
    for delta in (0.2, 0.5, 1.0):
        for spacing in (1.0, 3.0):
            reals = spacing * (np.arange(-3, 4) + 0.5)
            roots = np.concatenate([reals, [1j * delta, -1j * delta]])
            p = P.polyfromroots(roots).real
            grid = np.linspace(0, delta ** 2 / 2 * 1.2, 241)
            first = next((float(t) for t in grid if all_real(heat(p, t))), None)
            rows.append({'delta': delta, 'spacing': spacing, 'first_real_t': first,
                         'de_bruijn_t': delta ** 2 / 2,
                         'within_bound': bool(first is not None and first <= delta ** 2 / 2 + grid[1])})
    reals = np.arange(-3, 4) + 0.5
    back = [float(t) for t in (-0.02, -0.05, -0.1, -0.2) if not all_real(heat(P.polyfromroots(reals).real, t))]
    return {'rows': rows, 'backward_times_with_nonreal_roots': back}


def turan_bound(N, m):
    return (N / (8 * math.e * (m + N))) ** N


def test_turan(rng):
    rows = []
    worst = math.inf
    for N in (2, 4, 6, 8):
        for m in (0, 5, 50):
            for trial in range(200):
                if trial % 2:
                    z = rng.uniform(0.3, 1, N) * np.exp(1j * rng.uniform(0, 2 * math.pi, N))
                else:  # close pairs on nearly opposite phases, built to cancel
                    base = np.exp(1j * rng.uniform(0, 2 * math.pi, N // 2))
                    z = np.concatenate([base, -base * np.exp(1j * rng.uniform(-1e-2, 1e-2, N // 2))])
                z = z / np.max(np.abs(z))
                nus = np.arange(m + 1, m + N + 1)
                best = np.max(np.abs((z[None, :] ** nus[:, None]).sum(axis=1)))
                ratio = best / turan_bound(N, m)
                worst = min(worst, ratio)
            rows.append({'N': N, 'm': m, 'bound': turan_bound(N, m)})
    return {'cases': rows, 'trials_per_case': 200, 'least_ratio_of_max_to_bound': float(worst),
            'violations': bool(worst < 1)}


def test_sections(rng):
    rows = []
    for D in (6, 10, 14):
        for h in (0.1, 0.6, 2.0):
            gam = np.sort(rng.uniform(-8, 8, D))
            F = P.polyfromroots(-gam - 1j * h)          # zeros z = -gamma - i h, lower half-plane
            bad = []
            for d in range(2, D):
                r = P.polyroots(F[:d + 1])
                if np.max(r.imag) >= 0:
                    bad.append(int(d))
            rows.append({'degree': D, 'h': h, 'sections_with_upper_zero': bad, 'sections_tested': D - 2})
    return {'rows': rows, 'any_failure': any(r['sections_with_upper_zero'] for r in rows)}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--out', required=True)
    ap.add_argument('--seed', type=int, default=20261011)
    args = ap.parse_args()
    rng = np.random.default_rng(args.seed)
    result = {'seed': args.seed, 'heat': test_heat(), 'turan': test_turan(rng), 'sections': test_sections(rng)}
    with open(args.out, 'w') as fh:
        json.dump(result, fh, indent=1)
    print(json.dumps({'heat_within': [r['within_bound'] for r in result['heat']['rows']],
                      'backward': result['heat']['backward_times_with_nonreal_roots'],
                      'turan_least_ratio': result['turan']['least_ratio_of_max_to_bound'],
                      'sections_any_failure': result['sections']['any_failure']}))


if __name__ == '__main__':
    main()
