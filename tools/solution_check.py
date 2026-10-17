#!/usr/bin/env python3
"""Refute a claimed closure member on a satisfiable pigeonhole board by evaluating it at the board's solutions.

On a board with m <= N, every assignment sending the pigeons injectively to holes satisfies Booleanity, the hole
and functionality monomials and each pigeon axiom 1 - sum_h x_ih, so every member of every PC closure of these
axioms vanishes there, in every characteristic. A polynomial claimed to lie in a closure (for instance u*E for a
claimed killer u of an error E) that is nonzero at a solution is therefore not in it. This is a necessary test,
not a membership proof; it works over any prime field, where tools/pc_closure.py works over F_2 only.

17 October 2026: a registered corollary claimed that x00*x11 kills every error of a family in characteristic 3;
x00*x11*(1+x22+x33)*x00 takes the value 2 at the solution 0->0, 1->1, 2->2, 3->4, so it was false, and the hand
check behind it had covered only one family.

Usage: solution_check.py --pigeons 4 --holes 8 --prime 3 "x00*x11 + x00*x11*x22 + x00*x11*x33"
Variables are x<pigeon><hole> with one-digit indices, or x<pigeon>_<hole>; terms are products of variables with an
optional integer coefficient first ("2*x01*x12"); "1" is the constant. Prints the first solution where the
polynomial is nonzero and exits 1, or the number of solutions checked and exits 0.
"""
import argparse
import itertools
import random
import re
import sys

VAR = re.compile(r'^x(\d+)_(\d+)$|^x(\d)(\d)$')


def parse(text):
    """The polynomial as a list of (coefficient, [(pigeon, hole), ...])."""
    terms = []
    for raw in re.split(r'(?<!^)\s*(?=[+-])', text.strip().replace(' ', '')):
        sign = -1 if raw.startswith('-') else 1
        factors = [f for f in raw.lstrip('+-').split('*') if f]
        coefficient, variables = sign, []
        for factor in factors:
            if factor.isdigit():
                coefficient *= int(factor)
                continue
            match = VAR.match(factor)
            if not match:
                raise ValueError(f'not a variable or integer: {factor!r}')
            pigeon, hole = (match.group(1), match.group(2)) if match.group(1) else (match.group(3), match.group(4))
            variables.append((int(pigeon), int(hole)))
        terms.append((coefficient, variables))
    return terms


def value(terms, assignment, prime):
    """The polynomial at the solution assignment[pigeon] = hole, modulo prime."""
    return sum(c for c, variables in terms if all(assignment[p] == h for p, h in variables)) % prime


def solutions(m, n, limit, seed=0):
    """All injections of m pigeons into n holes when there are at most `limit`, otherwise `limit` random ones."""
    total = 1
    for k in range(m):
        total *= n - k
    if total <= limit:
        yield from itertools.permutations(range(n), m)
        return
    rng = random.Random(seed)
    for _ in range(limit):
        yield tuple(rng.sample(range(n), m))


def check(m, n, prime, text, limit=200000):
    terms = parse(text)
    for p, h in (v for _, vs in terms for v in vs):
        if p >= m or h >= n:
            raise ValueError(f'x{p}{h} is not on a board with {m} pigeons and {n} holes')
    count = 0
    for assignment in solutions(m, n, limit):
        count += 1
        if value(terms, assignment, prime):
            return assignment, count
    return None, count


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.split('\n\n')[0])
    parser.add_argument('--pigeons', type=int, required=True)
    parser.add_argument('--holes', type=int, required=True)
    parser.add_argument('--prime', type=int, required=True)
    parser.add_argument('--limit', type=int, default=200000, help='solutions to check (all if fewer exist)')
    parser.add_argument('polynomial')
    args = parser.parse_args(argv)
    if args.pigeons > args.holes:
        print('No solutions: more pigeons than holes, so evaluation decides nothing here.')
        return 2
    witness, count = check(args.pigeons, args.holes, args.prime, args.polynomial, args.limit)
    if witness is not None:
        print(f'Not in any closure: nonzero mod {args.prime} at the solution '
              + ', '.join(f'{p}->{h}' for p, h in enumerate(witness)) + f' (solution {count} checked).')
        return 1
    print(f'Zero at all {count} solutions checked; no refutation (membership is not shown).')
    return 0


if __name__ == '__main__':
    sys.exit(main())
