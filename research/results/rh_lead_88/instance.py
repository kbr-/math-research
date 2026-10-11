"""Arithmetic for the entry on the binomial family in the tilted inequality: its bounds on instances.

F(w) = int_0^L (1 - u/L) e^{-wu} du = 1/w - (1 - e^{-wL})/(L w^2); Phi(x) = F(-x).
Family: k + 1 points at one distance, c = delta - a, heights gamma0 + j pi/L, multiplicities binom(k, j).
Statements evaluated, for each instance (L, a, delta, k):
(a) |sum_j binom(k, j) F(-c + i(t - j pi/L))| <= Psi = (k+1)! (pi/(cL))^k e^{cL}/(L c^2) for real t, the left
    side evaluated directly on a grid of t (no use of the bound's proof);
(b) T_family(tau) >= 2.25 Phi(p) - 8 Psi on a grid of tau >= 6p containing gamma0 as a grid point;
(c) T_single(gamma0) <= 3.75 Phi(p) - 4 M (Phi(c) - beta), M = 2^k, beta = 1/|gamma0| + 2 e^{cL}/(L gamma0^2);
(d) the local reach: T_family(tau) >= 2.25 Phi(p) - sum_rho m_rho [3 B(gamma_rho) + 4 B(tau - gamma_rho)
    + B(2 tau - gamma_rho)], B(t) = min(Phi(c), 1/|t| + 2 e^{cL}/(L t^2));
(e) the displayed sufficient condition of part (2), (1/2 - delta) L >= log(6 (k+1)!) - k log(cL/pi) + 2 log(p/c),
    printed with both sides.
Expected before this run (the second version of the script; the first, with a weaker Psi, is kept as
instance_first_version.out.txt): (a) to (d) hold in every instance (asserted). In the first instance
2.25 Phi(p) - 8 Psi > 0 and 3.75 Phi(p) - 4 M (Phi(c) - beta) < 0 while (e) fails, as a reviewer computed by
hand for the first version. In the instance (30, 0.06, 0.46, 2), chosen by hand estimate, (e) holds and the
single point's upper bound is negative. In the two instances of the previous entry (L = 20; (0.3, 0, 4) and
(0.4, 0.1, 3)) the lower bound in (b) is negative while the computed minimum is positive."""
import math

import numpy as np


def F(w, L):
    w = np.asarray(w, dtype=complex)
    return 1 / w - (1 - np.exp(-w * L)) / (L * w**2)


def Phi(x, L):
    return (math.exp(x * L) - 1 - x * L) / (L * x**2)


def main():
    for L, a, delta, k in ((20.0, 0.015, 0.415, 2), (30.0, 0.06, 0.46, 2), (20.0, 0.0, 0.30, 4),
                           (20.0, 0.1, 0.40, 3), (60.0, 0.0, 0.40, 4), (200.0, 0.0, 0.30, 6)):
        p, c, M, h = 0.5 - a, delta - a, 2**k, math.pi / L
        assert p * L >= 2 and 0 < c < p
        weights = [math.comb(k, j) for j in range(k + 1)]
        scale = math.exp(-(p * L - math.log(L * p * p)))      # sizes are printed in units of e^{pL}/(L p^2)

        def fam(t):
            return sum(m * F(-c + 1j * (t - j * h), L) for j, m in enumerate(weights))
        ts = np.linspace(-40 * h, 40 * h + k * h, 160001)
        psi = math.factorial(k + 1) * (h / c)**k * math.exp(c * L) / (L * c * c)
        direct = np.abs(fam(ts)).max()
        assert direct <= psi * (1 + 1e-12)
        taus = np.linspace(6 * p, 6 * p + 40.0, 400001)
        gamma0 = taus[200000]                                 # a grid point, so the height itself is sampled
        pole = 3 * Phi(p, L) + 4 * F(-p + 1j * taus, L).real + F(-p + 2j * taus, L).real
        T = pole - (3 * fam(-gamma0 + 0 * taus).real + 4 * fam(taus - gamma0).real + fam(2 * taus - gamma0).real)
        low = 2.25 * Phi(p, L) - 8 * psi
        assert T.min() >= low - 1e-9 * abs(low)

        def B(t):
            t = np.abs(t)
            return np.minimum(Phi(c, L), 1 / t + 2 * math.exp(c * L) / (L * t * t))
        with np.errstate(divide='ignore'):
            local = 2.25 * Phi(p, L) - sum(m * (3 * B(-gamma0 - j * h + 0 * taus) + 4 * B(taus - gamma0 - j * h)
                                                + B(2 * taus - gamma0 - j * h)) for j, m in enumerate(weights))
        assert (T >= local - 1e-9 * np.abs(local)).all()
        beta = 1 / gamma0 + 2 * math.exp(c * L) / (L * gamma0**2)
        at = (3 * Phi(p, L) + 4 * F(-p + 1j * gamma0, L).real + F(-p + 2j * gamma0, L).real
              - M * (3 * F(-c - 1j * gamma0, L).real + 4 * Phi(c, L) + F(-c + 1j * gamma0, L).real))
        up = 3.75 * Phi(p, L) - 4 * M * (Phi(c, L) - beta)
        assert at <= up + 1e-9 * abs(up)
        needed = math.log(6 * math.factorial(k + 1)) - k * math.log(c * L / math.pi) + 2 * math.log(p / c)
        print(f'L = {L:g}, a = {a}, delta = {delta}, k = {k}, M = {M}: cL = {c * L:.2f}; condition (e): '
              f'(1/2 - delta) L = {(0.5 - delta) * L:.3f} against {needed:.3f}, '
              f'{"holds" if (0.5 - delta) * L >= needed else "fails"}; in units of e^(pL)/(L p^2): Phi(p) = '
              f'{Phi(p, L) * scale:.4f}, Psi = {psi * scale:.3e}, max |sum F| on the grid = {direct * scale:.3e}, '
              f'M Phi(c) = {M * Phi(c, L) * scale:.3e}; family: lower bound 2.25 Phi(p) - 8 Psi = '
              f'{low * scale:+.4f}, computed min T = {T.min() * scale:+.4f}, local-reach bound min = '
              f'{local.min() * scale:+.4f}; single point at its height: upper bound = {up * scale:+.4f}, '
              f'computed T = {at * scale:+.4f}')


if __name__ == '__main__':
    main()
