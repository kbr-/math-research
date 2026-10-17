"""Arithmetic of the nonvacuity witness of entry-2026-10-17-separated-bundles (staggered rectangles in groups of m).

No statement tested: it evaluates the witness's parameters, its discrete cost from the recorded bounds of psi_4^*,
hypothesis (B4), its layer count against the recorded chain bounds' conditions, and the plainest bound's factor,
at several N. Bounds used: psi_4^*(t) <= t (2 log t)^(1/4) + 1 and psi_4^*(t) >= t (log t)^(1/4)/(2 sqrt 2) for
t >= e^16 (recorded in entry-2026-10-17-cost-weighted-slopes); psi_4^*(e^16) <= 2.4 e^16.
"""
import math

E16 = math.exp(16)


def psi_up(t):
    return t * (2 * math.log(t)) ** 0.25 + 1


def psi_low(t):
    return t * math.log(t) ** 0.25 / (2 * math.sqrt(2))


for lnN in (14, 20, 30, 50, 80, 140, 200, 400, 700):
    N = math.exp(lnN)
    d0 = 2 ** math.floor(math.log2(8 * math.sqrt(lnN / N)))      # dyadic in [4 sqrt(log N/N), 8 sqrt(log N/N))
    while d0 < 4 * math.sqrt(lnN / N):
        d0 *= 2
    n = round(1 / d0)
    y = 2 * E16
    m = math.ceil(math.exp(math.sqrt(lnN)))
    G = math.floor(n / (8 * y * m * (2 * math.log(m * y)) ** 0.25))
    K = G * m
    if G < 1:
        print(f'ln N = {lnN}: G = 0, the witness needs larger N')
        continue
    # costs: bundles (at most n edges each, multiplicity m), single sides (2.25 n edges per layer), ends
    bundles = G * n * d0 ** 2 * psi_up(m * y / 2)
    singles = K * 2.25 * n * 2.4 * E16 * d0 ** 2
    ends = G * 2 * m * d0 ** 2 * psi_up(m * y / 2)
    bundle_low = G * (n / 2) * d0 ** 2 * psi_low(m * y / 2)
    ell = 0.5                                           # each bundle at least n/2 cells, length 1/2
    b4 = 2 * m * d0 * math.log(m * y) ** 0.25
    l1 = math.floor(math.log2(math.sqrt(N) / lnN ** 0.75))
    # each layer is at least n/2 cells wide and high (K <= n/8, bottoms below n/8 + 1.1 K), perimeter >= 2
    tv = y * d0 * K * 2
    multilevel = lnN ** (2 / 3) * math.log(y / 2) ** (1 / 3)
    print(f'ln N = {lnN}: n = {n}, m = {m}, G = {G}, K = {K}, log K = {math.log(K):.2f} '
          f'(multilevel bound {multilevel:.2f}, N^(1/7) gives {lnN / 7:.2f}); '
          f'cost: bundles <= {bundles:.4f}, singles <= {singles:.4f}, ends <= {ends:.2e}, total <= '
          f'{bundles + singles + ends:.4f}; bundle cost >= {bundle_low:.4f}; '
          f'(B4): ell = {ell} >= {max(b4, 2 ** -l1):.2e}; TV(g) >= {tv:.4f}; '
          f'plainest factor (log N)^(3/4) TV / sqrt(log N) = {lnN ** 0.25 * tv:.3f}')
