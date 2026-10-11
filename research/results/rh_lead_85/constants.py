"""Arithmetic for the entry on the tilted inequality's reach: constants of its proof and one instance.

F(w) = int_0^L (1 - u/L) e^{-wu} du = 1/w - (1 - e^{-wL})/(L w^2); Phi(x) = F(-x) = (e^{xL} - 1 - xL)/(L x^2).
Statements evaluated: (a) Re F(w) >= 0 on Re w >= 0, sampled; (b) the constants 1 - 3 e^{-2}, the bound of the
pole's terms at |tau| >= 6p by 0.75 Phi(p) for pL >= 2, and the threshold 2.25 (1 - 3 e^{-2})/8; (c) the root
y0 of (e^y - 1 - y)/y^2 = 2/3; (d) for the binomial family, k + 1 points at one distance with multiplicities
binom(k, j) and heights j pi/L, the combination T(tau) of the entry against its lower bound, on a grid of tau.
Expected before the run: (a) minimum of Re F over the sample is >= 0 up to rounding, attained near the
imaginary axis; (b) the two numerical inequalities hold with a small margin; (c) y0 between 0.80 and 0.82;
(d) T(tau) >= its lower bound at every sampled tau, and T > 0 where the entry's sufficient condition holds."""
import math

import numpy as np


def F(w, L):
    w = np.asarray(w, dtype=complex)
    return 1 / w - (1 - np.exp(-w * L)) / (L * w**2)


def Phi(x, L):
    return (math.exp(x * L) - 1 - x * L) / (L * x**2)


def main():
    L = 20.0
    xs, ys = np.meshgrid(np.linspace(0.0, 3.0, 301), np.linspace(0.013, 60.0, 6001))
    values = F(xs + 1j * ys, L).real
    at = np.unravel_index(values.argmin(), values.shape)
    print(f'(a) L = {L:g}: min Re F on 0 <= x <= 3, 0.013 <= y <= 60 is {values.min():.3e} at x = {xs[at]:.2f}, '
          f'y = {ys[at]:.3f}; max |F| there {np.abs(F(xs + 1j * ys, L)).max():.3f} against L/2 = {L / 2:g}')
    assert values.min() >= -1e-12
    lower = 1 - 3 * math.exp(-2)
    pole = 8.5 / 36 / lower + 0.75 / (lower * math.exp(2) / 2)
    print(f'(b) 1 - 3 e^-2 = {lower:.4f}; pole terms at |tau| >= 6p over Phi(p), for pL >= 2: at most {pole:.4f} '
          f'(claimed 0.75); threshold constant 8/(2.25 (1 - 3 e^-2)) = {8 / (2.25 * lower):.3f} (claimed at most 6)')
    assert pole <= 0.75 and 8 / (2.25 * lower) <= 6
    lo, hi = 0.1, 2.0
    for _ in range(60):
        mid = (lo + hi) / 2
        lo, hi = (mid, hi) if (math.exp(mid) - 1 - mid) / mid**2 < 2 / 3 else (lo, mid)
    print(f'(c) root of (e^y - 1 - y)/y^2 = 2/3: y0 = {lo:.4f}')
    assert 0.80 < lo < 0.82
    print('(d) binomial family, heights j pi/L, multiplicities binom(k, j), one distance delta, tilt a:')
    for delta, a, k in ((0.30, 0.0, 2), (0.30, 0.0, 4), (0.40, 0.1, 3), (0.45, 0.2, 4)):
        p, c, M = 0.5 - a, delta - a, 2**k
        weights = [math.comb(k, j) for j in range(k + 1)]
        taus = np.linspace(6 * p, 6 * p + 40.0, 40001)
        gamma0 = 6 * p + 20.0      # the cluster's heights lie inside the grid of tau, so resonance is sampled

        def zeros(t):
            return sum(m * F(-c + 1j * (t - gamma0 - j * math.pi / L), L).real for j, m in enumerate(weights))
        T = (3 * Phi(p, L) + 4 * F(-p + 1j * taus, L).real + F(-p + 2j * taus, L).real
             - 3 * zeros(0 * taus) - 4 * zeros(taus) - zeros(2 * taus))
        bound = 2.25 * Phi(p, L) - 8 * M * Phi(c, L)
        needed = math.log(6 * M) + 2 * math.log(p / c)
        single = (3 * Phi(p, L) + 4 * F(-p + 1j * taus, L).real + F(-p + 2j * taus, L).real
                  - M * (3 * F(-c + 1j * (0 * taus - gamma0), L).real + 4 * F(-c + 1j * (taus - gamma0), L).real
                         + F(-c + 1j * (2 * taus - gamma0), L).real))
        print(f'    delta = {delta}, a = {a}, k = {k}, M = {M}: (1/2 - delta) L = {(0.5 - delta) * L:.2f}, sufficient '
              f'{needed:.2f}; min T = {T.min():.3e} at tau - gamma0 = {taus[T.argmin()] - gamma0:.3f}, lower bound '
              f'{bound:.3e}, Phi(p) = {Phi(p, L):.3e}; the same M at one height: min T = {single.min():.3e}')
        assert T.min() >= bound - 1e-9 * abs(bound)


if __name__ == '__main__':
    main()
