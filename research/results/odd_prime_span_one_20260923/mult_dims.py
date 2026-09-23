"""dim(e A_2) in the top algebra A of weak unary PHP over F_3 (n holes): for single variables, random e, and e on few
pigeons.  e A_2 is the span of e*m over a basis of degree-2 monomials, modulo the degree-3 relations.
Usage: --n N --samples K --out PATH"""
import argparse, json, os, sys
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
ap = argparse.ArgumentParser(); ap.add_argument('--n', type=int, default=6); ap.add_argument('--samples', type=int, default=10)
ap.add_argument('--out'); opt = ap.parse_args()
sys.argv = [sys.argv[0], '--n', str(opt.n), '--samples', '0', '--out', os.devnull]
src = open(os.path.join(HERE, '..', 'odd_prime_spread_event_20260923', 'annihilators.py')).read()
exec(compile(src[:src.index("rng = np.random.default_rng(a.seed)")], 'annihilators.py', 'exec'))
def mult_dim(e):
    imgs = np.array([vec3(mul({m: 1}, e)) for m in M2], dtype=np.uint8)
    Q, _ = gf3.pack(imgs)
    return gf3.rref(None, parallel=True, packed=(np.vstack([Prel, Q]), W, len(M3)))[2].shape[0] - rel_rank
rng = np.random.default_rng(11); res = {'n': opt.n, 'gamma_1': g1, 'gamma_3': len(M3) - rel_rank}
x = np.zeros(v, dtype=np.int64); x[0] = 1; res['variable'] = mult_dim(x)
res['random'] = [mult_dim(rng.integers(0, 3, size=v)) for _ in range(opt.samples)]
res['one_pigeon'] = []
for _ in range(opt.samples):
    e = np.zeros(v, dtype=np.int64); e[0:n] = rng.integers(0, 3, size=n); res['one_pigeon'].append(mult_dim(e))
col = np.zeros(v, dtype=np.int64); col[[i * n for i in range(P1)]] = 1; res['column'] = mult_dim(col)
print(res, flush=True); json.dump(res, open(opt.out, 'w'), indent=1, default=int)
