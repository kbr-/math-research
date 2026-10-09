#!/usr/bin/env python3
"""Covers of the two-colourings of Z_p modulo complement by the p translates of a multiplier-invariant subspace
(side notebook near-half-pc-degree, entry-2026-10-09-translate-covers).

Statement tested: for p = n+1 prime with 2 a primitive root and a linear subspace V of codimension w whose
space of forms L (even subsets of Z_p) is invariant under i -> 2i, hence under all multipliers, the p translates
of V cover the space only when the covering sum p / 2^w is large; in particular not for p/2 < 2^w < p.
The invariant spaces of forms of dimension w are the kernels of g(T) on the even subsets, T: S -> 2S, for the
divisors g of x^n - 1 over F_2 of degree w (the even subsets form a free cyclic module); the script asserts
dim ker g(T) = deg g.  For each it counts the colourings (c_0 = 0) with no translate in V.  numpy does the
vectorised parity tests.  Usage: translate_covers.py P [P ...]   (P <= 23)
"""
import json
import sys

import numpy as np


def polymod(a, b):
    db = b.bit_length() - 1
    while a and a.bit_length() - 1 >= db:
        a ^= b << (a.bit_length() - 1 - db)
    return a


def kernel(rows, ncols):
    """Basis of {v : sum_i v_i rows[i] = 0} over F_2 (rows are ints); v as int over row indices."""
    piv, basis = {}, []
    for i, r in enumerate(rows):
        tag = 1 << i
        while r:
            h = r.bit_length() - 1
            if h in piv:
                r ^= piv[h][0]
                tag ^= piv[h][1]
            else:
                piv[h] = (r, tag)
                break
        if not r:
            basis.append(tag)
    return basis


def parity(x):
    x = x ^ (x >> 16)
    x = x ^ (x >> 8)
    x = x ^ (x >> 4)
    x = x ^ (x >> 2)
    x = x ^ (x >> 1)
    return x & 1


for arg in sys.argv[1:]:
    p = int(arg)
    n = p - 1
    assert p <= 23 and all(p % q for q in range(2, p)), p
    order, x = 1, 2
    while x != 1:
        x, order = 2 * x % p, order + 1
    assert order == n, 'two must be a primitive root'
    double = lambda S: sum(1 << (2 * i % p) for i in range(p) if S >> i & 1)
    even = [1 | 1 << i for i in range(1, p)]                 # basis {0, i} of the even subsets
    colourings = np.arange(1 << n, dtype=np.uint32) << np.uint32(1)   # c_0 = 0, bits 1..n
    xn1 = (1 << n) | 1
    for w in range(1, n.bit_length()):
        if 2 ** w >= p:
            break
        for g in range(1 << w, 1 << (w + 1)):
            if polymod(xn1, g):
                continue
            images = []                                       # g(T) applied to each basis vector
            for S in even:
                acc, power = 0, S
                for j in range(w + 1):
                    if g >> j & 1:
                        acc ^= power
                    power = double(power)
                images.append(acc)
            ker = kernel(images, p)
            forms = [0] * len(ker)
            for k, tag in enumerate(ker):
                for i in range(n):
                    if tag >> i & 1:
                        forms[k] ^= even[i]
            assert len(forms) == w, (p, w, g, len(forms))
            span = {0}
            for f in forms:
                span |= {v ^ f for v in span}
            assert len(span) == 2 ** w and all(double(f) in span for f in forms), 'invariant under doubling'
            covered = np.zeros(1 << n, dtype=bool)
            for b in range(p):
                inside = np.ones(1 << n, dtype=bool)
                for f in forms:
                    shifted = sum(1 << ((i + b) % p) for i in range(p) if f >> i & 1)
                    inside &= parity(colourings & np.uint32(shifted)) == 0
                covered |= inside
            missed = int((~covered).sum())
            print(json.dumps({'p': p, 'n': n, 'w': w, 'divisor': bin(g)[2:], 'cover_sum': round(p / 2 ** w, 4),
                              'uncovered': missed, 'uncovered_fraction': round(missed / 2 ** n, 5),
                              'covers': missed == 0}), flush=True)
