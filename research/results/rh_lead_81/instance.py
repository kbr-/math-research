"""Arithmetic for the entry on the cut-grid tail fraction: no statement is tested here.

Evaluates the entry's closed bounds at one instance (the Hann window) and for a taper window with unit ramp,
and compares the tail bound with the tail computed from the window's transform at the instance.
Statement evaluated: for phi real, even, C^1 with phi' absolutely continuous, supported in [-L/2, L/2],
B = int |phi''|, phi^2 >= c0 on |u| <= s, z = gamma - i delta, gamma at distance >= D from both ends of the
grid's interval:  tail/norm <= 2 B^2 e^{delta (L - 2s)} (delta + 1/(4s)) / (3 pi c0 D^3).
Expected before the run: the computed tail fraction at the instance is below the bound, by a wide margin, the
bound using only the decay B/|z|^2."""
import numpy as np

pi = np.pi


def bound(B, L, s, c0, delta, D):
    return 2 * B**2 * np.exp(delta * (L - 2 * s)) * (delta + 1 / (4 * s)) / (3 * pi * c0 * D**3)


def hann_quadrature(z, L):
    """Transform of cos^2(pi u/L) on [-L/2, L/2] at complex z, by quadrature of the definition."""
    u = np.linspace(-L / 2, L / 2, 200001)
    f = np.cos(pi * u / L) ** 2 * np.exp(-1j * u * z)
    return np.sum((f[1:] + f[:-1]) / 2) * (u[1] - u[0])


def hann_hat(z, L):
    """The same in closed form, from cos^2 = 1/2 + cos(2 pi u/L)/2 and the transform 2 sin(zL/2)/z of the
    interval's indicator; z an array of complex numbers away from 0 and +-2 pi/L."""
    flat = lambda x: 2 * np.sin(x * L / 2) / x
    return flat(z) / 2 + (flat(z - 2 * pi / L) + flat(z + 2 * pi / L)) / 4


def main():
    L, delta, s, c0 = 24.0, 0.5, 6.0, 0.25
    B = 4 * pi / L
    lower_norm_integral = c0 * np.sinh(2 * delta * s) / delta
    kappa_lower = lower_norm_integral / (3 * L / 8)
    D_min = (16 * bound(B, L, s, c0, delta, 1.0)) ** (1 / 3)
    print(f'Hann window, L = {L:g}, delta = {delta:g}, s = {s:g}, c0 = {c0:g}: B = {B:.4f}')
    print(f'  kappa >= {kappa_lower:.2f} (needs >= 2)')
    print(f'  tail fraction <= {bound(B, L, s, c0, delta, 1.0):.2f}/D^3; at most 1/16 for D >= {np.ceil(100 * D_min) / 100:.2f} '
          '(rounded up)')
    d, step = 200, 2 * pi / L
    k0 = d // 2
    gamma = k0 * step + 0.1
    D = min(gamma, (d - 1) * step - gamma)
    ks = np.arange(-4000, 4000 + d)
    points = gamma - 1j * delta - ks * step
    for index in (0, len(ks) // 2, len(ks) - 1):
        closed, direct = hann_hat(points[index:index + 1], L)[0], hann_quadrature(points[index], L)
        assert abs(closed - direct) <= 1e-6 * max(1.0, abs(direct)), (closed, direct)
        print(f'  closed form against quadrature at k = {ks[index]}: difference {abs(closed - direct):.1e}, '
              f'size {abs(direct):.1e}')
    values = np.abs(hann_hat(points, L)) ** 2
    inside = (ks >= 0) & (ks < d)
    fraction = values[~inside].sum() / values.sum()
    print(f'  d = {d}, gamma at distance D = {D:.2f} from the ends: computed tail fraction {fraction:.3e}, '
          f'bound {bound(B, L, s, c0, delta, D):.3e}; grid cut at |k| <= 4000 outside')
    assert fraction <= bound(B, L, s, c0, delta, D)
    print('Taper with unit ramp (w = 1, phi = 1 on |u| <= L/2 - 1), delta < 1/2, L >= 8, B = 2 R2, R2 = int |rho\'\'|:')
    coefficient = 2 * 4 * np.e * (0.5 + 1 / 12) / (3 * pi)
    print(f'  tail fraction < {coefficient:.3f} R2^2 / D^3; at most 1/16 for D >= '
          f'{np.ceil(100 * (16 * coefficient) ** (1 / 3)) / 100:.2f} R2^(2/3) (rounded up)')


if __name__ == '__main__':
    main()
