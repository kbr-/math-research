"""Near-occupancy pairs: start from the column-type pair of n8_K3_column_robust.json (trial 0; its hole values are the affine
plane AG(2,3) minus a point) and set the row functions of both forms to zero on s randomly chosen rows (partial occupancy on a sub-board).
For each perturbed pair: robustness (Q, t as in board_affine), Hilbert function of A/(l_1, l_2) through degree 3 against
HS_A/(1+t+t^2)^2, written in board_affine's run format so pencil_closure.py can compute the closure locus.
Usage: --ss 1,2,3,5,9 --trials 3 --seed --out"""
import json, os, sys
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); a = dict(zip(sys.argv[1::2], sys.argv[2::2]))
ss = [int(x) for x in a['--ss'].split(',')]; trials = int(a['--trials']); seed = int(a['--seed']); outp = a['--out']
sys.argv = [sys.argv[0], '--n', '8', '--K', '3', '--rs', '', '--family', 'random', '--seed', str(seed)]
exec(open(os.path.join(HERE, 'board_affine.py')).read().split("res = []\nif opt.phis:")[0])
base = [np.array(f) for f in json.load(open(os.path.join(HERE, 'n8_K3_column_robust.json')))['runs'][0]['forms']]
W, T = W_trunc(2, 3); res = []
for s in ss:
    for tr in range(trials):
        rows = rng.choice(P1, size=s, replace=False); F = [f.copy() for f in base]
        for f in F: f[rows] = 0
        H = hilbert(F); ex = [h - x for h, x in zip(H, T)]
        res.append(dict(r=2, s=s, trial=f's{s}-{tr}', rows=sorted(rows.tolist()), robust=robust_system(F), H=H, T=T, excess=ex, forms=[f.tolist() for f in F]))
        print(s, tr, sorted(rows.tolist()), res[-1]['robust'], H, ex, flush=True)
json.dump(dict(n=n, K=3, base='n8_K3_column_robust.json trial 0', runs=res), open(outp, 'w'), indent=1, default=int)
