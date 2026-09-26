"""Real-rootedness of the non-collision part of Delta_nu for n = 2 (bmd-r109 route review).

Bridge test (Lee-Yang-type localization): for monotone nu on {0,1}^2 with entries <= MAX, compute
Delta_nu(1, x) exactly over Q (a_1 = 1, a_2 = x; sympy, fraction-free determinant), remove the
collision factors x and x - 1, and report the degree of the rest, how many of its roots are real,
and their signs.  Usage: bmd_cube_nu_real_roots.py MAX
"""
import itertools
import sys
import sympy as sp

x = sp.symbols('x')
mx = int(sys.argv[1])


def sqrtser(a, N):
    return [sp.binomial(sp.Rational(1, 2), k) * a ** k for k in range(N)]


def mul(p, q, N):
    return [sp.expand(sum(p[i] * q[c - i] for i in range(c + 1))) for c in range(N)]


def delta(nu):
    N = sum(v + 1 for v in nu)
    s1, s2 = sqrtser(sp.Integer(1), N), sqrtser(x, N)
    rows = []
    for r in range(4):
        w = [sp.Integer(1)] + [sp.Integer(0)] * (N - 1)
        if r & 1:
            w = mul(w, s1, N)
        if r & 2:
            w = mul(w, s2, N)
        for j in range(nu[r] + 1):
            rows.append([sp.Integer(0)] * j + w[:N - j])
    return sp.Poly(sp.Matrix(rows).det(method='bareiss'), x)


for nu in itertools.product(range(-1, mx + 1), repeat=4):
    if not (nu[0] >= nu[1] >= nu[3] and nu[0] >= nu[2] >= nu[3]) or sum(v + 1 for v in nu) < 3:
        continue
    P = delta(nu)
    for f in (sp.Poly(x, x), sp.Poly(x - 1, x)):
        while P.degree() > 0 and P.rem(f).is_zero:
            P = P.quo(f)
    deg = P.degree()
    rr = [r for r in sp.real_roots(P)] if deg > 0 else []
    signs = ''.join('-' if r < 0 else ('+' if r > 0 else '0') for r in rr)
    print(f'nu={nu} rest degree {deg}, real roots {len(rr)} [{signs}]'
          f' {"ALL-REAL" if len(rr) == deg else "NONREAL"}', flush=True)
