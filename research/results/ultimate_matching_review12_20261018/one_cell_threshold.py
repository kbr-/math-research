"""The smallest N at which a one-height chain on the Leighton-Shor mesh can be nonzero at cost 2.

Statement tested: at (4,4), W = 2^(-l_1) with l_1 the largest integer such that 2^(-l_1) >=
(log N)^(3/4)/sqrt(N), and the one height y* = e^19.28 of thm:one-height-chain-reduction, the
cheapest nonzero one-height chain, one layer of one cell, costs 4 W^2 psi_4^*(y*/2) (four boundary
edges, each with |Delta g| = W y*, cost W^2 psi_4^*(|Delta g|/(2W))). The class of cost at most 2
holds a nonzero chain only once that is at most 2. psi_4^*(s) = sup_t (s t - (exp(t^4) - 1)),
computed at its stationary point s = 4 t^3 exp(t^4) by bisection on t.
Expected (written before the run): the threshold lies near N = 3e10, the blind stage's hand estimate.
Refuted by: a threshold more than a factor ten away from 3e10.
Possible because: the hand estimate used psi^*(t) ~ t (log t)^(1/4) and a rough W.
Baseline: psi_4^*(s) <= s (log s)^(1/4) for large s, the bound the hand estimate used.
Record checked: thm:one-height-chain-reduction (y* >= e^19.28) and lem:one-height-rounding (the cost
convention with 2W), read this session.
"""
import math


def psi_star(s):
    lo, hi = 0.0, 3.0
    for _ in range(200):
        t = (lo + hi) / 2
        if 4 * t ** 3 * math.exp(t ** 4) < s:
            lo = t
        else:
            hi = t
    t = lo
    return s * t - (math.exp(t ** 4) - 1)


def W(N):
    target = math.log(N) ** 0.75 / math.sqrt(N)
    l1 = math.floor(-math.log2(target))  # largest l with 2^(-l) >= target
    return 2.0 ** (-l1)


ystar = math.exp(19.28)
ps = psi_star(ystar / 2)
print(f"y* = {ystar:.4e}, psi_4^*(y*/2) = {ps:.4e}, baseline (y*/2)(log(y*/2))^(1/4) = "
      f"{ystar / 2 * math.log(ystar / 2) ** 0.25:.4e}")
prev = None
for e in range(80, 141):
    N = 10 ** (e / 10)
    cost = 4 * W(N) ** 2 * ps
    if prev is not None and prev > 2 >= cost:
        print(f"one-cell cost crosses 2 between N = 10^{(e - 1) / 10:.1f} and 10^{e / 10:.1f}")
    prev = cost
for e in (9, 10, 10.5, 11, 12):
    N = 10 ** e
    print(f"N = 10^{e}: W = {W(N):.3e}, one-cell cost = {4 * W(N) ** 2 * ps:.3f}")
