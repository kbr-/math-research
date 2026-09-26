"""Exact non-collision part of Delta_nu for n = 3 degree vectors, over Q (bmd-r131).

Statement examined.  conj:cube-limit-determinant-squarefree: for nu_r = d - |r| on three variables (the collision
limit U_d of {0,1}^4), the part of Delta_nu(a1, a2, a3) prime to the collision forms a_i, a_i - a_j is squarefree.
Delta_nu is homogeneous, so it is determined by D(x, y) = Delta_nu(x, y, 1).  The determinant is computed exactly by a
fraction-free (Bareiss) determinant with polynomial entries in x, y (sympy).
The collision forms x, y, x - 1, y - 1, x - y are divided out with their exact multiplicities, and the rest is factored
over Q to look for structure (factor degrees, symmetry) in the non-collision part.
Usage: python3 bmd_cube_nu_noncollision3.py d [d ...]
"""
import sys
import time
import itertools
import sympy as sp

x, y = sp.symbols('x y')


def sqrtser(a, N):
    return [sp.binomial(sp.Rational(1, 2), k) * a ** k for k in range(N)]


def mul(p, q, N):
    return [sp.expand(sum(p[i] * q[c - i] for i in range(c + 1))) for c in range(N)]


def delta_at(nu, avals):
    N = sum(v + 1 for v in nu.values())
    rows = []
    for r, deg in nu.items():
        w = [sp.Integer(1)] + [sp.Integer(0)] * (N - 1)
        for i in range(3):
            if r[i]:
                w = mul(w, sqrtser(avals[i], N), N)
        for j in range(deg + 1):
            rows.append([sp.Integer(0)] * j + w[:N - j])
    return sp.Matrix(rows).det(method='bareiss'), N


for spec in sys.argv[1:]:
    t0 = time.time()
    d = int(spec)
    nu = {r: max(d - sum(r), -1) for r in itertools.product((0, 1), repeat=3)}
    nu = {r: v for r, v in nu.items() if v >= 0}
    N = sum(v + 1 for v in nu.values())
    DEG = sum(range(N)) - sum(q * (q + 1) // 2 for q in nu.values())  # sum of orders minus sum over T-shifts
    # total degree of Delta in a: sum over rows of (order - shift) = sum_{k<N} k - sum_r sum_{j<=nu_r} j
    D = sp.expand(delta_at(nu, (x, y, 1))[0])
    c, facs = sp.factor_list(D)
    colls = {x, y, x - 1, y - 1, x - y}
    col = [(str(f), e) for f, e in facs if sp.expand(f) in colls or sp.expand(-f) in colls]
    rest = [(f, e) for f, e in facs if not (sp.expand(f) in colls or sp.expand(-f) in colls)]
    print(f"d={d} N={N} deg={DEG}: collision factors {col}; non-collision factors "
          f"{[(str(f), e, sp.Poly(f, x, y).total_degree()) for f, e in rest]}; "
          f"squarefree {all(e == 1 for f, e in rest)}  ({time.time() - t0:.1f} s)", flush=True)
