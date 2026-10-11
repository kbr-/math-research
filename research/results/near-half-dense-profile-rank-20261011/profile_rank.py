#!/usr/bin/env python3
"""Least degree at which the cube's profile lies in the span of the profiles of dense rows.

Statement tested (entry-2026-10-11-symmetric-flat-ceiling, lem:symmetric-profile-criterion and
lem:flat-profile-parity). Over F_2, let w independent linear forms have atoms A_mu, mu in F_2^w
nonzero, all nonempty and large, with parities a_mu = |A_mu| mod 2, and enough variables in no
form. Let V_0 = {forms = 0} (through the origin) and V_1 = {forms = their values at the all-ones
point}. With u = z/(1+z), the profile of V = {forms = c} with a set T of variables, t_mu of them
in A_mu and tau_mu = t_mu mod 2, divided by (1+z)^n, is

    P = u^|T| * sum over eps with sum eps_mu mu = c of prod_mu F(a_mu, tau_mu, eps_mu),

    F = [eps = tau] if a = tau, and (u+1 if eps = tau else u) if a != tau.

A symmetric static barrier at D against the two rows exists iff 1 is not in the span of the P with
|T| <= D - w. This script computes Dstar = the least D with 1 in that span.

Question: is Dstar linear in w or of the order of 2^w? prop:symmetric-flat-row-ceiling gives
Dstar <= w + o_0 + o_1 - 1 when both rows have an odd atom, o_c the number of odd atoms; for all
atoms odd that is w + 2^(w+1) - 3 = 7, 16, 34 at w = 2, 3, 4.

Expectations, written before the run.
- Control (formula): for one instance at w = 2 with n = 10, the profile computed by enumerating the
  points of the flat equals (1+z)^n P(u) for every flat and every T tried; the script asserts it.
- Control (theorem): every Dstar printed is at most the proposition's bound when an atom is odd
  (the two rows have the same atoms, so o_1 = o_0), and Dstar = w when all atoms are even (the
  profile of V_0 at empty T is the cube's). Asserted.
- Control (width one): one odd atom gives Dstar = 1, the two rows covering the cube.
- The statement: no prediction. The outcomes differ at w = 3 and 4: values near the bounds 16 and
  34 mean exponential; values of a few times w mean linear. All parity patterns are run at
  w = 1, 2, 3; at w = 4 the all-odd pattern, the all-even one and 40 patterns from a seeded
  generator.
"""
import argparse
import itertools
import random


def mul(p, k):
    """Multiply the F_2[u] polynomial p (an int bitmask) by 0, 1, u or u+1 (k = 0, 1, 2, 3)."""
    if k == 0:
        return 0
    if k == 1:
        return p
    if k == 2:
        return p << 1
    return p ^ (p << 1)


def factor(a, tau):
    """Coefficients (at eps = 0, at eps = 1) of the atom's factor, coded as in mul."""
    if a == tau:
        return (1, 0) if tau == 0 else (0, 1)
    return (3, 2) if tau == 0 else (2, 3)


def coefficient_polys(w, a, targets):
    """For every tau, the polynomials C_tau at each target c; returns {|tau|: set of polys}."""
    size = 1 << w
    atoms = list(range(1, size))
    out = {}

    def rec(i, vec, weight):
        if i == len(atoms):
            for c in targets:
                if vec[c]:
                    out.setdefault(weight, set()).add(vec[c])
            return
        mu = atoms[i]
        for tau in (0, 1):
            k0, k1 = factor(a[i], tau)
            new = [mul(vec[g], k0) ^ mul(vec[g ^ mu], k1) for g in range(size)]
            if any(new):
                rec(i + 1, new, weight + tau)

    start = [0] * size
    start[0] = 1
    rec(0, start, 0)
    return out


def insert(basis, p):
    while p:
        h = p.bit_length() - 1
        if h not in basis:
            basis[h] = p
            return
        p ^= basis[h]


