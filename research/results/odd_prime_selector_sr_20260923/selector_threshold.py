"""Least M at which weak unary PHP^{n+1}_n over F_3 plus M random selector constraints 1 - L^2 = 0
(L a uniformly random affine form in the cells, i.e. L != 0) is refuted at PC degree D (exact, collision
quotient, recorded fast closure).  Bisection over M in [lo, hi] on a fixed per-seed sequence of constraints.
Conjecture SR's graded count, with the Frobenius syzygy L(1-L^2)=0 per constraint, predicts the first degree fall
at M = gamma_3/(gamma_1-1) for D = 3 (gamma_j graded quotient dimensions of the base; no Koszul term below degree 4).  Usage: --n N --D D --seeds S --lo LO --hi HI --out PATH [--probe M]"""
import argparse, json, os, sys, time
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', 'odd_prime_one_count_20260922'))
from random_conditioning_fast import QSpace, closure_of, refuted, base_rows
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
ap = argparse.ArgumentParser()
for k in ('n', 'D', 'seeds', 'lo', 'hi', 'probe'): ap.add_argument('--' + k, type=int, default=None)
ap.add_argument('--out'); a = ap.parse_args()
space = QSpace(a.n, a.D); v = a.n * (a.n + 1)
res = {'n': a.n, 'D': a.D, 'columns': space.cols, 'seeds': []}
for s in range(a.seeds):
    seed = 9000 + 10 * a.n + s; rng = np.random.default_rng(seed)
    cons = [selector(rng, v) for _ in range(a.hi)]
    def test(M):
        t = time.time(); P, W, piv = closure_of(space, base_rows(a.n) + cons[:M]); r = refuted(space, P, W)
        print(f'  seed {seed} M={M} refuted={r} rank={P.shape[0]} {time.time() - t:.0f}s', flush=True); return r
    if a.probe is not None:
        test(a.probe); continue
    lo, hi = a.lo, a.hi            # invariant: not refuted at lo, refuted at hi (checked)
    assert not test(lo) and test(hi)
    while hi - lo > 1:
        mid = (lo + hi) // 2
        if test(mid): hi = mid
        else: lo = mid
    res['seeds'].append({'seed': seed, 'least_refuted_M': hi})
    print(f'seed {seed}: least refuted M = {hi}', flush=True)
if a.out and a.probe is None: json.dump(res, open(a.out, 'w'), indent=1)
