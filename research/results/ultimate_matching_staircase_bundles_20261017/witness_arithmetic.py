"""Arithmetic of the nonvacuity witness of entry-2026-10-17-staircase-bundles: the separated-bundles witness with each
group's shared bottom a monotone staircase f_j(x) = b_j + floor((x - n/8)/2), b_{j+1} = b_j + 2m + 2.

No statement tested: it evaluates the witness's parameters, its discrete cost from the recorded bounds of psi_4^*
(psi_4^*(t) <= t (2 log t)^(1/4) + 1, psi_4^*(t) >= t (log t)^(1/4)/(2 sqrt 2) for t >= e^16, psi_4^*(e^16) <=
2.4 e^16), hypothesis (B4) with the factor 4, the layer count against the recorded chain bounds' conditions, and
the plainest bound's factor, at several N. Grid lengths: a staircase rising one row every 2 columns over a width w
has grid length at most 1.5 w + 2; each layer's left, right and top sides have at most 2.25 n edges; its bottom
at most 1.5 n.
"""
import math

E16 = math.exp(16)


def psi_up(t):
    return t * (2 * math.log(t)) ** 0.25 + 1


def psi_low(t):
    return t * math.log(t) ** 0.25 / (2 * math.sqrt(2))


for lnN in (80, 140, 200, 400, 700):
    N = math.exp(lnN)
    d0 = 2 ** math.floor(math.log2(8 * math.sqrt(lnN / N)))
    while d0 < 4 * math.sqrt(lnN / N):
        d0 *= 2
    n = round(1 / d0)
    y = 2 * E16
    m = math.ceil(math.exp(math.sqrt(lnN)))
    G = math.floor(n / (16 * y * m * (2 * math.log(m * y)) ** 0.25))
    K = G * m
    height_used = G * (2 * m + 2) + K + 3 * n / 8          # bottoms' offsets, tops' descent, the staircase's rise
    bundles = G * 1.5 * n * d0 ** 2 * psi_up(m * y / 2)    # each shared bottom at most 1.5 n edges at multiplicity m
    singles = K * (2.25 + 1.5) * n * 2.4 * E16 * d0 ** 2   # sides and the unshared parts of bottoms
    # per end: the cut m + 1 columns and the m columns where the group's layers start, 1.5 edges per column,
    # multiplicity at most m
    ends = G * 2 * 1.5 * (2 * m + 2) * d0 ** 2 * psi_up(m * y / 2)
    bundle_low = G * (n / 2) * d0 ** 2 * psi_low(m * y / 2)
    b4 = 4 * m * d0 * math.log(m * y) ** 0.25
    l1 = math.floor(math.log2(math.sqrt(N) / lnN ** 0.75))
    tv = y * d0 * K * 2
    multilevel = lnN ** (2 / 3) * math.log(y / 2) ** (1 / 3)
    print(f'ln N = {lnN}: n = {n:.3e}, m = {m}, G = {G}, K = {K:.3e}, log K = {math.log(max(K, 1)):.2f} '
          f'(multilevel {multilevel:.2f}, N^(1/7) {lnN / 7:.2f}); height used {height_used / n:.3f} n of 3n/4; '
          f'cost: bundles <= {bundles:.4f}, singles <= {singles:.4f}, ends <= {ends:.2e}, total <= '
          f'{bundles + singles + ends:.4f}; bundle cost >= {bundle_low:.4f}; (B4): ell >= 1/2 >= '
          f'{max(b4, 2 ** -l1):.2e}; TV >= {tv:.4f}; plainest factor {lnN ** 0.25 * tv:.3f}')