def in_span(basis, p):
    while p:
        h = p.bit_length() - 1
        if h not in basis:
            return False
        p ^= basis[h]
    return True


def dstar(w, a, cap):
    atoms = list(range(1, 1 << w))
    c1 = 0
    for mu, par in zip(atoms, a):
        if par:
            c1 ^= mu
    polys = coefficient_polys(w, a, sorted({0, c1}))
    basis = {}
    for d in range(w, cap + 1):
        for weight, cs in polys.items():
            j = d - w - weight
            if j >= 0:
                for c in cs:
                    insert(basis, c << (weight + j))
        if in_span(basis, 1):
            return d
    return None


def brute_control():
    """w = 2, atoms of sizes 3, 2, 3 and two free variables: enumeration against the formula."""
    sizes = {1: 3, 2: 2, 3: 3}
    free = 2
    var_atom = []
    for mu, s in sizes.items():
        var_atom += [mu] * s
    var_atom += [0] * free
    n = len(var_atom)
    a = [sizes[mu] % 2 for mu in (1, 2, 3)]
    checked = 0
    for c in range(4):
        for tset in ((), (0,), (0, 1), (3,), (0, 3, 5), (8,), (0, 8, 9), (5, 6), (0, 1, 2, 3, 5)):
            coeff = [0] * (n + 1)
            for x in itertools.product((0, 1), repeat=n):
                if any(x[i] == 0 for i in tset):
                    continue
                val = 0
                for i, bit in enumerate(x):
                    if bit:
                        val ^= var_atom[i]
                if val == c:
                    coeff[sum(x)] ^= 1
            direct = sum(b << k for k, b in enumerate(coeff))
            t = {mu: sum(1 for i in tset if var_atom[i] == mu) for mu in (1, 2, 3)}
            vec = [1, 0, 0, 0]
            for idx, mu in enumerate((1, 2, 3)):
                k0, k1 = factor(a[idx], t[mu] % 2)
                vec = [mul(vec[g], k0) ^ mul(vec[g ^ mu], k1) for g in range(4)]
            p = vec[c] << len(tset)
            formula = 0
            for i in range(p.bit_length()):
                if (p >> i) & 1:
                    term = 1 << i
                    for _ in range(n - i):
                        term ^= term << 1
                    formula ^= term
            assert direct == formula, (c, tset)
            checked += 1
    return checked


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", required=True)
    args = parser.parse_args()
    lines = ["control: %d profiles at w = 2, n = 10 agree with enumeration" % brute_control()]
    rng = random.Random(20261011)
    for w in (1, 2, 3, 4):
        m = (1 << w) - 1
        if w <= 3:
            patterns = list(itertools.product((0, 1), repeat=m))
        else:
            patterns = [(1,) * m, (0,) * m] + [tuple(rng.randint(0, 1) for _ in range(m))
                                                for _ in range(40)]
        worst = (-1, None)
        hist = {}
        for a in patterns:
            d = dstar(w, a, w + 2 * m + 2)
            assert d is not None, (w, a)
            odd = sum(a)
            if odd == 0:
                assert d == w, (w, a, d)
            else:
                assert d <= w + 2 * odd - 1, (w, a, d)
            if w == 1 and a == (1,):
                assert d == 1
            hist[d] = hist.get(d, 0) + 1
            if d > worst[0]:
                worst = (d, a)
            if a == (1,) * m:
                lines.append("w = %d all atoms odd: Dstar = %d (proposition's bound %d)"
                             % (w, d, w + 2 * m - 1))
        lines.append("w = %d, %d patterns: largest Dstar = %d at parities %s; histogram %s"
                     % (w, len(patterns), worst[0], "".join(map(str, worst[1])),
                        sorted(hist.items())))
    with open(args.out, "w") as handle:
        handle.write("\n".join(lines) + "\n")
    print("\n".join(lines))


if __name__ == "__main__":
    main()
