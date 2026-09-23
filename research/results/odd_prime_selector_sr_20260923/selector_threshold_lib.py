"""Selector constraint 1 - L^2 (L uniform random affine form in the cells), shared by the drivers."""
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'odd_prime_one_count_20260922'))
from random_conditioning import random_eq
def selector(rng, v):
    L = random_eq(rng, v)
    sq = {}
    for m1, a1 in L.items():
        for m2, a2 in L.items():
            mon = tuple(sorted(set(m1 + m2)))
            sq[mon] = (sq.get(mon, 0) + a1 * a2) % 3
    p = {(): 1}
    for mon, c in sq.items(): p[mon] = (p.get(mon, 0) - c) % 3
    return {m: c for m, c in p.items() if c}
