"""Cheap tests of the route review of 26 September 2026 (cycle bmd-r74).

1. Products at (d, rho): the product witnesses at (d, rho) are the products of boundary witnesses over partitions of d
   into exactly rho parts, with multiplicity o = sum psi(p_i) at the double point (psi(p) = floor(p^2/2)).  The squeeze
   lemma needs rho of them with independent cones and pi - (sum of the rho - 1 largest o) >= mu, pi = psi(d).  The
   table reports, for every (d, rho) with 3 <= d <= 7, 2 <= rho <= d - 1, whether distinct product partitions can meet
   this at all (a necessary condition; independence is not tested here).
2. Forney / degree identity: on a general line through the double point, sum b_i = d^2 - 1 - C(rho, 2) - pi.  The
   generator degrees b_i are read from the saved splitting output.
3. Hilbert-Burch: at (6,2) the 2 x 2 minor of the product cones on the top two coordinates, divided by the common
   factor, is compared with the cone of F_6, a multiple of U^6 S^6 (U^6 - S^6); coefficients from the saved r73 output.
4. Pairing: the increments of psi are 2, 2, 4, 4, 6, 6, ...; compared with the tight cases rho mu = pi.
"""
import re
import sys
from itertools import combinations
from math import comb

Q = 1000003


def psi(p):
    return p * p // 2


def partitions(n, k, maxp=None):
    if maxp is None:
        maxp = n
    if k == 0:
        if n == 0:
            yield ()
        return
    for p in range(min(n - (k - 1), maxp), 0, -1):
        for rest in partitions(n - p, k - 1, p):
            yield (p,) + rest


def mu(d, rho):
    return min(sum(psi(p) for p in lam) for lam in partitions(d, rho))


def B(d, rho):
    return min(sum(p * p - 1 for p in lam) for lam in partitions(d, rho))


out = []
out.append("1. products and the squeeze (d, rho, mu, pi, tight, partitions with o, feasible)")
for d in range(3, 8):
    for rho in range(2, d):
        m_, pi = mu(d, rho), psi(d)
        parts = sorted(((sum(psi(p) for p in lam), lam) for lam in partitions(d, rho)))
        feasible = any(pi - sum(sorted(o for o, _ in S)[1:]) >= m_ for S in combinations(parts, rho))
        out.append(f"  ({d},{rho}): mu={m_} pi={pi} tight={rho * m_ == pi} products={[(lam, o) for o, lam in parts]}"
                   f" squeeze-feasible-by-products={feasible}")

out.append("2. Forney / degree identity on the line through (1,1,0) and (7,3,11)")
text = open(sys.argv[1]).read()
blocks = re.findall(r"d=(\d+) m=(\d+) rho=(\d+).*?generator degrees b_i: ([\d ]+)", text, re.S)
for d, m, rho, gens in blocks:
    d, rho = int(d), int(rho)
    b = list(map(int, gens.split()))
    pred = d * d - 1 - comb(rho, 2) - psi(d)
    out.append(f"  ({d},{rho}): sum b_i = {sum(b)}, d^2-1-C(rho,2)-pi = {pred}: {'agree' if sum(b) == pred else 'DIFFER'}")

out.append("3. Hilbert-Burch at (6,2): minor of the top two cones")
r73 = open(sys.argv[2]).read()
def cone(c, which):
    line = re.search(rf"c={c} cone A \(coefficients[^:]*\):([\d ]+)\| cone B:([\d ]+)", r73)
    return list(map(int, line.group(1 if which == 'A' else 2).split()))
A25, A24, B25, B24 = cone(25, 'A'), cone(24, 'A'), cone(25, 'B'), cone(24, 'B')
a, a2 = A25[4], A24[4]  # both cones A are multiples of U^4 S^4
assert all(x == 0 for i, x in enumerate(A25) if i != 4) and all(x == 0 for i, x in enumerate(A24) if i != 4)
comb_ = [(a * y - a2 * x) % Q for x, y in zip(B25, B24)]  # minor / (U^4 S^4) as a form of degree 10 (U-power index)
# target U^2 S^2 (U^6 - S^6): U^a S^(10-a) coefficients at a = 2: -1, a = 8: +1
nz = {i: x for i, x in enumerate(comb_) if x}
ok = set(nz) == {2, 8} and (nz[2] + nz[8]) % Q == 0
out.append(f"  minor/U^4S^4 coefficients (U-power: value) = {nz}; proportional to U^2 S^2 (U^6 - S^6): {ok}")

out.append("4. pairing of psi increments")
inc = [psi(p + 1) - psi(p) for p in range(0, 9)]
out.append(f"  increments psi(p+1)-psi(p), p = 0..8: {inc}")
for e in range(2, 6):
    out.append(f"  (2e,2) with e={e}: tight={2 * mu(2 * e, 2) == psi(2 * e)}, e even={e % 2 == 0}")
print("\n".join(out))
