"""The lower bound for the Gram form on the binomial family, on instances inside its stated range.

Model as in research/results/rh_lead_90/cluster_form.py: flat window, complete grid, L = 1, points
z_j = j pi -+ i b with multiplicities binom(k, j). Statement of the entry: if b >= 4(k+1),
b^2 >= (4 pi^2/3) k (k+1)^2 and e^b >= 6e 2^(k+2) (k+1) e^(2k+2) (b/pi)^k/k!, then
-lambda_min(B) >= c0 U with U = (2 e^b/b) k! (pi/b)^k and c0 = 1/(12e).
Its proof evaluates the form at f(t) = i e^{i gamma_c t} o(t), gamma_c = k pi/2, o(t) = G(1/2 - t) - G(1/2 + t),
G(u) = e^{-eta u} on [0, w], eta = b/(k+1), w = 2(k+1)/b, and claims the form there is
Q = -(I_pp - I_pm)/||G||^2 with I_pp = iint G G K(1 - u - u'), I_pm = iint G(u) G(u') K(u' - u),
K(S) = (2 cos(pi S/2))^k 2 cosh(b S).

Evaluated for each instance: the three conditions (asserted, the instances being chosen inside the range);
lambda_min(B) from the matrix of sinc values; Q by the formula above (two-dimensional Gauss-Legendre); Q again,
not sharing that formula, as sum_z m_z F(z)^2/||f||^2 with F(z) = int f(t) e^{-izt} dt by one-dimensional
Gauss-Legendre; and U.
Expected before the run: the two values of Q agree to a relative 1e-8; lambda_min(B) <= Q < 0; -Q >= c0 U in
every instance (asserted); and -lambda_min(B)/U between c0 and 1."""
import math

import numpy as np

C0 = 1 / (12 * math.e)


def sinc(x):
    x = np.asarray(x, dtype=complex)
    return np.where(x == 0, 1, np.sin(x) / np.where(x == 0, 1, x))


def smallest(b, k):
    points = [j * math.pi - 1j * b for j in range(k + 1)]
    weights = [math.comb(k, j) for j in range(k + 1)]
    z = np.array(points + [p.conjugate() for p in points])
    root = np.sqrt(np.array(weights + weights, dtype=float))
    values = np.linalg.eigvals(root[:, None] * root[None, :] * sinc((z[:, None] - z[None, :]) / 2))
    assert np.abs(values.imag).max() <= 1e-6 * np.abs(values).max()
    return values.real.min()


def form_values(b, k, nodes=600):
    eta, w, gamma_c = b / (k + 1), 2 * (k + 1) / b, k * math.pi / 2
    x, weight = np.polynomial.legendre.leggauss(nodes)
    u, du = (x + 1) * w / 2, weight * w / 2                      # nodes on [0, w]
    G = np.exp(-eta * u)
    norm = (du * G * G).sum()                                    # ||G||^2; ||o||^2 = ||f||^2 = 2 ||G||^2

    def K(S):
        return (2 * np.cos(math.pi * S / 2))**k * 2 * np.cosh(b * S)
    W = (du * G)[:, None] * (du * G)[None, :]
    I_pp = (W * K(1 - u[:, None] - u[None, :])).sum()
    I_pm = (W * K(u[None, :] - u[:, None])).sum()
    by_formula = -(I_pp - I_pm) / norm
    # directly: f on the two pieces t = 1/2 - u (o = G) and t = -1/2 + u (o = -G)
    t = np.concatenate([0.5 - u, -0.5 + u])
    f = 1j * np.exp(1j * gamma_c * t) * np.concatenate([G, -G])
    dt = np.concatenate([du, du])
    total = 0
    for j in range(k + 1):
        for sign in (-1, 1):
            z = j * math.pi + sign * 1j * b
            total += math.comb(k, j) * ((dt * f * np.exp(-1j * z * t)).sum())**2
    direct = total / (2 * norm)
    assert abs(direct.imag) <= 1e-8 * abs(direct.real)
    return by_formula, direct.real


def main():
    print('b  k | conditions: 4(k+1), sqrt((4 pi^2/3) k (k+1)^2), log of the third\'s right side | '
          'lambda_min(B)   Q by formula   Q directly   U   -Q/U   -lambda_min/U   (c0 = %.4f)' % C0)
    for k, bs in ((1, (11, 12, 14, 18, 24)), (2, (16, 18, 22, 26)), (3, (26, 30))):      # (22, 3), in the first run, is outside the second condition
        for b in bs:
            third = math.log(6 * math.e * 2**(k + 2) * (k + 1)) + 2 * k + 2 + k * math.log(b / math.pi) \
                - math.log(math.factorial(k))
            second = math.sqrt(4 * math.pi**2 / 3 * k * (k + 1)**2)
            assert b >= 4 * (k + 1) and b >= second and b >= third, (b, k, second, third)
            low = smallest(float(b), k)
            by_formula, direct = form_values(float(b), k)
            U = 2 * math.exp(b) / b * math.factorial(k) * (math.pi / b)**k
            assert abs(by_formula - direct) <= 1e-8 * abs(direct)
            assert low <= direct * (1 - 1e-9) < 0 and -direct >= C0 * U
            assert -low <= U        # the upper bound of the earlier entry's part (3), which its script did not assert
            print(f'{b:2d} {k} | {4 * (k + 1):2d} {second:6.2f} {third:6.2f} | {low:14.6e} {by_formula:14.6e} '
                  f'{direct:14.6e} {U:12.6e} {-direct / U:7.4f} {-low / U:7.4f}')


def doubled():
    """Added after the first version's runs, for part (4) of the entry: the same points, built for bandwidth 1,
    in the form at bandwidth 2 (matrix entries sqrt(m m') sinc(z - w)).  Statement: if b >= 3.4 and
    b^2 >= 4 pi^2 k, the smallest eigenvalue is at most -0.1 2^k e^(2b)/b.  Expected before the run: the
    assertion holds in every instance, and the ratio of -lambda_min to 2^k (sinh(2b)/(2b) - 1), the value for
    one pair of multiplicity 2^k at that bandwidth, lies between 0.4 and 1."""
    print('twice the bandwidth: b  k | sqrt(4 pi^2 k) | lambda_min   -0.1 2^k e^(2b)/b   ratio to one pair of 2^k')
    for k, bs in ((1, (7, 9, 12)), (2, (9, 12, 15)), (3, (11, 14)), (4, (13, 16))):
        for b in bs:
            assert b >= 3.4 and b * b >= 4 * math.pi**2 * k
            points = [j * math.pi - 1j * b for j in range(k + 1)]
            weights = [math.comb(k, j) for j in range(k + 1)]
            z = np.array(points + [p.conjugate() for p in points])
            root = np.sqrt(np.array(weights + weights, dtype=float))
            values = np.linalg.eigvals(root[:, None] * root[None, :] * sinc(z[:, None] - z[None, :]))
            assert np.abs(values.imag).max() <= 1e-6 * np.abs(values).max()
            low, bound = values.real.min(), -0.1 * 2**k * math.exp(2 * b) / b
            one = 2**k * (math.sinh(2 * b) / (2 * b) - 1)
            assert low <= bound
            print(f'{b:2d} {k} | {math.sqrt(4 * math.pi**2 * k):5.2f} | {low:14.6e} {bound:14.6e} {-low / one:7.4f}')


if __name__ == '__main__':
    main()
    doubled()
