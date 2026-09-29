"""Weierstrass count of a caterpillar component from its far-near window (29 September 2026, cycle
bmd-20260929-z; prop:cube-caterpillar-component-count).

A component with F far roots, one visible root and n near roots (lambda = 3/2) has the limit space
  Pol_<P_n  +  phi Pol_<n  +  S^-3 Pol_<P_F(1/S)  +  S^-l phi Pol_<F(1/S)  +  S^-l W,
with P_k = binom(k,2), where W is the limit of the far-near block. W reaches S^-p at 0 and S^q at infinity:
a consecutive window [-p, q] has p + q + 1 = F n; a tied pair of windows gives <S^-(p-1), ..., S^(q-1)> plus
one combination S^q + kappa S^-p, with p + q = F n. The Pluecker formula on P^1 with generic local orders gives
the number of non-branch Weierstrass points. Prints it for the observed components and for predictions.
"""
from fractions import Fraction as Fr
from math import comb

LAM = Fr(3, 2)


def count(F, n, p, q):
    Pn, PF = comb(n, 2), comb(F, 2)
    R = comb(F + n + 1, 2)
    assert Pn + n + PF + F + F * n == R and p >= F - 1 and q >= n - 1 and p + q in (F * n - 1, F * n)
    int0 = comb(Pn + n, 2) - sum(range(3, PF + 3))
    half0 = (F * n + F) * (-LAM - p) + comb(F * n + F, 2)
    s1 = (n + F) * (-LAM) + comb(n + F, 2) + comb(R - n - F, 2)
    intinf = -comb(Pn, 2) + sum(range(3, PF + F + 3))
    halfinf = (F * n + n) * (LAM - q) + comb(F * n + n, 2)
    return comb(R, 2) - (int0 + half0) - s1 - (intinf + halfinf)


CASES = [
    ('N=5 scale 1 (binary face, F=1, n=3, window [0,2])', 1, 3, 0, 2, 3),
    ('N=6 scale 1 (binary face, F=1, n=4, window [0,3])', 1, 4, 0, 3, 6),
    ('N=5 scale 2 (F=2, n=2, tie of [-2,1] and [-1,2])', 2, 2, 2, 2, 12),
    ('N=6 scale 2 (F=2, n=3, window [-2,3])', 2, 3, 2, 3, 14),
    ('N=6 scale 3 (F=3, n=2, window [-3,2])', 3, 2, 3, 2, 14),
]
for name, F, n, p, q, observed in CASES:
    print(f'{name}: count {count(F, n, p, q)}, observed {observed}')
for name, F, n, p, q in [('N=7 scale 2 (F=2, n=4, window [-3,4])', 2, 4, 3, 4),
                         ('N=7 scale 3 (F=3, n=3, window [-4,4])', 3, 3, 4, 4)]:
    print(f'{name}: predicted count {count(F, n, p, q)}')
for F in range(1, 6):
    print(f'F={F}:', [f'n={n}: ' + ','.join(str(count(F, n, p, F * n - 1 - p)) for p in range(F - 1, F * n - n + 1))
                      for n in range(1, 5)])
