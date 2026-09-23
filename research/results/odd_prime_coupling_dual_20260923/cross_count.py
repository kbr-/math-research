"""Count for the cross-form idea: a cross form l = sum_c alpha_c x_{i,c} + sum_{x != i} beta_x x_{x,a} restricts to a
column form on the board without row i, whose square vanishes, so it adds nothing to the row Horace trace.
Tested quantity: rank of w -> D_l^2 w on K_3 for single cross forms (random nonzero alpha, beta), against gamma_1 - 1,
the number a generic form imposes; and the prefix ranks of M cross forms (random a) against min(gamma_3 - gamma'_3, ...).
Usage: python3 cross_count.py --ns 6,7 --out OUT.json"""
import argparse, json, os, sys
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', 'odd_prime_horace_pieces_20260923'))
from horace_pieces import Board, series
ap = argparse.ArgumentParser(); ap.add_argument('--ns', default='6,7'); ap.add_argument('--out', required=True); a = ap.parse_args()
res = []; rng = np.random.default_rng(5)
for n in map(int, a.ns.split(',')):
    R, N = n + 1, n; b = Board(R, N); i = R - 1; g3 = b.Kb.shape[1]; g1 = R * (N - 1); allc = np.arange(g3)
    contains = np.array([i in S for S in b.sets[3]]); kR = int(contains[b.block_of_col].sum())
    forms = []
    for k in range(60):
        f = np.zeros((R, N), dtype=np.int64); lab = int(rng.integers(0, N))
        f[i, :] = rng.integers(1, 3, size=N); f[i, 0] = 0                 # nonconstant on row i
        f[:i, lab] = rng.integers(1, 3, size=R - 1); forms.append(f)
    blocks = [b.D2K(f, allc) for f in forms]
    single = [series([bl], g3)[0] for bl in blocks[:5]]
    pref = series(blocks, g3)
    res.append(dict(n=n, gamma1_minus_1=g1 - 1, gamma3=g3, residual_dim=kR, single_ranks=single, prefix=pref))
    print(f'n={n}: gamma1-1={g1-1}, single cross ranks {single}; prefix ranks {pref[:12]} ... {pref[-1]} (residual dim {kR})', flush=True)
json.dump(res, open(a.out, 'w'), indent=1)
