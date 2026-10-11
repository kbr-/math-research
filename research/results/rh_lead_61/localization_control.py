"""Numerical control of the localization lemma for the Gram form.

Setting: phi real, even, supported in [-L/2, L/2], with phi' absolutely continuous and B = int |phi''|;
phihat(z) = int phi(u) e^{-iuz} du; grid tau_k = 2 pi k / L (tau_0 = 0 without loss), c real supported on
0 <= k < d, H_c(tau) = sum_k c_k phihat(tau - tau_k), I = [tau_0, tau_{d-1}].

Statements tested, with the Hann window phi(u) = cos^2(pi u / L), for which B = 4 pi / L:
 D. |phihat(r)| <= B / r^2 for real r != 0.
 T. For R > 0:  int_{dist(tau, I) >= R} H_c(tau)^2 dtau  <=  |c|^2 B^2 (2/(3 R^3) + L/(6 pi R^2)).

Method: phihat by its closed form (L/2) sinc(x) pi^2/(pi^2 - x^2), x = r L/2, which is first compared with a
direct quadrature of the definition at 12 points (expected agreement 1e-9).  The left side of T by the trapezoid
rule on both sides of I from distance R to R + 4000/L with step 0.01/L; the part beyond the cut is left out,
which makes the computed left side smaller, and its size by the statement itself is printed beside it.
Vectors c: 20 random Gaussian ones, the constant one, the alternating one, and for each R the vector aligned with
(phihat(tau* - tau_k))_k at the point tau* at distance R above I, which maximizes |H_c(tau*)| for its norm.

Expected, written before the run: D holds at every sampled r, with the largest value of r^2 |phihat(r)| / B below
1 (the script prints it); T holds in every case, and the largest ratio of the two sides is printed: the bound
comes from Cauchy-Schwarz at each tau separately and is not expected to be close to attained, so ratios far
below 1 are expected, and I expect the aligned vectors to give the largest.
No negative control is run: the bound is not tight, so an altered constant or exponent need not fail, and a
control that cannot be asserted to differ is not one.  What the run can show is a violation.
"""
import math

import numpy as np
from scipy.integrate import quad

L, D_GRID = 12.0, 40
B = 4 * math.pi / L
TAU = 2 * math.pi * np.arange(D_GRID) / L


def phihat(r):
    x = np.asarray(r, dtype=float) * L / 2
    with np.errstate(divide='ignore', invalid='ignore'):
        value = (L / 2) * np.sinc(x / math.pi) * math.pi ** 2 / (math.pi ** 2 - x ** 2)
    return np.where(np.abs(np.abs(x) - math.pi) < 1e-9, L / 4, value)


def direct(r):
    return quad(lambda u: math.cos(math.pi * u / L) ** 2 * math.cos(u * r), -L / 2, L / 2, limit=400)[0]


def tail(c, radius):
    step, span = 0.01 / L, 4000.0 / L
    offsets = radius + np.arange(0, span, step)
    total = 0.0
    for points in (TAU[-1] + offsets, TAU[0] - offsets):
        values = (phihat(points[:, None] - TAU[None, :]) @ c) ** 2
        total += float(np.sum((values[1:] + values[:-1]) / 2) * step)
    return total


def main():
    worst = max(abs(direct(r) - float(phihat(r))) for r in (0.0, 0.1, 0.37, 0.9, 1.3, 2.0, 3.3, 5.1, 8.0, 13.7, 21.0, 40.0))
    print(f'closed form of phihat against quadrature at 12 points: largest difference {worst:.1e} (expected below 1e-9)')
    r = np.linspace(0.01, 400.0, 400000)
    decay = float(np.max(r ** 2 * np.abs(phihat(r)) / B))
    print(f'D: largest r^2 |phihat(r)| / B on (0, 400]: {decay:.4f}: ' + ('holds' if decay <= 1 else 'FAILS'))

    rng = np.random.default_rng(20261011)
    vectors = [('random', rng.standard_normal(D_GRID)) for _ in range(20)]
    vectors += [('constant', np.ones(D_GRID)), ('alternating', (-1.0) ** np.arange(D_GRID))]
    largest, where, cases = 0.0, None, 0
    for radius in (0.5, 1.0, 2.0, 5.0, 12.0, 30.0):
        aligned = phihat(TAU[-1] + radius - TAU)
        bound_unit = B ** 2 * (2 / (3 * radius ** 3) + L / (6 * math.pi * radius ** 2))
        cut = radius + 4000.0 / L
        beyond = B ** 2 * (2 / (3 * cut ** 3) + L / (6 * math.pi * cut ** 2)) / bound_unit
        for name, c in vectors + [('aligned', aligned)]:
            ratio = tail(c, radius) / (float(c @ c) * bound_unit)
            cases += 1
            if ratio > largest:
                largest, where = ratio, (name, radius)
        print(f'R={radius}: bound per |c|^2 = {bound_unit:.3e}; the part beyond the cut is at most {beyond:.1e} of it')
    print(f'T: {cases} cases; largest ratio of the two sides {largest:.3e} at {where}: '
          + ('holds' if largest <= 1 else 'FAILS'))


if __name__ == '__main__':
    main()
