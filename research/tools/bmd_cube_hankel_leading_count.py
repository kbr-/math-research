"""Leading-monomial count for products of 2x2 Hankel minors (cycle bmd-20261001-b).

h_ij = t_i t_{j+1} - t_j t_{i+1} (1 <= i < j <= n) has lex-leading monomial t_i t_{j+1} (t_1 > t_2 > ...), a pair
(p, q) with q - p >= 2.  The leading monomial of h_ab h_cd is the product of the two pairs.  D(n) = number of
degree-4 monomials in t_1..t_{n+1} that split into two pairs with gap >= 2.  Distinct leading monomials are linearly
independent, so the span of the products has dimension >= D(n), and the number of quadratic relations is
<= #products - D(n).  Compare with the target n^2(n^2-1)/12 - C(n-1,4) (image dimension if the relations are exactly
the two Pluecker systems) for n <= 40.
"""
from itertools import combinations_with_replacement
from math import comb

def D(n):
    cnt = 0
    for m in combinations_with_replacement(range(1, n + 2), 4):
        a, b, c, d = m
        # partitions of a sorted multiset into two pairs: (a,b)(c,d), (a,c)(b,d), (a,d)(b,c)
        if any(q1 - p1 >= 2 and q2 - p2 >= 2 for (p1, q1), (p2, q2) in (((a, b), (c, d)), ((a, c), (b, d)), ((a, d), (b, c)))):
            cnt += 1
    return cnt

bad = 0
for n in range(4, 41):
    P = comb(comb(n, 2) + 1, 2)
    target = n * n * (n * n - 1) // 12 - comb(n - 1, 4)
    d = D(n)
    if d != target:
        bad += 1
    if n <= 10 or d != target:
        print(f"n = {n}: products {P}, D(n) = {d}, target image dimension {target}, relations bound {P - d}")
print("n = 4..40 with D(n) != target:", bad)
