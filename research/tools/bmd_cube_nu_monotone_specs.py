"""Monotone degree vectors for the review tests of conj:cube-monotone-squarefree (bmd-r109).

Usage: bmd_cube_nu_monotone_specs.py n MAX COUNT SEED
  n = 2: every monotone vector with entries in -1..MAX and N >= 2 (COUNT, SEED ignored).
  n >= 3: COUNT random monotone vectors with entries in -1..MAX (seeded), built by taking
  nu_r = min over the one-step-lower sets of nu plus a random nonpositive step.
Prints the vectors joined by '/', each as 2^n comma-separated entries indexed by r = sum r_i 2^i.
"""
import itertools
import random
import sys

n, mx, count, seed = int(sys.argv[1]), int(sys.argv[2]), int(sys.argv[3]), int(sys.argv[4])


def monotone(nu):
    return all(nu[r] >= nu[r | (1 << i)] for r in range(1 << n) for i in range(n) if not r >> i & 1)


out = []
if n == 2:
    for nu in itertools.product(range(-1, mx + 1), repeat=4):
        if monotone(nu) and sum(x + 1 for x in nu) >= 2:
            out.append(nu)
else:
    rng = random.Random(seed)
    seen = set()
    while len(out) < count:
        nu = [0] * (1 << n)
        for r in sorted(range(1 << n), key=lambda s: bin(s).count('1')):
            lower = [nu[r ^ (1 << i)] for i in range(n) if r >> i & 1]
            top = min(lower) if lower else mx
            nu[r] = max(-1, top - rng.randint(0, 2)) if lower else rng.randint(1, mx)
        t = tuple(nu)
        if monotone(t) and t not in seen and sum(x + 1 for x in t) >= 2:
            seen.add(t)
            out.append(t)
print('/'.join(','.join(map(str, v)) for v in out))
