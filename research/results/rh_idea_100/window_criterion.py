"""The rightmost-point window criterion for prime sums at one height, in a model, and the progression that hides.

Model: points rho = beta + i gamma with multiplicities m; a weight W >= 0 on [0, l], here the hat function on
[0, log 2], a(z) = int W(v) e^(zv) dv = (2/(l z^2)) (e^(zl/2) - 1)^2; tau real;
P(u) = sum m a(rho - i tau) e^((rho - i tau) u), the zeros' side of a weighted prime sum at height tau and
length e^u.

Statement tested (the entry's proposition, part 1): if rho_0 = beta_0 + i tau has multiplicity m_0 and every
point has beta <= beta_0, then for every window [U1, U1 + R], U1 >= 0,
    m_0 <= sup over the window of |P(u)| e^(-beta_0 u) / a(beta_0)
           + sum over the other points of m e^(-(beta_0 - beta) U1) min(1, 16/(R^2 (gamma - tau)^2)).
Part 2: for the points beta_0 + i(tau + j g), j an integer, unit multiplicities, P(u) = (2 pi/g) sum over
integers n of W(n 2 pi/g - u) e^(beta_0 n 2 pi/g), so P vanishes on every window that keeps a distance l from
the next multiple of 2 pi/g above it.

Computed. (A) 200 random configurations of 41 points (beta_0 = 0.8 at height tau, the others with
beta in [0.5, 0.8], heights within 30 of tau, multiplicities 1 to 3, windows with U1 in [5, 40] and R in
[2, 30]): the right side with the supremum taken over 4001 points of the window; asserted m_0 <= right side
plus 1e-9; printed, the least value of right side minus m_0 and the number of configurations in which the sum
alone is below m_0 (only those test the supremum term).
(B) The progression with beta_0 = 0.7, g = 0.5, |j| <= 20000: on a window between two multiples of the
period, sup |P| e^(-beta_0 u)/a(beta_0) against the truncation's size (sum of |a| over |j| > 20000, bounded by
the integral); and at 201 points near a multiple of the period, P against the closed form of part 2.
Expected before the run: (A) holds in all 200, with the sum alone below m_0 in at least 20 of them; (B) the
supremum on the hidden window is below ten times the truncation bound and below 1e-3, and the closed form
agrees to a relative 1e-3 where it is not zero.
Refuted by: a configuration in (A) with m_0 above the right side; or in (B) a value on the hidden window above
ten times the truncation bound, or a disagreement with the closed form above a relative 1e-3.
Possible because: the criterion was derived by hand with two integrations by parts and a bound for the
weight's transform, and the progression's vanishing rests on Poisson summation with a truncated sum."""
import math

import numpy as np

L = math.log(2)


def a(z):
    z = np.asarray(z, dtype=complex)
    small = np.abs(z) < 1e-8
    safe = np.where(small, 1, z)
    return np.where(small, L / 2, 2 / (L * safe * safe) * (np.exp(safe * L / 2) - 1)**2)


def W(v):
    return np.where((v >= 0) & (v <= L), 1 - np.abs(2 * v / L - 1), 0.0)


def P(u, beta, lam, m):
    """sum m a(beta + i lam) e^((beta + i lam) u) for an array u; lam = gamma - tau."""
    coefficient = m * a(beta + 1j * lam)
    return np.exp(np.outer(u, beta + 1j * lam)) @ coefficient


def main():
    rng = np.random.default_rng(20261012)
    beta0, least, tested = 0.8, math.inf, 0
    for _ in range(200):
        n = 40
        beta = np.concatenate([[beta0], rng.uniform(0.5, beta0, n)])
        lam = np.concatenate([[0.0], rng.uniform(-30, 30, n)])
        m = np.concatenate([[rng.integers(1, 4)], rng.integers(1, 4, n)]).astype(float)
        U1, R = rng.uniform(5, 40), rng.uniform(2, 30)
        u = np.linspace(U1, U1 + R, 4001)
        sup = float(np.abs(P(u, beta, lam, m) * np.exp(-beta0 * u)).max() / a(beta0).real)
        others = float((m[1:] * np.exp(-(beta0 - beta[1:]) * U1)
                        * np.minimum(1, 16 / (R * R * lam[1:]**2))).sum())
        assert m[0] <= sup + others + 1e-9, (m[0], sup, others)
        least = min(least, sup + others - m[0])
        tested += others < m[0]
    print(f'(A) 200 configurations: least value of right side minus m_0 = {least:.4f}; '
          f'the sum alone is below m_0 in {tested}')
    assert tested >= 20

    beta0, g, J = 0.7, 0.5, 20000
    period = 2 * math.pi / g
    j = np.arange(-J, J + 1)
    beta, lam, m = np.full(j.size, beta0), g * j, np.ones(j.size)
    truncation = 2 * (2 / L) * (math.exp(beta0 * L / 2) + 1)**2 / (g * g * J) / a(beta0).real
    u = np.linspace(period + 0.1, 2 * period - L - 0.1, 2001)
    hidden = float(np.abs(P(u, beta, lam, m) * np.exp(-beta0 * u)).max() / a(beta0).real)
    print(f'(B) period {period:.4f}; hidden window of length {u[-1] - u[0]:.4f}, R g = {(u[-1] - u[0]) * g:.3f}; '
          f'sup |P| e^(-beta_0 u)/a(beta_0) = {hidden:.3e}; truncation bound {truncation:.3e}')
    assert hidden <= 10 * truncation and hidden <= 1e-3
    u = np.linspace(2 * period - L + 0.05, 2 * period - 0.05, 201)
    closed = period * W(2 * period - u) * math.exp(beta0 * 2 * period)
    got = P(u, beta, lam, m)
    worst = float(np.abs(got - closed).max() / np.abs(closed).max())
    print(f'    near the multiple: largest |P - closed form| relative to the largest closed value = {worst:.3e}; '
          f'the closed form there is {np.abs(closed).max() * math.exp(-beta0 * 2 * period) / a(beta0).real:.3f} '
          f'in the units of the hidden window')
    assert worst <= 1e-3


if __name__ == '__main__':
    main()
