"""Arithmetic for the entry on the on-line cut-form bound: two series constants and one instance.

Statement evaluated: for real points with at most A log(|t| + 3) of them in every closed interval [t, t+1],
a window phi (real, even, C^1 with phi' absolutely continuous, supported in [-L/2, L/2], B = int |phi''|,
B2 = int |(phi^2)''|), grid tau_k = tau_0 + 2 pi k/L, 0 <= k < d, M = max(|tau_0|, |tau_{d-1}|):
  lambda_max of sum_gamma v_gamma v_gamma^T on the cut grid, divided by L ||phi||_2^2, is at most
  Lambda0 = 2 A log(M + 5) (1 + (pi^2/6) B2/||phi||_2^2 + B^2 (c4/L + c3/(6 pi))/||phi||_2^2),
  c4 = sum_{j>=1} (1 + log j) j^-4, c3 = sum_{j>=1} (1 + log j) j^-3.
Expected before the run: c4 < 1.16 and c3 < 1.41; at the instance (the integers, Hann window) the computed
largest eigenvalue is below the bound by a factor of several, the bound using absolute row sums and a
logarithm that the integers do not need."""
import numpy as np

pi = np.pi


def series(power, terms=10**6):
    """sum_{j>=1} (1 + log j) j^-power with an upper bound for the tail by an integral."""
    j = np.arange(1, terms + 1, dtype=float)
    partial = np.sum((1 + np.log(j)) * j**-power)
    n, p = float(terms), power - 1
    tail = (1 + np.log(n)) * n**-p / p + n**-p / p**2      # int_n^inf (1 + log x) x^-power dx
    return partial, partial + tail


def hann_hat(z, L):
    flat = lambda x: 2 * np.sin(x * L / 2) / x
    return flat(z) / 2 + (flat(z - 2 * pi / L) + flat(z + 2 * pi / L)) / 4


def main():
    low4, c4 = series(4)
    low3, c3 = series(3)
    print(f'c4 in [{low4:.5f}, {c4:.5f}], c3 in [{low3:.5f}, {c3:.5f}]; c3/(6 pi) <= {c3 / (6 * pi):.5f}')
    assert c4 < 1.16 and c3 < 1.41
    L, d, tau0 = 24.0, 200, 16.0
    step = 2 * pi / L
    taus = tau0 + step * np.arange(d)
    M = taus[-1]
    norm2 = 3 * L / 8                       # int cos^4(pi u/L) over [-L/2, L/2]
    B = 4 * pi / L                          # int |phi''| for the Hann window
    u = np.linspace(-L / 2, L / 2, 400001)
    second = np.gradient(np.gradient(np.cos(pi * u / L) ** 4, u), u)
    B2 = np.sum(np.abs(second[1:] + second[:-1]) / 2) * (u[1] - u[0])
    A = 2 / np.log(3)                       # the integers: at most 2 in [t, t+1], and log(|t| + 3) >= log 3
    bound = 2 * A * np.log(M + 5) * (1 + (pi**2 / 6) * B2 / norm2 + B**2 * (c4 / L + c3 / (6 * pi)) / norm2)
    points = np.arange(int(np.floor(tau0)) - 400, int(np.ceil(M)) + 401) + 0.3   # shifted off the grid's poles
    V = hann_hat(points[None, :] - taus[:, None], L)
    form = V @ V.T / (L * norm2)
    top = np.linalg.eigvalsh(form)[-1]
    print(f'Hann window, L = {L:g}, d = {d}, tau_0 = {tau0:g}, M = {M:.2f}: ||phi||^2 = {norm2:g}, B = {B:.4f}, '
          f'B2 = {B2:.4f} (quadrature)')
    print(f'  points: the integers shifted by 0.3, {len(points)} of them within 400 of the interval; A = {A:.4f}')
    print(f'  normalized largest eigenvalue of the cut form: {top:.4f}; bound Lambda0 = {bound:.2f}')
    assert top <= bound


if __name__ == '__main__':
    main()
