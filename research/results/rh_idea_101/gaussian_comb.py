"""A finite Gaussian comb of close points that hides a strictly rightmost point on a window of lengths (model).

Model of the rightmost point window criterion: W the hat function on [0, l], l = log 2,
a(z) = int W(v) e^(zv) dv; points rho_j = beta_0 - c j^2/U + i(tau + j g), |j| <= J, unit multiplicities;
P_J(u) = sum_j a(rho_j - i tau) e^((rho_j - i tau) u). rho_0 is strictly rightmost.

Statement tested (the entry's proposition). With 0 < d < pi, Lam >= 1/2, A = d^2/(4 Lam), a window [U, U + R]
such that g x stays at distance at least d from the multiples of 2 pi for U <= x <= U + R + l,
c = A U/(U + R + l) and J >= sqrt(Lam/c):
    0 <= P_J(u) e^(-beta_0 u)/a(beta_0) + tail,   |P_J(u)| e^(-beta_0 u)/a(beta_0) <= bound + tail
on the window, with bound = 4.2 A^(-1/2) e^(-Lam) and tail = e^(-c J^2)/(c J).
Also the closed form for the full comb: P(u) = int W(v) e^(beta_0 x) Theta(x) dv, x = u + v,
Theta(x) = sqrt(pi U/(c x)) sum_n exp(-U (g x - 2 pi n)^2/(4 c x)).

Computed, for beta_0 = 0.7, U = 20, R = 6, d = 2, g = 0.16, Lam = 8:
(A) hypotheses asserted (the distance d on the whole range of x; A <= d^2/2);
(B) sup over 2001 points of the window of |P_J| e^(-beta_0 u)/a(beta_0), against bound + tail, both printed;
(C) independent route: the full comb by direct summation over |j| <= 400 against the closed form by
    Simpson quadrature in v with the Poisson side of Theta, at 41 points of the window and at 41 points
    around the peak at x = 2 pi/g, where the comb does not hide; largest relative difference printed with
    the size of the quantity;
(D) the criterion of the earlier entry on this configuration: the sum over the other points of
    e^(-(beta_0 - beta_j) U) min(1, 16/(R^2 (j g)^2)), which that criterion says is at least 1 - sup.
Expected before the run: (B) sup <= bound + tail; (C) relative difference below 1e-6 at the peak points and
absolute difference below 1e-9 times e^(beta_0 u) a(beta_0) on the window; (D) the sum is at least 1 - sup;
the value near the peak is above 1, so the window matters.
Refuted by: a window point with |P_J| e^(-beta_0 u)/a(beta_0) above bound + tail; a disagreement of the two
routes above the tolerances; or the criterion's sum below 1 - sup.
Possible because: the bound's constant 4.2 and the tail were derived by hand, the closed form rests on
Poisson summation for a Gaussian with a normalisation I could have wrong, and the earlier criterion is a
separately proved statement."""
import math

import numpy as np

L = math.log(2)


def a(z):
    z = np.asarray(z, dtype=complex)
    return 2 / (L * z * z) * (np.exp(z * L / 2) - 1)**2


def comb(u, beta0, c, U, g, J):
    j = np.arange(-J, J + 1)
    z = beta0 - c * j * j / U + 1j * j * g
    return np.exp(np.outer(u, z)) @ a(z)


def theta(x, c, U, g, terms=40):
    A = c * x / U
    n = np.arange(-terms, terms + 1)
    centre = np.round(g * x / (2 * math.pi))
    return np.sqrt(math.pi / A) * np.exp(-(g * x[:, None] - 2 * math.pi * (centre[:, None] + n))**2
                                         / (4 * A[:, None])).sum(axis=1)


def closed(u, beta0, c, U, g, nodes=2001):
    v = np.linspace(0, L, nodes)
    w = np.ones(nodes)
    w[1:-1:2], w[2:-1:2] = 4, 2
    w *= L / (3 * (nodes - 1))
    hat = 1 - np.abs(2 * v / L - 1)
    out = []
    for u0 in u:
        x = u0 + v
        out.append(float((w * hat * np.exp(beta0 * x) * theta(x, c, U, g)).sum()))
    return np.array(out)


def main():
    beta0, U, R, d, g, lam = 0.7, 20.0, 6.0, 2.0, 0.16, 8.0
    A = d * d / (4 * lam)
    c = A * U / (U + R + L)
    J = math.ceil(math.sqrt(lam / c))
    x = np.linspace(U, U + R + L, 20001)
    distance = np.abs(g * x - 2 * math.pi * np.round(g * x / (2 * math.pi)))
    assert distance.min() >= d and A <= d * d / 2
    print(f'(A) g x in [{g * U:.3f}, {g * (U + R + L):.3f}], least distance from 2 pi Z {distance.min():.4f} >= d = {d}; '
          f'A = {A:.4f}, c = {c:.5f}, J = {J}, points {2 * J + 1}, heights within {J * g:.2f} of tau')
    a0 = a(beta0).real
    u = np.linspace(U, U + R, 2001)
    values = comb(u, beta0, c, U, g, J) * np.exp(-beta0 * u) / a0
    sup = float(np.abs(values).max())
    bound, tail = 4.2 * A**-0.5 * math.exp(-lam), math.exp(-c * J * J) / (c * J)
    print(f'(B) sup |P_J| e^(-beta_0 u)/a(beta_0) on the window = {sup:.4e}; bound {bound:.4e} + tail {tail:.4e} '
          f'= {bound + tail:.4e}; least real part {values.real.min():.3e}')
    assert sup <= bound + tail and values.real.min() >= -tail

    inside = np.linspace(U, U + R, 41)
    direct = comb(inside, beta0, c, U, g, 400)
    form = closed(inside, beta0, c, U, g)
    scale = np.exp(beta0 * inside) * a0
    worst_inside = float((np.abs(direct - form) / scale).max())
    peak = 2 * math.pi / g
    near = np.linspace(peak - L - 1, peak + 1, 41)
    direct_p, form_p = comb(near, beta0, c, U, g, 400), closed(near, beta0, c, U, g)
    worst_peak = float((np.abs(direct_p - form_p) / np.abs(form_p)).max())
    top = float((np.abs(direct_p) * np.exp(-beta0 * near) / a0).max())
    print(f'(C) direct sum against closed form: on the window, largest |difference|/(e^(beta_0 u) a(beta_0)) = '
          f'{worst_inside:.2e}, where the quantity itself is at most {sup:.2e}; near the peak at x = {peak:.3f}, '
          f'largest relative difference {worst_peak:.2e}, the quantity there up to {top:.3f} in the same units')
    assert worst_inside <= 1e-9 and worst_peak <= 1e-6 and top > 1

    j = np.arange(1, J + 1)
    others = float(2 * (np.exp(-c * j * j) * np.minimum(1, 16 / (R * R * (j * g)**2))).sum())
    print(f'(D) the earlier criterion\'s sum over the other points = {others:.4f}; 1 - sup = {1 - sup:.4f}')
    assert others >= 1 - sup


if __name__ == '__main__':
    main()
