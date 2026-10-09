#!/usr/bin/env python3
"""Truncated Buchberger completion over F_2: exact polynomial-calculus degree of small systems.

Implements the pair condition of the truncated Buchberger criterion (side notebook
near-half-pc-degree, entry-2026-10-09-truncated-buchberger): for a degree-compatible order, if
every pair of a set G whose leading monomials have an lcm of degree at most D has an S-polynomial
that reduces to zero by G, then the multiples of G within degree D form the degree-D
polynomial-calculus closure, and it contains 1 only if G contains a constant.

Polynomials are sets of monomials; a monomial is a tuple of exponents.  The order is degree, then
the exponent tuple.  The Boolean axioms x_i^2 + x_i are ordinary generators.  Pure Python: meant
for small systems (a few hundred leading monomials), as a checker and reference implementation.

  check_pairs(G, D)     pairs with lcm degree <= D whose S-polynomial does not reduce to zero
  complete(G, D)        add remainders until the pair condition holds; all added elements lie in
                        the degree-D closure of G
  pc_degree(axioms, n, max_degree)
                        least D in 0..max_degree with 1 in the degree-D closure of the axioms and
                        the Boolean axioms (axioms of degree above D are not used), or None
"""
import argparse
import itertools
import json


def key(m):
    return (sum(m), m)


def lm(f):
    return max(f, key=key)


def mul(f, m):
    return {tuple(a + b for a, b in zip(t, m)) for t in f}


def divides(a, b):
    return all(x <= y for x, y in zip(a, b))


def reduce_top(f, leads):
    """Top-reduce f by the polynomials in leads (dict leading monomial -> polynomial)."""
    f = set(f)
    while f:
        m = lm(f)
        for lead, g in leads.items():
            if divides(lead, m):
                f ^= mul(g, tuple(a - b for a, b in zip(m, lead)))
                break
        else:
            return f
    return f


def s_poly(g, h):
    a, b = lm(g), lm(h)
    lcm = tuple(max(x, y) for x, y in zip(a, b))
    return lcm, mul(g, tuple(x - y for x, y in zip(lcm, a))) ^ mul(h, tuple(x - y for x, y in zip(lcm, b)))


def coprime(a, b):
    return all(x == 0 or y == 0 for x, y in zip(a, b))


def _leads(G):
    leads = {}
    for g in G:
        g = reduce_top(g, leads)
        if g:
            leads[lm(g)] = frozenset(g)
    return leads


def check_pairs(G, D):
    """Return the pairs (lcm, remainder) with lcm degree <= D that are not resolved by G."""
    polys = [frozenset(g) for g in G if g]
    leads = {}
    for g in polys:
        leads.setdefault(lm(g), g)
    bad = []
    for g, h in itertools.combinations(polys, 2):
        a, b = lm(g), lm(h)
        if coprime(a, b) and sum(a) and sum(b):
            continue
        lcm, s = s_poly(g, h)
        if sum(lcm) > D:
            continue
        r = reduce_top(s, leads)
        if r:
            bad.append((lcm, frozenset(r)))
    return bad


def complete(G, D):
    """Truncated completion: returns (leads, has_constant)."""
    leads = _leads([g for g in G if g and sum(lm(g)) <= D])
    todo = list(itertools.combinations(list(leads), 2))
    while todo:
        a, b = todo.pop()
        if a not in leads or b not in leads or coprime(a, b):
            continue
        lcm, s = s_poly(leads[a], leads[b])
        if sum(lcm) > D:
            continue
        r = reduce_top(s, leads)
        if r:
            new = lm(r)
            if sum(new) == 0:
                return leads, True
            todo.extend((new, c) for c in leads)
            leads[new] = frozenset(r)
    return leads, any(sum(m) == 0 for m in leads)


def boolean_axioms(n):
    out = []
    for i in range(n):
        sq = tuple(2 if j == i else 0 for j in range(n))
        x = tuple(1 if j == i else 0 for j in range(n))
        out.append({sq, x})
    return out


def pc_degree(axioms, n, max_degree):
    for D in range(0, max_degree + 1):
        _, const = complete(boolean_axioms(n) + [set(a) for a in axioms], D)
        if const:
            return D
    return None


def affine_product(n, forms):
    """Multilinear-free product of affine forms given as (mask, const) pairs, as a polynomial."""
    poly = {tuple([0] * n)}
    for mask, const in forms:
        terms = [tuple(1 if j == i else 0 for j in range(n)) for i in range(n) if mask >> i & 1]
        if const:
            terms.append(tuple([0] * n))
        new = set()
        for t in poly:
            for u in terms:
                new ^= {tuple(a + b for a, b in zip(t, u))}
        poly = new
    return poly


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("instance", help="parity 2-clause instance: 'n m' then m lines 'mask1 c1 mask2 c2'")
    ap.add_argument("--max-degree", type=int, required=True)
    args = ap.parse_args()
    with open(args.instance) as fh:
        n, m = map(int, fh.readline().split())
        axioms = []
        for _ in range(m):
            a, ca, b, cb = map(int, fh.readline().split())
            axioms.append(affine_product(n, [(a, ca), (b, cb)]))
    print(json.dumps({"n": n, "m": m, "pc_degree": pc_degree(axioms, n, args.max_degree),
                      "max_degree": args.max_degree}))


if __name__ == "__main__":
    main()
