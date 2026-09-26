"""Local problem at a quadruple point r_a = r_b = r_c = r_d.

Coordinates x_a, x_b, x_c (x_d = 0).  For mu >= 1, is there a homogeneous P of degree mu with
P restricted to each of the six planes x_x = x_y equal to eps_xy (x_z - x_w)^mu, for signs eps
(any choice)?  Also reports, for the zero right-hand side, the space of P of degree mu vanishing
on all six planes (divisible by the A_3 discriminant).  Prints solvability per mu.
"""
import itertools
import sys
import sympy as sp

xa, xb, xc = sp.symbols('xa xb xc')
X = {'a': xa, 'b': xb, 'c': xc, 'd': sp.Integer(0)}
names = 'abcd'


def run(mu):
    mons = list(itertools.combinations_with_replacement(range(3), mu))
    v = [xa, xb, xc]
    cs = sp.symbols('c0:%d' % len(mons))
    P = sum(c * sp.prod([v[i] for i in m]) for c, m in zip(cs, mons))
    kap = sp.symbols('k0:6')
    eqs = []
    for idx, (x, y) in enumerate(itertools.combinations(names, 2)):
        z, w = [t for t in names if t not in (x, y)]
        sub = {}
        if X[x] != 0:
            sub = {X[x]: X[y]}
        else:
            sub = {X[y]: X[x]}
        free = [t for t in v if t not in sub]
        G = sp.expand(P.subs(sub) - kap[idx] * ((X[z] - X[w]) ** mu).subs(sub))
        eqs += sp.Poly(G, *free).coeffs() if G != 0 else []
    unknowns = list(cs) + list(kap)
    A = sp.Matrix([[sp.expand(e).coeff(u) for u in unknowns] for e in eqs])
    ns = A.nullspace()
    good = [n for n in ns]
    # dimension of solutions and whether some solution has all kappa nonzero
    K = sp.Matrix.hstack(*[n[len(cs):, :] for n in ns]) if ns else None
    ranks = K.rank() if K is not None else 0
    print(f'mu={mu}: solution space dim {len(ns)}, kappa-part rank {ranks}', flush=True)
    for n in ns:
        print('   kappa', list(n[len(cs):, 0]), 'P =', sp.factor(P.subs(dict(zip(cs, n[:len(cs), 0])))), flush=True)


for mu in [int(t) for t in sys.argv[1:]]:
    run(mu)
