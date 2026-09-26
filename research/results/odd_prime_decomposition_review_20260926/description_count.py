"""Counting test for the decomposition review (odd-prime thread, 26 Sept 2026): bits needed to describe an
arbitrary family of S = n^K blocks of h dense affine forms on N = n(n+1) cells over F_3, against a rough upper
count for families arising from a derivation of S lines, where each new line's new form is a combination of two
earlier forms (two premise indices, two coefficients, one constant, a rule tag)."""
from math import log2
for n, K, h in [(100, 1, 20), (1000, 1, 30)]:
    N = n * (n + 1); S = n ** K
    arb = S * h * N * log2(3)
    der = S * (2 * log2(S) + 2 * log2(3) + 2)
    print(n, K, h, 'arbitrary bits %.3g' % arb, 'derivation bits %.3g' % der, 'ratio %.3g' % (arb / der))
