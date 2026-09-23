"""Minimal perturbations of the occupancy pair (n8_K3_column_robust.json trial 0): add +1 or +2 to one coefficient x_ij of one
of the two forms (6 random choices), then the Hilbert function of A/(l_1, l_2) through degree 3.  Usage: --seed --out"""
import json, os, sys
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); a = dict(zip(sys.argv[1::2], sys.argv[2::2]))
sys.argv = [sys.argv[0], '--n', '8', '--K', '3', '--rs', '', '--family', 'random', '--seed', a['--seed']]
exec(open(os.path.join(HERE, 'board_affine.py')).read().split("res = []\nif opt.phis:")[0])
base = [np.array(f) for f in json.load(open(os.path.join(HERE, 'n8_K3_column_robust.json')))['runs'][0]['forms']]
W, T = W_trunc(2, 3); res = []
for tr in range(6):
    b, i, j, e = int(rng.integers(2)), int(rng.integers(P1)), int(rng.integers(n)), int(rng.integers(1, 3))
    F = [f.copy() for f in base]; F[b][i, j] = (F[b][i, j] + e) % 3
    H = hilbert(F); res.append(dict(form=b, row=i, hole=j, add=e, H=H, T=T, excess=[h - x for h, x in zip(H, T)])); print(res[-1], flush=True)
json.dump(dict(runs=res), open(a['--out'], 'w'), indent=1, default=int)
