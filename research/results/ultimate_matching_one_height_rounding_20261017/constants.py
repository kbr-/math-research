"""Constants of the Leighton-Shor mesh reduction, entry-2026-10-17-one-height-rounding, and its next attempt's instance.

No statement tested: it evaluates the constants the proofs use and the figures of the Follow-up's smallest case.
psi_4(u) = e^(u^4) - 1 and psi_4^*(t) = sup_u (t u - psi_4(u)), by a bounded scalar maximization; for t >= e^16 the
recorded bounds t (log t)^(1/4)/(2 sqrt 2) <= psi_4^*(t) <= t (2 log t)^(1/4) + 1.

Printed: psi_4^*(1); T(M) = 4 + 2M/psi_4^*(1); for rounding at Y = e^22 a function of cost M = 2 (the averages cost at
most M, the factor-one count of the averaging lemma (c)): ratio = psi_4^*(Y/2)/Y (upper bound), C1 = 7M + ratio T(M),
c = C1/2, y* = Y/c against 2e^16.

Smallest case (one stack of D coarse lines, multiplicity m = e^(sqrt(log N)), height y*, horizontal stretch of length
1/2 on the mesh W = 2^(-l_1)), at full budget: D chosen so that the stack's cost upper bound D (l/W) W^2 psi_4^*(m y*/2)
equals 1, a = m D y* W its amplitude, TV = a l. Printed against sqrt(log N): the factor of lem:fine-grid-leighton-shor
(b), (log N)^(3/4) TV; of lem:tube-localized-discrepancy (b) at tube width D W, ((2 log2 D + 5)^(3/4) + sqrt(log N)) a l
with the amplitude count 12 a l included as a constant factor 13; of lem:cost-weighted-slope-bound (b), 6 eta (log(m y*))^(1/4)
with eta = 1 the stack's cost.
"""
import math

from scipy.optimize import minimize_scalar


def psi4_star(t):
    res = minimize_scalar(lambda u: -(t * u - math.expm1(u ** 4)), bounds=(0.0, 3.0), method='bounded',
                          options={'xatol': 1e-12})
    return -res.fun


def psi_up(t):
    return t * (2 * math.log(t)) ** 0.25 + 1


p1 = psi4_star(1.0)
print(f'psi_4^*(1) = {p1:.6f}')
T = {M: 4 + 2 * M / p1 for M in (2, 4)}
for M in (2, 4):
    print(f'T({M}) = 4 + 2*{M}/psi_4^*(1) = {T[M]:.4f}')
Y = math.exp(22)
ratio = psi_up(Y / 2) / Y
C1 = 7 * 2 + ratio * T[2]
c = C1 / 2
ys = Y / c
print(f'Y = e^22: psi_4^*(Y/2)/Y <= {ratio:.4f}; C1 = 7*2 + ratio*T(2) = {C1:.4f}; c = C1/2 = {c:.4f}; '
      f'y* = Y/c = e^{math.log(ys):.4f}, 2e^16 = e^{math.log(2 * math.exp(16)):.4f}, y* >= 2e^16: {ys >= 2 * math.exp(16)}')
print('smallest case at full budget (stack cost 1), ell = 1/2; each bound as its factor over sqrt(N log N):')
for lnN in (100, 400, 1600, 6400, 25600):
    l1 = math.floor((lnN / 2 - 0.75 * math.log(lnN)) / math.log(2))       # 2^(-l1) >= (log N)^(3/4)/sqrt N, largest
    lnW = -l1 * math.log(2)
    lnm = math.sqrt(lnN)
    ell = 0.5
    t = math.exp(lnm) * ys / 2                                            # psi_up(t) in logs: t (2 log t)^(1/4) + 1, t huge
    ln_psi = math.log(t) + 0.25 * math.log(2 * math.log(t))
    lnD = -(math.log(ell) + lnW + ln_psi)                                 # D (l/W) W^2 psi = 1
    tv = ell * math.exp(lnm + lnD + math.log(ys) + lnW)                  # a l, a = m D y* W
    fg = lnN ** 0.25 * tv                                                 # (log N)^(3/4) TV over sqrt(log N)
    tube = 13 * ((2 * lnD / math.log(2) + 5) ** 0.75 / math.sqrt(lnN) + 1) * tv
    cw = 6 * (lnm + math.log(ys)) ** 0.25
    print(f'  ln N = {lnN}: log2 D = {lnD / math.log(2):.1f}, log(D W) = {lnD + lnW:.1f}, a l = {tv:.4f}; '
          f'fine-grid (b) {fg:.3f}, tube (b) {tube:.3f}, cost-weighted (b) loss {cw:.3f}')
