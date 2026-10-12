"""The tilted three-four-one function for a configuration in two strata, at a negative tilt.

Statement tested (the entry's proposition): tilt a in (-1/2, 1/2), p = 1/2 - a.  S0 a multiset of points
1/2 + d + i g with a < d <= delta0 < 1/2, c0 = delta0 - a, such that for every real t the points with
|g - t| <= 1 number at most kappa log(|t| + 3) with multiplicity; S1 a finite multiset of points with
a < d <= delta < 1/2, total multiplicity M, c = delta - a.  If c0 L >= 2, |tau| >= 6p,
    (1/2 - delta) L  >= log(12 M) + 2 log(p/c)   and
    (1/2 - delta0) L >= log(kappa (174 + 66 log(|tau| + 4))) + 2 log(p/c0),
then T_S(tau) >= 0 for S the union, with T_S as in research/results/rh_check_95/local_count_reach.py.

Instance: a = -0.3, delta0 = 0 (S0 the on-line points 1/2 + i(j + 1/2), |j| <= 4000, kappa = 3), S1 the pair
1/2 + 0.2 +- 50 i (M = 2, delta = 0.2), L = 19.  Computed: both conditions (asserted); that the one-stratum
condition of the earlier proposition, (1/2 - delta) L >= log(kappa (87 + 33 log(|tau| + 4))) + 2 log(p/c) with
all points in one stratum, FAILS at this instance (asserted, so that the instance is one the earlier
statement does not cover); the local count of S0 on a grid; T_S(tau) from its definition and the proof's lower
bound 2.25 Phi(p) - sum over S0 of b0 - 8 M Phi(c), for tau in {50, 25, 7.3, 200.3}.
Expected before the run: the hypotheses hold, the earlier condition fails, and T_S(tau) >= lower bound >= 0.
Refuted by: T_S(tau) < 0 at some tau, or T_S below the lower bound, or a lower bound below zero.
Possible because: the two conditions were derived by hand by halving the pole's term between the strata, and
the instance is shorter than the length the one-stratum statement needs."""
import math

import numpy as np


def F(w, L):
    w = np.asarray(w, dtype=complex)
    return 1 / w - (1 - np.exp(-w * L)) / (L * w * w)


def main():
    a, delta0, delta, kappa, M, L = -0.3, 0.0, 0.2, 3, 2, 19.0
    p, c0, c = 0.5 - a, delta0 - a, delta - a
    g0 = np.arange(-4000, 4001) + 0.5
    g1 = np.array([50.0, -50.0])
    assert c0 * L >= 2 and a < delta0 < 0.5 and a < delta < 0.5
    ts = np.linspace(-4100, 4100, 82001)
    counts = np.array([np.count_nonzero(np.abs(g0 - t) <= 1) for t in ts])
    assert np.all(counts <= kappa * np.log(np.abs(ts) + 3))
    Phi = lambda x: (math.exp(x * L) - 1 - x * L) / (L * x * x)
    K0 = c0 + (1 + math.exp(c0 * L)) / L
    b0 = lambda u: np.minimum(Phi(c0), K0 / np.maximum(u * u, 1e-300))
    print(f'Phi(p) = {Phi(p):.4e}; Phi(c0) = {Phi(c0):.4e}; Phi(c) = {Phi(c):.4e}')
    print('tau | first condition: left, right | second: left, right | earlier one-stratum: left, right | '
          'T_S | lower bound | points part')
    for tau in (50.0, 25.0, 7.3, 200.3):
        log_tau = math.log(abs(tau) + 4)
        first = math.log(12 * M) + 2 * math.log(p / c)
        second = math.log(kappa * (174 + 66 * log_tau)) + 2 * math.log(p / c0)
        earlier = math.log(kappa * (87 + 33 * log_tau)) + 2 * math.log(p / c)
        assert abs(tau) >= 6 * p and (0.5 - delta) * L >= first and (0.5 - delta0) * L >= second
        assert (0.5 - delta) * L < earlier
        pole = 3 * Phi(p) + 4 * F(-p + 1j * tau, L).real + F(-p + 2j * tau, L).real
        d = np.concatenate([np.full(g0.size, delta0), np.full(2, delta)])
        g = np.concatenate([g0, g1])
        w0 = a - d - 1j * g
        points = float((3 * F(w0, L).real + 4 * F(w0 + 1j * tau, L).real + F(w0 + 2j * tau, L).real).sum())
        T = float(pole) - points
        low = 2.25 * Phi(p) - float((3 * b0(g0) + 4 * b0(tau - g0) + b0(2 * tau - g0)).sum()) - 8 * M * Phi(c)
        assert T >= low >= 0, (tau, T, low)
        print(f'{tau:7.1f} | {(0.5 - delta) * L:.3f} {first:.3f} | {(0.5 - delta0) * L:.3f} {second:.3f} | '
              f'{(0.5 - delta) * L:.3f} {earlier:.3f} | {T:.4e} | {low:.4e} | {points:.4e}')


if __name__ == '__main__':
    main()
