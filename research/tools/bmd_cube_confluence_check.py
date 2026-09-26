"""Exact check of lem:cube-confluence-valuation for n = 2 (written by the bmd-r107 referee).

For several degree vectors nu on {0,1}^2 and fixed rational a_1, compares the a_2-adic valuation of
Delta_nu with e(nu) and the leading coefficient with Delta_{nu'}(a_1).
"""
import sympy as sp, itertools, random, sys
def sqrtser(a,N):  # coefficients of (1+aT)^{1/2}
    return [sp.binomial(sp.Rational(1,2),k)*a**k for k in range(N)]
def mul(p,q,N):
    return [sp.expand(sum(p[i]*q[c-i] for i in range(c+1))) for c in range(N)]
def Delta(nu,avars):
    n=len(avars); rows=[]; N=sum(v+1 for v in nu.values())
    for r,v in nu.items():
        w=[sp.Integer(1)]+[sp.Integer(0)]*(N-1)
        for i in range(n):
            if r[i]: w=mul(w,sqrtser(avars[i],N),N)
        for j in range(v+1):
            rows.append([sp.Integer(0)]*j+w[:N-j])
    return sp.expand(sp.Matrix(rows).det(method='bareiss'))
a2=sp.symbols("a2"); a1=sp.Rational(-5,11)
random.seed(1)
cases=[{(0,0):3,(1,0):2,(0,1):2,(1,1):1},{(0,0):1,(1,0):-1,(0,1):-1,(1,1):2},{(0,0):2,(1,0):1,(0,1):-1,(1,1):0}]
for t in range(8):
    nu={r:random.randint(-1,2) for r in itertools.product([0,1],repeat=2)}
    if sum(v+1 for v in nu.values())>0: cases.append(nu)
for nu in cases:
    D=Delta(nu,[a1,a2])
    e=sum((nu[(r,0)]+1)*(nu[(r,1)]+1) for r in (0,1))
    nup={(r,):nu[(r,0)]+nu[(r,1)]+1 for r in (0,1)}
    P=sp.Poly(D,a2); val=min(m[0] for m in P.monoms())
    lead=sp.expand(sp.cancel(D/a2**val)).subs(a2,0)
    Dp=Delta(nup,[a1])
    print(nu,'val',val,'e',e,'ratio',sp.simplify(lead/Dp),flush=True)
