"""No statement tested: evaluates, on members of the power-growing charged family, the size of the canonical
short-range ratio B_m(K-d)/B_m(K) (which h(K-d)/h(K) equals up to the factor 1 - eta_occ of lem:cut-ball-occupancy)
as a power of the encoding length N, at gaps d = 1, Delta, t and 2t, for the two extremes of the edge count.

Family (prop:charge-affine-rank-gap's registered statement): Delta = ceil(n^alpha), 0 < alpha < min(1/17, 1/l),
n Delta/8 <= m <= n Delta, D = floor(n Delta/64), K = floor(D/8), h = ceil(Delta log n), log N = Theta(Delta). The
accuracy t = h is taken with the natural logarithm. A first version of this script set Delta = ceil((log2 n)^2),
which is not the family's (its reviewer, 17 October 2026); this one uses its members: (log2 n, alpha) =
(340, 1/20), as the approximator product review did, (680, 1/20) and (680, 1/40), each alpha below 1/17.

The ball ratio: B_m(k-1)/B_m(k) lies between (1-q) t_{k-1}/t_k and t_{k-1}/t_k, t_i = 2^i binom(m, i),
q = K/(2(m-K+1)), and t_{K-d}/t_K = prod_{i<d} (K-i)/(2(m-K+i+1)). At these sizes d/K < 1e-80, so the product
equals (K/(2(m-K)))^d within a factor exp(+-2 d^2/K), printed; the bounds printed are the product's, with the
factor (1-q)^d of the lower bound shown separately.

The encoding length is not computed: log2 N is taken at Delta and at 3 Delta (the charge clauses are one-hot
ternary clauses of degree up to 2 Delta, so the clause count may be nearer 2^(3 Delta); unverified), and every
exponent of N printed is this bookkeeping's. The level-one threshold t * eta >= ln M, eta = canonical/2 at d = 1
(lem:weighted-adaptive-approximation over F_2), is printed as the largest A it allows: A <= t eta / ln N.
"""
import math
from fractions import Fraction

for log_n, alpha in ((340, Fraction(1, 20)), (680, Fraction(1, 20)), (680, Fraction(1, 40))):
    assert alpha < Fraction(1, 17)
    log2_delta = log_n * alpha                    # Delta = 2^(log2 n * alpha), an integer here
    assert log2_delta.denominator == 1
    log2_delta = int(log2_delta)
    ln_n = log_n * math.log(2)
    delta = 2 ** log2_delta
    t = math.ceil(delta * ln_n)
    log2_nd = log_n + log2_delta                  # log2(n Delta)
    log2_K = log2_nd - 6 - 3                      # K = n Delta / 512 (exact here: powers of two)
    for label, log2_m in (('m = n Delta/8', log2_nd - 3), ('m = n Delta', log2_nd)):
        # K/(2(m-K)) = 1/(2(m/K - 1)), m/K a power of two
        per_level = -math.log2(2 * (2 ** (log2_m - log2_K) - 1))
        log2_q = log2_K - 1 - math.log2(2 ** log2_m - 2 ** log2_K)   # q ~ K/(2(m-K)), tiny
        q = 2 ** (log2_K - log2_m - 1) / (1 - 2 ** (log2_K - log2_m))
        print(f'log2 n = {log_n}, alpha = {alpha}, Delta = 2^{log2_delta}, t = {t}, {label}: canonical per level '
              f'2^{per_level:.3f}, q = {q:.2e}')
        for dlabel, d in (('1', 1), ('Delta', delta), ('t', t), ('2t', 2 * t)):
            log2_c = d * per_level
            slack = 2 * d * d / 2 ** log2_K                             # exp(+-2 d^2/K) in natural units
            lower_extra = d * math.log2(1 - q)
            for enc, log2_N in (('log2 N = Delta', delta), ('log2 N = 3 Delta', 3 * delta)):
                print(f'  d = {dlabel} = {d}: log2 canonical = {log2_c:.4g} (product within e^+-{slack:.1e}; the '
                      f'ball ratio within a further 2^{lower_extra:.3g}), = N^{log2_c / log2_N:.3g} at {enc}; '
                      f'log2(t * canonical) = {log2_c + math.log2(t):.4g}')
        eta1 = 2 ** per_level / 2
        for enc, log2_N in (('log2 N = Delta', delta), ('log2 N = 3 Delta', 3 * delta)):
            print(f'  level one: t * eta = {t * eta1:.4g} against ln N = {log2_N * math.log(2):.4g} at {enc}: '
                  f'survival for A up to {t * eta1 / (log2_N * math.log(2)):.3g}')
