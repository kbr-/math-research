"""The tilted three-four-one function T_S for a configuration with a local count, at a negative tilt.

Statement tested (the entry's proposition): tilt a in (-1/2, 1/2), p = 1/2 - a; S a multiset of points
1/2 + d + i g with a < d <= delta < 1/2, c = delta - a, such that for every real t the points with |g - t| <= 1
number at most kappa log(|t| + 3) with multiplicity.  If cL >= 2, |tau| >= 6p and
    (1/2 - delta) L >= log(kappa (87 + 33 log(|tau| + 4))) + 2 log(p/c),
then T_S(tau) >= 0, where, with F(w) = int_0^L (1 - u/L) e^(-wu) du,
    T_S(tau) = 3 F(-p) + 4 Re F(-p + i tau) + Re F(-p + 2 i tau)
               - sum_S m [3 Re F(a - d - i g) + 4 Re F(a - d + i(tau - g)) + Re F(a - d + i(2 tau - g))].
Its proof bounds each point's term by b(u) = min(Phi(c), K/u^2), K = c + (1 + e^(cL))/L, Phi(c) = F(-c), and
uses the constants lambda = 1 - 3/e^2, K <= 2.37 c^2 Phi(c) for cL >= 2, and sum_{k>=1} log(1 + k)/k^2 <= 1.9.

Instance: a = -0.1, delta = 0.2, kappa = 3; S = the on-line points 1/2 + i(j + 1/2), |j| <= 4000, with one pair
1/2 + 0.2 +- 50 i; L = 27.  Computed: the three constants; the hypotheses (asserted, the local count over a grid
of t); T_S(tau) directly from the definition, F by its closed form; the proof's lower bound
2.25 Phi(p) - sum of b's; for tau in {50, 25, 7.3, 200.3} (the first run had 1000.2 in place of the last, see below).
Expected before the run: the hypotheses hold; T_S(tau) >= the proof's lower bound >= 0 at each tau; the lower
bound is a small fraction of T_S, the proof bounding by absolute values.
Refuted by: T_S(tau) < 0 at some tau, or T_S below the proof's lower bound, or a constant above its stated bound.
Possible because: the condition was derived by hand through four numerical constants and a shell count, and
the instance puts three points in every unit window and a point of the pair at tau and at 2 tau."""
import math

import numpy as np


def F(w, L):
    w = np.asarray(w, dtype=complex)
    return 1 / w - (1 - np.exp(-w * L)) / (L * w * w)


def main():
    lam = 1 - 3 / math.e**2
    ratio = (1 + 3 / math.e**2) / lam                       # K <= ratio c^2 Phi(c) for cL >= 2
    N = 10**6
    k = np.arange(1, N + 1, dtype=float)
    shell = float((np.log1p(k) / k**2).sum()) + (math.log(N + 1) + 1) / N    # tail by the integral from N
    print(f'lambda = {lam:.4f}; K/(c^2 Phi(c)) <= {ratio:.4f}; sum log(1+k)/k^2 <= {shell:.4f}')
    assert ratio <= 2.37 and shell <= 1.9

    a, delta, kappa, L = -0.1, 0.2, 3, 27.0
    p, c = 0.5 - a, delta - a
    g = np.concatenate([np.arange(-4000, 4001) + 0.5, [50.0, -50.0]])
    d = np.concatenate([np.zeros(8001), [0.2, 0.2]])
    assert np.all((a < d) & (d <= delta)) and c * L >= 2 and p * L >= 2
    ts = np.linspace(-4100, 4100, 82001)
    counts = np.array([np.count_nonzero(np.abs(g - t) <= 1) for t in ts])
    assert np.all(counts <= kappa * np.log(np.abs(ts) + 3))
    Phi = lambda x: (math.exp(x * L) - 1 - x * L) / (L * x * x)
    K = c + (1 + math.exp(c * L)) / L
    assert K <= 2.37 * c * c * Phi(c)
    b = lambda u: np.minimum(Phi(c), K / np.maximum(u * u, 1e-300))
    print(f'Phi(p) = {Phi(p):.4e}; Phi(c) = {Phi(c):.4e}; K = {K:.4e}')
    print('tau | condition: (1/2 - delta) L, right side | T_S | proof lower bound | pole part | points part')
    for tau in (50.0, 25.0, 7.3, 200.3):       # 1000.2, in the first run, is outside the condition at L = 27
        right = math.log(kappa * (87 + 33 * math.log(abs(tau) + 4))) + 2 * math.log(p / c)
        assert abs(tau) >= 6 * p and (0.5 - delta) * L >= right
        pole = 3 * Phi(p) + 4 * F(-p + 1j * tau, L).real + F(-p + 2j * tau, L).real
        w0 = a - d - 1j * g
        points = (3 * F(w0, L).real + 4 * F(w0 + 1j * tau, L).real + F(w0 + 2j * tau, L).real).sum()
        T = float(pole - points)
        low = 2.25 * Phi(p) - float((3 * b(g) + 4 * b(tau - g) + b(2 * tau - g)).sum())
        assert T >= low >= 0, (tau, T, low)
        print(f'{tau:7.1f} | {(0.5 - delta) * L:.3f} {right:.3f} | {T:.4e} | {low:.4e} | {float(pole):.4e} | '
              f'{float(points):.4e}')


if __name__ == '__main__':
    main()
