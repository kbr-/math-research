"""dim Ann_{A_1}(l) = gamma_1 - rank(A_1 -> A_2, e -> e l) for the same uniform forms l sampled in ann4c.py (seed 0,
consecutive draws) and ann4.py (seed 3, first five draws), so that dim l*A_1 = gamma_1 can be read off.
Usage: --n N --seed S --samples K"""
import argparse, os, sys
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import a4lib as L
ap = argparse.ArgumentParser(); ap.add_argument('--n', type=int); ap.add_argument('--seed', type=int, default=0)
ap.add_argument('--samples', type=int, default=3); opt = ap.parse_args(); L.setup(opt.n)
Q1, g1 = L.quotient(1, 1); Q2, g2 = L.quotient(2, 1)
basis1 = [q['cols'][c] for q in Q1.values() for c in q['nonp']]
rng = np.random.default_rng(opt.seed); out = []
for s in range(opt.samples):
    l = rng.integers(0, 3, size=L.v); lin = {(int(u),): int(l[u]) for u in np.nonzero(l)[0]}
    rows = np.array([L.normal_form(L.mul({m: 1}, lin), Q2, g2) for m in basis1], dtype=np.uint8)
    out.append(g1 - L.gf3.rank(rows))
print(dict(n=opt.n, seed=opt.seed, gamma_1=g1, dim_Ann_A1_of_l=out))
