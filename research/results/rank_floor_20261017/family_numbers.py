"""Evaluates the dense product rank floor and its ratio corollary at members of the power-growing charged family.

No statement tested: it evaluates the displayed terms of the lemma's bound (proved in the entry) at the family's
own parameters, copied from prop:charge-affine-rank-gap's registered statement read in this turn: Delta =
ceil(n^alpha), 0 < alpha < min(1/17, 1/ell), n Delta/8 <= m <= n Delta, degrees between Delta/4 and 2 Delta,
expansion at least Delta/4, D = floor(n Delta/64), K = floor(D/8), and the accuracy t = ceil(Delta ln n) of the
rate scale review's test.  The expansion is taken at its least admitted value Delta/4, the worst case for rho.
The pairs: the pi largest of the 2 Delta + 1 matchings of a proper edge colouring (Vizing) hold at least
pi m/(2 Delta + 1) edges with at most pi at a vertex, so s <= floor(pi m/(2(2 Delta + 1))) pairs exist with
largest paired degree pi; the review's range D/2 < s <= D - K is intersected with that and with s >= K + t + 1.
zeta_C is bounded by its mean over uniform binary C, (2^t - 1)((1 + 2K/m)/2)^s, so some C meets the bound.
Every quantity is computed in base-2 logarithms; a term far below 2^-1000 is printed as its exponent.
"""
import math

LOG2E = math.log2(math.e)


def member(log2n, alpha, m_over, pi_frac):
    n = 2.0 ** log2n
    Delta = math.ceil(2 ** (log2n * alpha))
    m = n * Delta * m_over
    D = math.floor(n * Delta / 64)
    K = math.floor(D / 8)
    t = math.ceil(Delta * math.log(2) * log2n)          # ceil(Delta ln n)
    eps = Delta / 4
    pi = Delta * pi_frac
    s_max = math.floor(pi * m / (2 * (2 * Delta + 1)))
    lo, hi = max(D // 2 + 1, K + t + 1), min(D - K, s_max)
    rows = []
    for s in sorted({lo, hi}) if lo <= hi else []:
        rho = (eps - 2 * pi) / (2 * (eps - pi))
        log2_beta = rho * math.log2(math.e * K / (rho * (m - 2 * s)))
        log2_x = 1 + (eps - pi) * log2_beta                   # x = 2 beta'^(eps - pi)
        log2_eta = math.log2(2 * n) + log2_x + 1 if log2_x + math.log2(2 * n) < -1 else float('nan')   # e^{2nx}-1 <= 4nx
        log2_zeta = t + s * math.log2((1 + 2 * K / m) / 2)
        bstar = 4 * s * (K / m) ** 2                           # Markov term s (K/m)^2 / b* = 1/4
        kappa = bstar / (s - K - t + 1)
        tail = 0.75 - 2.0 ** max(log2_eta, -1074) - 2.0 ** max(log2_zeta, -1074)
        log2_floor = t * math.log2(1 - kappa) + math.log2(tail)
        q = K / (2 * (m - K + 1))
        log2_ratio = 2 * t * math.log2(q) - log2_floor
        log2_record = s * K / m * LOG2E                        # cor:pair-sector-bounds (iii): e^{sK/m}
        rows.append(dict(log2n=log2n, alpha=alpha, m=f'{m_over:g} n Delta', Delta=Delta, D=f'2^{math.log2(D):.3f}',
                         K=f'2^{math.log2(K):.3f}', t=t, s=f'2^{math.log2(s):.4f}', pi=pi, rho=round(rho, 4),
                         beta=round(2 ** log2_beta, 4), log2_eta=round(log2_eta, 1), log2_zeta=f'{log2_zeta:.4e}',
                         kappa=f'{kappa:.4e}', log2_floor=round(log2_floor, 1), log2_q=round(math.log2(q), 4),
                         log2_ratio_2t=f'{log2_ratio:.4e}', log2_t_ratio=f'{log2_ratio + math.log2(t):.4e}',
                         log2_record_excess=f'{log2_record:.4e}', record_bound_log2=f'{2 * t * math.log2(q) + log2_record:.4e}'))
    return rows


if __name__ == '__main__':
    for log2n, alpha in [(340, 1 / 20), (680, 1 / 20), (680, 1 / 40)]:
        for m_over in (1 / 8, 1 / 2, 1):
            rows = member(log2n, alpha, m_over, 1 / 16)
            if not rows:
                print(f'log2 n={log2n} alpha={alpha:g} m={m_over:g} n Delta: no s in the range with pi = Delta/16')
            for r in rows:
                print(r)
