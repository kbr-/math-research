"""Instance check of the tenth review: thm:coarse-mean-flow-obstruction's cost step at log N = 100.

No statement tested: it evaluates the review's displayed quantities at one instance, from the proof's
cost step as written in entry-2026-10-17-regrouped-corrections: u_N >= 2^(-r) theta sqrt(ln N)/(sqrt2 L),
mu = N^(-theta log_2(4/p_0)) with log_2(4/p_0) = 770, so I_k >= W psi_alpha(u_N) diverges when
u_N^alpha - 770 theta ln N -> infinity; r* = (1/2 - 1/alpha) log_2 ln N.
Usage: python3 instance_check.py --out FILE
"""
import math
import sys

out = sys.argv[sys.argv.index('--out') + 1]
ln_n, theta, L, alpha = 100.0, 6e-4, 1.0, 4
lines = [f'ln N = {ln_n}, theta = {theta} (below 1/1542 = {1 / 1542:.6f}), L = {L}, alpha = {alpha}',
         f'r* = (1/2 - 1/alpha) log_2 ln N = {(0.5 - 1 / alpha) * math.log2(ln_n):.3f}',
         f'a ln N = 770 theta ln N = {770 * theta * ln_n:.2f}']
for r in range(0, 4):
    u = 2 ** -r * theta * math.sqrt(ln_n) / (math.sqrt(2) * L)
    lines.append(f'r = {r}: u_N = {u:.3e}, u_N^alpha = {u ** alpha:.3e}, u_N^alpha - a ln N = {u ** alpha - 770 * theta * ln_n:.2f}')
lines.append(f'r* at ln N = 1e4: {(0.5 - 1 / alpha) * math.log2(1e4):.3f}; at alpha = infinity: {0.5 * math.log2(1e4):.3f}')
# Second stage (reviewer's figures, recomputed): u_N^alpha - a ln N = ln N (C 2^(alpha(r* - r)) - a), C = (theta/(sqrt2 L))^alpha,
# so the cost step needs C 2^(alpha(r* - r)) > a + eps: r <= r* - c_0, c_0 = log_2(a/C)/alpha; at r = 0 the
# conclusion needs (ln N)^(alpha/2 - 1) > a/C.
C, a = (theta / (math.sqrt(2) * L)) ** alpha, 770 * theta
lines.append(f'C = {C:.3e}, a/C = {a / C:.3e}, c_0 = log_2(a/C)/alpha = {math.log2(a / C) / alpha:.2f} levels')
lines.append(f'at r = 0 the cost step needs ln N > (a/C)^(1/(alpha/2 - 1)) = {(a / C) ** (1 / (alpha / 2 - 1)):.3e}')
lines.append(f'alpha = infinity: r <= (1/2) log_2 ln N - log_2(2 sqrt2 L/theta), offset {math.log2(2 * math.sqrt(2) * L / theta):.2f}')
# Retained chain test: the multilevel bound's large-layer count e^((ln N)^(2/3)) against the seventh review's N^(1/7),
# and the ln N beyond which (ln N)^(2/3) < ln N/7.
lines.append(f'ln N = 100: (ln N)^(2/3) = {100 ** (2 / 3):.2f}, ln N/7 = {100 / 7:.2f}; crossing at ln N = 7^3 = {7 ** 3}')
lines.append(f'with the registered factor (log(y_B/2))^(1/3) >= 16^(1/3) = {16 ** (1 / 3):.2f}: bound on log|B| at ln N = 100 '
             f'at least {100 ** (2 / 3) * 16 ** (1 / 3):.1f}; small-layer cap N^(1/6)/(ln N)^2 = e^{100 / 6 - 2 * math.log(100):.2f}')
# Two-scale composition at (4,4), in units of 1/sqrt N: cell side l = (ln N)^(3/4), s = L sqrt(ln N), n = (ln N)^(3/2)
# points per cell, an inner Gaussian displacement of standard deviation sqrt(ln ln N); the exponent of its tail at
# s t^(1/4), (s t^(1/4))^2/(2 ln ln N) = L^2 sqrt(t) ln N/(2 ln ln N), against t (it must be at least t up to t = ln N).
for ln_n2 in (100.0, 1e4):
    l, s, n, var = ln_n2 ** 0.75, L * math.sqrt(ln_n2), ln_n2 ** 1.5, math.log(ln_n2)
    worst = min(L ** 2 * math.sqrt(t) * ln_n2 / (2 * var) / t for t in (1, ln_n2 ** 0.5, ln_n2))
    lines.append(f'ln N = {ln_n2:g}: l/s = {l / s:.3f}, (l/s)^4 = {(l / s) ** 4:.1f} = ln N/L^4, n = {n:.0f} points per cell, '
                 f'inner sd/s = {math.sqrt(var) / s:.3f}, min over t in [1, ln N] of tail exponent/t = {worst:.2f} '
                 '[WITHDRAWN: compares with t only up to ln N at composition constant 1, not the budget integral; '
                 'see review.txt and the review entry]')
open(out, 'w').write('\n'.join(lines) + '\n')
