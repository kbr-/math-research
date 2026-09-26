"""Exact factorization of Delta_nu for n = 2 degree vectors given on the command line (bmd-r108)."""
import sys
import sympy as sp

a1, a2 = sp.symbols('a1 a2')


def sqrtser(a, N):
    return [sp.binomial(sp.Rational(1, 2), k) * a ** k for k in range(N)]


def mul(p, q, N):
    return [sp.expand(sum(p[i] * q[c - i] for i in range(c + 1))) for c in range(N)]


def delta(nu):
    N = sum(x + 1 for x in nu)
    rows = []
    for r in range(4):
        w = [sp.Integer(1)] + [sp.Integer(0)] * (N - 1)
        if r & 1:
            w = mul(w, sqrtser(a1, N), N)
        if r & 2:
            w = mul(w, sqrtser(a2, N), N)
        for j in range(nu[r] + 1):
            rows.append([sp.Integer(0)] * j + w[:N - j])
    return sp.Matrix(rows).det(method='bareiss')


for spec in sys.argv[1:]:
    nu = [int(x) for x in spec.split(',')]
    print(spec, sp.factor_list(sp.expand(delta(nu))), flush=True)
