"""Surfaces meeting each collision plane in mu times its three double-double lines.

For mu >= 1, W_mu is the space of homogeneous pi of degree 3 mu in y1..y4 (r0 = 0, r_i = y_i)
such that for every collision plane D_ab (r_a = r_b) the restriction pi|_D is a scalar multiple
of prod_{dd lines of D} (r_c - r_d)^mu (the three forms r_c - r_d with {c,d} disjoint from {a,b}).
Computed over Q with sympy (small sizes); prints dim W_mu and the factorization of a basis.
"""
import itertools
import sys
import sympy as sp

y = sp.symbols('y1:5')
r = [sp.Integer(0)] + list(y)
pts = range(5)


def run(mu):
    k = 3 * mu
    mons = list(itertools.combinations_with_replacement(range(4), k))
    cs = sp.symbols('c0:%d' % len(mons))
    F = sum(c * sp.prod([y[i] for i in m]) for c, m in zip(cs, mons))
    lams = sp.symbols('l0:10')
    eqs = []
    for idx, (a, b) in enumerate(itertools.combinations(pts, 2)):
        rest = [x for x in pts if x not in (a, b)]
        target = sp.prod([(r[c] - r[d]) ** mu for c, d in itertools.combinations(rest, 2)])
        sol = sp.solve([r[a] - r[b]], y, dict=True)[0]
        free = [v for v in y if v not in sol]
        G = sp.expand(F.subs(sol) - lams[idx] * target.subs(sol))
        eqs += sp.Poly(G, *free).coeffs()
    unknowns = list(cs) + list(lams)
    A = sp.Matrix([[e.coeff(u) for u in unknowns] for e in eqs])
    ns = A.nullspace()
    print(f'mu={mu} degree {k}: dim W = {len(ns)}', flush=True)
    for v in ns:
        pol = sp.expand(F.subs(dict(zip(cs, v[:len(cs)]))))
        print('  ', sp.factor(pol), flush=True)


for mu in [int(x) for x in sys.argv[1:]]:
    run(mu)
