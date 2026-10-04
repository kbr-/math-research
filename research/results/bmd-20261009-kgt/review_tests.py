"""Review kgt cheap tests from recorded d = 3 data (polar-colon.txt, acm-comparison-p65521.txt).
Gamma = CI(F, m1) on a plane, degrees a = 55, b = 56, length 3080; Gamma0 = colon section (1580),
Gamma1 = residual (1500).  Cayley-Bacharach for a plane CI: h_G1(t) = |G1| - (dim I_G0 - dim I_G)(a+b-3-t)."""
from math import comb
a, b = 55, 56
gens = {53: 1, 54: 2, 55: 4, 56: 39}; rels = {57: 45}
def dimI0(t):  # ideal of the colon section from its Betti numbers
    return sum(n * comb(t - g + 2, 2) for g, n in gens.items() if t >= g) - sum(n * comb(t - g + 2, 2) for g, n in rels.items() if t >= g)
def dimIG(t):  # complete intersection (a, b) in three variables
    f = lambda e: comb(e + 2, 2) if e >= 0 else 0
    return f(t - a) + f(t - b) - f(t - a - b)
h0 = {t: comb(t + 2, 2) - dimI0(t) for t in range(48, 59)}
h1 = {t: 1500 - (dimI0(a + b - 3 - t) - dimIG(a + b - 3 - t)) for t in range(48, 59)}
d0 = {t: h0[t] - h0[t - 1] for t in range(49, 59)}
d1 = {t: h1[t] - h1[t - 1] for t in range(49, 59)}
print("dim I_G0:", [dimI0(t) for t in range(53, 58)])
print("h_G0:", h0); print("Dh_G0:", d0)
print("h_G1:", h1); print("Dh_G1:", d1)
def oseq(d, alpha):  # in P^2, Dh(t) = t+1 below alpha, nonincreasing from alpha on, ends at 0
    ok = all(d[t] == t + 1 for t in d if t < alpha) and all(d[t] >= d[t + 1] for t in d if t >= alpha and t + 1 in d)
    return ok and d[max(d)] == 0
print("O-sequence Gamma0 (alpha 53):", oseq(d0, 53), " Gamma1 (alpha 54):", oseq(d1, 54))
print("max rank Gamma0 at 53:", min(comb(55, 2), 1580), "actual", h0[53], "; general alpha:", min(t for t in range(80) if comb(t + 2, 2) > 1580))
for d, lam, alpha, endB in [(2, 15, 12, 9), (3, 55, 53, 48)]:
    e = 2 * lam - 3 - alpha
    print(f"d={d}: e(C') = 2lambda-3-alpha = {e}; end_B + 6 = {endB + 6}")
