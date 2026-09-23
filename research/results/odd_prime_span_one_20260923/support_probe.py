"""dim Ann_{A_1}(sum_{b in S} c_b l_b^2) in the top algebra A of weak unary PHP over F_3, for uniform l_b and
random nonzero c_b, by support size s = |S|.  Reuses the algebra construction of annihilators.py.
Usage: --n N --sizes 2,3,... --samples K --out PATH"""
import argparse, json, os, sys
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
ap = argparse.ArgumentParser(); ap.add_argument('--n', type=int, default=6); ap.add_argument('--sizes')
ap.add_argument('--samples', type=int, default=20); ap.add_argument('--out'); opt = ap.parse_args()
sys.argv = [sys.argv[0], '--n', str(opt.n), '--samples', '0', '--out', os.devnull]
src = open(os.path.join(HERE, '..', 'odd_prime_spread_event_20260923', 'annihilators.py')).read()
src = src[:src.index("rng = np.random.default_rng(a.seed)")]   # algebra construction only
exec(compile(src, 'annihilators.py', 'exec'))
rng = np.random.default_rng(7)
res = {'n': opt.n, 'by_size': {}}
for s in [int(x) for x in opt.sizes.split(',')]:
    dims = []
    for _ in range(opt.samples):
        q = {}
        for _b in range(s):
            l = rng.integers(0, 3, size=v); c = int(rng.integers(1, 3))
            for m, x in square(l).items(): q[m] = (q.get(m, 0) + c * x) % 3
        dims.append(ann_dim(q))
    res['by_size'][s] = dims; print(s, dict(zip(*np.unique(dims, return_counts=True))), flush=True)
json.dump(res, open(opt.out, 'w'), indent=1, default=int)
