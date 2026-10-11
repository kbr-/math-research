#!/usr/bin/env python3
"""Level counts of the pigeonhole principle's closure, by the pigeon dance, against two bounds.

Statement tested: for m pigeons and n holes, with N_j the number of partial one-to-one maps a from j pigeons to
the holes 1..n on which a pigeon dance exists (the pigeons, in increasing order, each move to a free hole
above their own), one has N_j >= binom(m, j) (n-j)(n-j-1)...(n-2j+1) for j <= n/2, the maps into the first
n - j holes all having a dance.  By the basis theorem of Impagliazzo, Pudlak and Sgall (Proposition 3.8) N_j
is the j-th level of the closure of the pigeonhole principle at any degree D with j <= D <= ceil(n/2).

Expected before the run: the inequality holds in every case (it is proved); N_j is strictly above the bound
once j >= 2, the bound counting only maps into the first n - j holes; and N_j exceeds binom(n, j) 3^j, an upper
bound for binom(X, j) with X <= 3n/2, wherever n - 2j + 1 >= 4.  A failure of the inequality would mean the
dance is implemented wrongly or the argument is false.  The dance is the minimal one of the source's
Definition 3.3; the count is by enumeration of all injective maps, so small sizes only.
"""
import argparse
import itertools
import math


def has_dance(pigeons, holes, n):
    """The minimal dance: each pigeon in turn moves to the smallest free hole above its own."""
    place = dict(zip(pigeons, holes))
    for p in pigeons:                       # pigeons in increasing order
        used = set(place.values())
        target = next((h for h in range(place[p] + 1, n + 1) if h not in used), None)
        if target is None:
            return False
        place[p] = target
    return True


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--max-n", type=int, default=7)
    args = ap.parse_args()
    with open(args.out, "w") as fh:
        for n in range(2, args.max_n + 1):
            m = n + 1
            for j in range(1, n // 2 + 1):
                per_set = sum(has_dance(tuple(range(1, j + 1)), holes, n)
                              for holes in itertools.permutations(range(1, n + 1), j))
                # the dance depends on the order of the pigeons only, so every j-set of pigeons gives the same count
                level = math.comb(m, j) * per_set
                lower = math.comb(m, j) * math.perm(n - j, j)
                assert level >= lower, (n, j)
                thin_cap = math.comb(n, j) * 3 ** j
                fh.write(f"n={n} m={m} j={j} N_j={level} lower_bound={lower} binom(n,j)*3^j={thin_cap} "
                         f"n-2j+1={n - 2 * j + 1} N_j_exceeds_cap={level > thin_cap}\n")
    print("done")


if __name__ == "__main__":
    main()
