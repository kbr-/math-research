"""Control for the strip positivity obstruction (riemann notebook, 11 October 2026).

Statement tested.  For continuous even real g of compact support with Re h >= 0 on |Im z| <= 1/2, h the
transform int g(u) e^{izu} du:  Re h(t + iy) = (1/2pi) int phi(s) K_y(t - s) ds with phi(s) = Re h(s + i/2)
and K_y(t) = 2 pi cos(pi y) cosh(pi t)/(sinh^2(pi t) + cos^2(pi y)), and hence
    Re h(gamma + i y) >= cos(pi y) cos(pi delta) exp(-pi |gamma - gamma0|) Re h(gamma0 + i delta).
Checks: (1) K_y against quadrature of int cosh(yu)/cosh(u/2) cos(tu) du; (2) the kernel inequality on a grid;
(3) the final inequality for test functions g = G/cosh(u/2), G a triangle times (1 + cos(a u))/2, which is
positive definite (hypothesis also asserted: phi >= 0 on a grid), computed from g without the kernel; a
violation in (2) or (3) falsifies the lemma.  Pairs whose bound is below 1e-9 are skipped and counted.
"""
import argparse
import json
import math

import numpy as np
from scipy.integrate import quad


def K(y, t):
    return 2 * math.pi * math.cos(math.pi * y) * math.cosh(math.pi * t) / (
        math.sinh(math.pi * t) ** 2 + math.cos(math.pi * y) ** 2)


def K_quad(y, t):
    def m(u):   # cosh(yu)/cosh(u/2) without overflow
        return (math.exp((y - 0.5) * u) + math.exp(-(y + 0.5) * u)) / (1 + math.exp(-u))
    if t == 0:
        val, _ = quad(m, 0, math.inf, limit=400)
    else:       # Fourier integral over a half-line, QUADPACK's oscillatory rule
        val, _ = quad(m, 0, math.inf, weight='cos', wvar=t, limit=400)
    return 2 * val


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--out', required=True)
    args = ap.parse_args()
    rng = np.random.default_rng(20261011)
    kernel = max(abs(K(y, t) - K_quad(y, t)) / K(y, t)
                 for y in (0.0, 0.2, 0.4, 0.49) for t in (0.0, 0.3, 1.0, 2.5))
    worst = math.inf
    for y1 in np.linspace(0, 0.499, 12):
        for d0 in np.linspace(0, 0.499, 12):
            for t in np.linspace(-4, 4, 41):
                for d in np.linspace(-3, 3, 25):
                    worst = min(worst, K(y1, t + d) / (math.cos(math.pi * y1) * math.cos(math.pi * d0)
                                                       * math.exp(-math.pi * abs(d)) * K(d0, t)))
    # End to end: G(u) = tri(u/L) * (1 + cos(a u))/2-type positive-definite functions, g = G/cosh(u/2).
    u = np.linspace(-12, 12, 48001)
    du = u[1] - u[0]
    rows = []
    for trial in range(40):
        L = rng.uniform(4, 12)
        a = rng.uniform(5, 40)
        G = np.clip(1 - np.abs(u) / L, 0, None) * (1 + np.cos(a * u)) / 2
        g = G / np.cosh(u / 2)

        def reh(t, y):
            return float(np.sum(g * np.cosh(y * u) * np.cos(t * u)) * du)
        s = np.linspace(-60, 60, 601)
        phi_min = min(reh(x, 0.5) for x in s)
        g0, dl = rng.uniform(a - 2, a + 2), rng.uniform(0.05, 0.45)
        base = reh(g0, dl)
        ratio = math.inf
        used = 0
        for _ in range(30):
            gam, y = g0 + rng.uniform(-3, 3), rng.uniform(0, 0.49)
            bound = math.cos(math.pi * y) * math.cos(math.pi * dl) * math.exp(-math.pi * abs(gam - g0)) * base
            if bound > 1e-9:
                used += 1
                ratio = min(ratio, reh(gam, y) / bound)
        rows.append({'L': L, 'a': a, 'gamma0': g0, 'delta': dl, 'phi_min_on_grid': phi_min,
                     'value_at_point': base, 'least_ratio': ratio, 'pairs_used': used})
    result = {'kernel_max_relative_error': kernel, 'kernel_inequality_least_ratio': worst, 'rows': rows,
              'hypothesis_phi_nonnegative': bool(min(r['phi_min_on_grid'] for r in rows) > -1e-6),
              'pairs_used': sum(r['pairs_used'] for r in rows), 'pairs_drawn': 30 * len(rows),
              'least_ratio_end_to_end': min(r['least_ratio'] for r in rows)}
    with open(args.out, 'w') as fh:
        json.dump(result, fh, indent=1)
    print(json.dumps({k: v for k, v in result.items() if k != 'rows'}))


if __name__ == '__main__':
    main()
