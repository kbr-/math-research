"""Check of the genus-0 collision-limit coefficient (bmd-r118, lem:cube-boundary-generator-invariant).

On the genus-0 curve w_1^2 = 1 + a_1 T, w_2^2 = 1 + a_2 T, the function psi = (a_1 - a_2) + a_2 w_1 - a_1 w_2 has a
double zero at p_0 (T = 0, w = 1), and psi^(2d) spans the functions of order 4d in L(2d H_inf).  Written in the basis
w^r T^j, its coefficient of w_1 w_2 T^(d-1) is claimed to be
    lambda_d = -(a_1 a_2)^d * sum_{k odd} C(2d, k) a_1^((k-1)/2) a_2^(d-(k+1)/2).
The script reduces psi^(2d) exactly (sympy, rational coefficients) and compares, for d = 1..DMAX.
Usage: bmd_cube_genus0_limit_check.py DMAX
"""
import sys
from math import comb
import sympy as sp

a1, a2, T, u, v = sp.symbols('a1 a2 T u v')


def reduce_uv(expr):
    """Reduce a polynomial in u = w_1, v = w_2 with u^2 = 1 + a1 T, v^2 = 1 + a2 T; return the (u v)-coefficient."""
    p = sp.Poly(sp.expand(expr), u, v)
    out = 0
    for (i, j), c in p.terms():
        if i % 2 == 1 and j % 2 == 1:
            out += c * (1 + a1 * T) ** (i // 2) * (1 + a2 * T) ** (j // 2)
    return sp.expand(out)


dmax = int(sys.argv[1])
for d in range(1, dmax + 1):
    psi = (a1 - a2) + a2 * u - a1 * v
    D = reduce_uv(psi ** (2 * d))
    degT = sp.Poly(D, T).degree()
    lam = sp.Poly(D, T).coeff_monomial(T ** (d - 1))
    claim = -(a1 * a2) ** d * sum(comb(2 * d, k) * a1 ** ((k - 1) // 2) * a2 ** (d - (k + 1) // 2)
                                  for k in range(1, 2 * d, 2))
    ok = sp.expand(lam - claim) == 0
    print(f'd={d}: deg_T of the w1w2 part = {degT} (<= d-1: {degT <= d - 1}); coefficient matches the formula: {ok}')
    sys.stdout.flush()
