#!/usr/bin/env python3
"""Exact degree-D polynomial-calculus closures over F_2 in the multilinear ring, with membership queries.

    from pc_closure import Closure
    c = Closure(axioms, nvars, D)        # axioms: iterables of monomial bit masks (0 is the constant)
    c.proper, c.dim, c.contains(poly), c.remainder(poly)

The closure C_D is the smallest space containing the axioms of degree at most D and closed under
multiplication of its members of degree below D by a variable; Booleanity is built in (x*x = x).
Monomials are ordered by degree descending, so a row's lowest set bit is its leading monomial; the
members of degree below D are spanned by the rows whose pivot has degree below D, and each such row is
multiplied by every variable until nothing new enters.  The remainder is canonical: no pivot position
stays set, so it is linear and two polynomials have equal remainders exactly when they differ by a
member.  Pure Python, for systems with a few thousand monomials of degree at most D.  Its tests compare
the refutation degree with tools/truncated_buchberger.py, an independent method; a committed provenance
run (research/results/common_multiplier_closure_module_20261016/cross_check.py) compares properness and
closure dimension with tools/f2_closure_degree.cpp, which uses the same elimination design and so checks
the implementation, not the convention.

Built after a hand-written closure in a research script had a non-canonical remainder and missed
members of degree below D arising from cancelling top terms (16 October 2026).
"""
import itertools


def monomials(nvars, dmax):
    """Monomial bit masks of degree at most dmax, degree descending, masks descending within a degree."""
    return [m for k in range(dmax, -1, -1) for m in sorted(
        (sum(1 << i for i in c) for c in itertools.combinations(range(nvars), k)), reverse=True)]


def degree(poly):
    return max((bin(m).count('1') for m in poly), default=-1)


def multiply(p, q):
    """Product in the multilinear ring over F_2 of two polynomials given as sets of masks."""
    out = set()
    for a in p:
        for b in q:
            out ^= {a | b}
    return out


class Closure:
    def __init__(self, axioms, nvars, D):
        self.nvars, self.D = nvars, D
        self.monos = monomials(nvars, D)
        self.index = {m: i for i, m in enumerate(self.monos)}
        self.rows = {}
        for a in axioms:
            a = set(a)
            if degree(a) <= D:
                self._add(self.vector(a))
        while True:
            added = False
            for p in [p for p in self.rows if bin(self.monos[p]).count('1') < D]:
                poly = self.poly(self.rows[p])
                for x in range(nvars):
                    if self._add(self.vector(multiply(poly, {1 << x}))):
                        added = True
            if not added:
                break
        self.proper = self.reduce(self.vector({0})) != 0
        self.dim = len(self.rows)

    def vector(self, poly):
        v = 0
        for m in poly:
            if bin(m).count('1') > self.D or m >> self.nvars:
                raise ValueError('a monomial above the closure degree or outside the variables has no coordinate')
            v ^= 1 << self.index[m]
        return v

    def poly(self, v):
        return {self.monos[i] for i in range(v.bit_length()) if v >> i & 1}

    def reduce(self, v):
        for p in sorted(self.rows):
            if v >> p & 1:
                v ^= self.rows[p]
        return v

    def _add(self, v):
        v = self.reduce(v)
        if not v:
            return False
        p = (v & -v).bit_length() - 1
        # Keep every stored row reduced at the new pivot, so remainders stay canonical.
        for q, row in list(self.rows.items()):
            if row >> p & 1:
                self.rows[q] = row ^ v
        self.rows[p] = v
        return True

    def remainder(self, poly):
        return self.poly(self.reduce(self.vector(poly)))

    def contains(self, poly):
        return self.reduce(self.vector(poly)) == 0


def refutation_degree(axioms, nvars, max_degree):
    """Least D <= max_degree with 1 in the degree-D closure, or None."""
    for D in range(0, max_degree + 1):
        if not Closure(axioms, nvars, D).proper:
            return D
    return None
