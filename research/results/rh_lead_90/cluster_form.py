"""The Gram form's smallest eigenvalue on the hidden binomial family, against the form's diagonal.

Model: flat window, complete grid, bandwidth L (scaled to L = 1, so delta = b). Off-axis points
z_j = j pi - i b, 0 <= j <= k, with their conjugates, multiplicities binom(k, j), M = 2^k, kappa = sinh(b)/b.
The off-axis part of the normalized form has the nonzero eigenvalues of the (2k+2) x (2k+2) matrix
B[z, w] = sqrt(m_z m_w) sinc((z - w)/2), sinc(x) = sin(x)/x (the entry's lemma), and its diagonal at a real
height tau is d(tau) = 2 sum_j m_j Re sinc((tau - z_j)/2)^2, the one-sided density divided by L. A real lattice
of spacing s <= 2 pi adds the constant 2 pi/s to both. So the family is hidden from the diagonal behind a
lattice exactly when 2 pi/s >= -min d, and from the form's sign exactly when 2 pi/s >= -lambda_min(B).

Computed for b = 4..14 and k = 1..4, the item's k = floor(b/pi) marked: lambda_min(B); min over tau of d(tau)
on a grid; the single point of the same total multiplicity, -M (kappa - 1); the heaviest point alone,
-max_j m_j (kappa - 1); the record's hiding bound for the diagonal, (2 e^b/b^2)(k+1)! (pi/b)^k + 6 2^k/b^2.
Control, not sharing the lemma: for (b, k) = (6, 1) and (8, 2) the same eigenvalue from the real vectors
themselves on the grid truncated at |n| <= 400000, as the smallest eigenvalue of Gamma J, Gamma the real Gram
matrix of the vectors' real and imaginary parts and J the signs.

Expected before the run: (1) the control agrees with lambda_min(B) to a relative 1e-3 (the truncation error is
of order 1/N times e^b); (2) lambda_min(B) <= min d in every case, as a smallest eigenvalue against a Rayleigh
quotient; (3) -lambda_min(B) is below half of M (kappa - 1) at k = floor(b/pi) for every b, the leading term
cancelling as it does on the diagonal; (4) my guess, on which nothing rests: the ratio lambda_min(B)/min d
lies between 1 and 10, the form seeing little more than its diagonal."""
import math

import numpy as np


def sinc(x):
    x = np.asarray(x, dtype=complex)
    return np.sin(x) / x if np.all(x != 0) else np.where(x == 0, 1, np.sin(x) / np.where(x == 0, 1, x))


def family(b, k):
    points = [j * math.pi - 1j * b for j in range(k + 1)]
    weights = [math.comb(k, j) for j in range(k + 1)]
    return points + [p.conjugate() for p in points], weights + weights


def smallest(b, k):
    points, weights = family(b, k)
    z = np.array(points)
    root = np.sqrt(np.array(weights, dtype=float))
    B = root[:, None] * root[None, :] * sinc((z[:, None] - z[None, :]) / 2)
    values = np.linalg.eigvals(B)
    assert np.abs(values.imag).max() <= 1e-6 * np.abs(values).max(), (b, k, values)
    return values.real.min(), values.real.max()


def diagonal(b, k):
    taus = np.linspace(-6 * math.pi, (k + 6) * math.pi, 240001)
    d = sum(2 * math.comb(k, j) * (sinc((taus - (j * math.pi - 1j * b)) / 2)**2).real for j in range(k + 1))
    return d.min(), taus[d.argmin()]


def control(b, k, N=400000):
    points, weights = family(b, k)
    alpha = 2 * math.pi * np.arange(-N, N + 1)
    half = len(points) // 2
    rows, signs = [], []
    for point, weight in zip(points[:half], weights[:half]):
        v = sinc((point - alpha) / 2)
        rows += [math.sqrt(2 * weight) * v.real, math.sqrt(2 * weight) * v.imag]
        signs += [1.0, -1.0]
    R = np.array(rows)
    return np.linalg.eigvals((R @ R.T) * np.array(signs)[None, :]).real.min()


def main():
    for b, k in ((6.0, 1), (8.0, 2)):
        exact, truncated = smallest(b, k)[0], control(b, k)
        print(f'control b = {b:g}, k = {k}: lambda_min from the matrix {exact:.6f}, from the truncated grid '
              f'{truncated:.6f}, relative difference {abs(exact - truncated) / abs(exact):.2e}')
        assert abs(exact - truncated) <= 1e-3 * abs(exact)
    print('b  k  M  item | lambda_min(B)  min d (at tau)  -M(kappa-1)  -max m (kappa-1)  -record bound | '
          'lambda_min/min d  -lambda_min/(M(kappa-1))')
    for b in range(4, 15):
        for k in range(1, 5):
            low, _ = smallest(float(b), k)
            d, at = diagonal(float(b), k)
            kappa, M = math.sinh(b) / b, 2**k
            record = 2 * math.exp(b) / b**2 * math.factorial(k + 1) * (math.pi / b)**k + 6 * M / b**2
            assert low <= d + 1e-9 * abs(d)
            assert d >= -record * (1 + 1e-9)
            print(f'{b:2d} {k} {M:2d} {"*" if k == int(b // math.pi) else " "} | {low:12.4f} {d:12.4f} '
                  f'({at:6.3f}) {-M * (kappa - 1):12.4f} {-max(math.comb(k, j) for j in range(k + 1)) * (kappa - 1):12.4f} '
                  f'{-record:12.4f} | {low / d:8.3f} {-low / (M * (kappa - 1)):8.4f}')


if __name__ == '__main__':
    main()
