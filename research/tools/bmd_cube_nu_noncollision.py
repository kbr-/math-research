"""Exact non-collision parts of Delta_nu for n = 2 degree vectors (bmd-r130).

Statement examined.  conj:cube-monotone-squarefree for n = 2: for a monotone degree vector nu = (nu_00, nu_10, nu_01,
nu_11), the part of Delta_nu(a1, a2) prime to a1, a2, a1 - a2 is squarefree.  Delta_nu is homogeneous, so it is
determined by D(x) = Delta_nu(1, x).  This script computes D(x) exactly over Q (fraction-free determinant of the
truncated expansions of T^j w^r, w = (1 + T)^{1/2} and (1 + xT)^{1/2}, as in bmd_cube_nu_factor.py), removes the
factors x and x - 1 (the collision forms a2 and a1 - a2; a1 is the dehomogenizing variable, whose multiplicity is
deg - deg D), and prints the factorization of the rest over Q with its discriminant status, looking for a pattern in
the non-collision factors (degrees, rational roots, hypergeometric type).
Usage: python3 bmd_cube_nu_noncollision.py NU [NU ...]   (NU = a,b,c,d)
"""
import sys
import time
import sympy as sp

x = sp.symbols('x')


def sqrtser(a, N):
    return [sp.binomial(sp.Rational(1, 2), k) * a ** k for k in range(N)]


def mul(p, q, N):
    return [sp.expand(sum(p[i] * q[c - i] for i in range(c + 1))) for c in range(N)]


def delta(nu):
    N = sum(v + 1 for v in nu)
    rows = []
    for r in range(4):
        w = [sp.Integer(1)] + [sp.Integer(0)] * (N - 1)
        if r & 1:
            w = mul(w, sqrtser(sp.Integer(1), N), N)
        if r & 2:
            w = mul(w, sqrtser(x, N), N)
        for j in range(nu[r] + 1):
            rows.append([sp.Integer(0)] * j + w[:N - j])
    M = sp.Matrix(rows)
    return sp.Poly(M.det(method='bareiss'), x), N


for spec in sys.argv[1:]:
    t0 = time.time()
    nu = [int(v) for v in spec.split(',')]
    assert nu[0] >= nu[1] and nu[0] >= nu[2] and nu[1] >= nu[3] and nu[2] >= nu[3], "not monotone"
    D, N = delta(nu)
    c, facs = sp.factor_list(D.as_expr())
    col = {str(f): e for f, e in facs if sp.Poly(f, x).degree() == 1 and sp.Poly(f, x).eval(0) * sp.Poly(f, x).eval(1) == 0}
    rest = [(f, e) for f, e in facs if not (sp.Poly(f, x).degree() == 1 and sp.Poly(f, x).eval(0) * sp.Poly(f, x).eval(1) == 0)]
    sqfree = all(e == 1 for f, e in rest)
    print(f"nu={spec} N={N}: collision factors {col}; non-collision factors "
          f"{[(str(sp.factor(f)), e) for f, e in rest]}; squarefree {sqfree}; "
          f"non-collision degree {sum(sp.Poly(f, x).degree() * e for f, e in rest)}  ({time.time() - t0:.1f} s)", flush=True)
