"""Check over F2[Y,Z], n = 1..6: F(Z) = prod(1+Z Y_i) + Z prod(1+Y_i) + Z + 1 equals Z (Z+1) G(Z) with
G = sum_{l<i} Y_i Y_l prod_{j<l}(1+Z Y_j) prod_{l<j<i}(1+Y_j), the telescoped second divided difference.
Also the general affine form P = prod(a_i + b_i Z): P - P(0) - Z (P(1) - P(0)) = Z (Z+1) * sum_{l<i} b_i b_l
prod_{j<l}(a_j + b_j Z) prod_{l<j<i}(a_j + b_j) prod_{j>i} a_j, for n = 1..5.
Control: dropping the j<l prefix must break the identity for some n >= 2 (printed)."""
import sympy as sp


def check(n):
    Y = sp.symbols(f'y1:{n + 1}')
    Z = sp.Symbol('Z')
    prod = lambda xs: sp.Mul(*xs) if xs else sp.Integer(1)
    F = prod([1 + Z * y for y in Y]) + Z * prod([1 + y for y in Y]) + Z + 1
    G = sum(Y[i] * Y[l] * prod([1 + Z * Y[j] for j in range(l)]) * prod([1 + Y[j] for j in range(l + 1, i)])
            for i in range(n) for l in range(i))
    bad = sum(Y[i] * Y[l] * prod([1 + Y[j] for j in range(l + 1, i)]) for i in range(n) for l in range(i))
    gens = list(Y) + [Z]
    ok = sp.Poly(sp.expand(F - Z * (Z + 1) * G), *gens, modulus=2).is_zero
    ctl = sp.Poly(sp.expand(F - Z * (Z + 1) * bad), *gens, modulus=2).is_zero if n >= 2 else None
    return ok, ctl


def check_general(n):
    A = sp.symbols(f'a1:{n + 1}')
    Bv = sp.symbols(f'b1:{n + 1}')
    Z = sp.Symbol('Z')
    prod = lambda xs: sp.Mul(*xs) if xs else sp.Integer(1)
    P = lambda z: prod([A[i] + Bv[i] * z for i in range(n)])
    lhs = P(Z) - P(0) - Z * (P(1) - P(0))
    G = sum(Bv[i] * Bv[l] * prod([A[j] + Bv[j] * Z for j in range(l)])
            * prod([A[j] + Bv[j] for j in range(l + 1, i)]) * prod([A[j] for j in range(i + 1, n)])
            for i in range(n) for l in range(i))
    return sp.Poly(sp.expand(lhs - Z * (Z + 1) * G), *(list(A) + list(Bv) + [Z]), modulus=2).is_zero


def check_grouping(n):
    """Part (c) at k=1 in Z: h = f/Z + f/(Z+1) = sum_i [1 + prod_{l<i}(1+Y_l)] Y_i prod_{l>i}(1+Z Y_l); and the
    Boolean values of h's Z^m coefficients are binomial(w-1, m+1) + prod(1+y_i) mod 2 (w the weight of y)."""
    import itertools
    Y = sp.symbols(f'y1:{n + 1}')
    Z = sp.Symbol('Z')
    prod = lambda xs: sp.Mul(*xs) if xs else sp.Integer(1)
    F = prod([1 + Z * y for y in Y]) + Z * prod([1 + y for y in Y]) + Z + 1
    H = sum((1 + prod([1 + Y[l] for l in range(i)])) * Y[i] * prod([1 + Z * Y[l] for l in range(i + 1, n)])
            for i in range(n))
    ok = sp.Poly(sp.expand(F - Z * (Z + 1) * H), *(list(Y) + [Z]), modulus=2).is_zero
    coeffs = sp.Poly(sp.expand(H), Z).all_coeffs()[::-1]
    values = True
    for bits in itertools.product((0, 1), repeat=n):
        w = sum(bits)
        sub = dict(zip(Y, bits))
        for m, c in enumerate(coeffs):
            want = (sp.binomial(w - 1, m + 1) + prod([1 + b for b in bits])) % 2
            values &= int(c.subs(sub)) % 2 == want
    return ok, values


for n in range(1, 7):
    print('grouping', n, check_grouping(n))
for n in range(1, 7):
    print('special', n, check(n))
for n in range(1, 6):
    print('general', n, check_general(n))
