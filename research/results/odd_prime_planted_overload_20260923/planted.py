"""Planted overload on a two-dimensional span, weak unary PHP^{n+1}_n over F_3, degree D=3.
a, b: random cell forms; target v in F_3^2; planted: for each of the 4 directions (alpha,beta) and each value
c != alpha v1 + beta v2, the selector 1-(alpha a + beta b - c)^2 (so every value pair except v is forbidden; 8 selectors).
Measures: (i) whether the degree-3 closure of base+planted contains a - v1 and b - v2;
(ii) least refuted M of uniform selectors added after the planted ones; (iii) the same after imposing a = v1, b = v2
directly (no planted selectors); (iv) prediction ceil(g3/(g1-1)) from the conditioned base's graded quotient dims.
Usage: --n N --seeds S --hi H --out PATH"""
import argparse, json, os, sys
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', 'odd_prime_one_count_20260922'))
sys.path.insert(0, os.path.join(HERE, '..', 'odd_prime_alignment_mechanism_20260922'))
import gf3
from random_conditioning_fast import QSpace, closure_of, refuted, base_rows
ap = argparse.ArgumentParser(); ap.add_argument('--n', type=int, default=6); ap.add_argument('--seeds', type=int, default=2)
ap.add_argument('--hi', type=int, default=120); ap.add_argument('--out'); opt = ap.parse_args()
n = opt.n; v = n * (n + 1)
def lin_poly(coef, c0):
    L = {(u,): int(coef[u]) % 3 for u in range(v) if coef[u] % 3}
    if c0 % 3: L[()] = c0 % 3
    return L
def selector(L):
    sq = {}
    for m1, a1 in L.items():
        for m2, a2 in L.items():
            mm = tuple(sorted(set(m1 + m2))); sq[mm] = (sq.get(mm, 0) + a1 * a2) % 3
    p = {(): 1}
    for mm, c in sq.items(): p[mm] = (p.get(mm, 0) - c) % 3
    return {m: c for m, c in p.items() if c}
def contains(space, P, W, poly):
    Q, _ = gf3.pack(space.vec(poly)[None, :])
    return gf3.rref(None, parallel=True, packed=(np.vstack([P, Q]), W, space.cols))[2].shape[0] == P.shape[0]
def least_refuted(space, prefix, cons, hi):
    def test(M):
        P, W, _ = closure_of(space, base_rows(n) + prefix + cons[:M]); return refuted(space, P, W)
    if test(0): return 0
    if not test(hi): return None
    lo = 0
    while hi - lo > 1:
        mid = (lo + hi) // 2
        if test(mid): hi = mid
        else: lo = mid
    return hi
res = {'n': n, 'runs': []}
S3 = QSpace(n, 3)
for s in range(opt.seeds):
    rng = np.random.default_rng(500 + s)
    a = rng.integers(0, 3, size=v); b = rng.integers(0, 3, size=v); vt = rng.integers(0, 3, size=2)
    planted = []
    for (al, be) in [(1, 0), (0, 1), (1, 1), (1, 2)]:
        val = (al * vt[0] + be * vt[1]) % 3
        for c in range(3):
            if c != val: planted.append(selector(lin_poly(al * a + be * b, -c)))
    eqs = [lin_poly(a, -int(vt[0])), lin_poly(b, -int(vt[1]))]
    P, W, _ = closure_of(S3, base_rows(n) + planted)
    derived = [bool(contains(S3, P, W, e)) for e in eqs]
    uni = []
    while len(uni) < opt.hi:
        coef = rng.integers(0, 3, size=v)
        if coef.any(): uni.append(selector(lin_poly(coef, int(rng.integers(0, 3)))))
    thr_planted = least_refuted(S3, planted, uni, opt.hi)
    thr_cond = least_refuted(S3, eqs, uni, opt.hi)
    d = {}
    for j in (1, 2, 3):
        Sj = QSpace(n, j); Pj, Wj, _ = closure_of(Sj, base_rows(n) + eqs); d[j] = Sj.cols - Pj.shape[0]
    g = {1: d[1] - 1, 2: d[2] - d[1], 3: d[3] - d[2]}
    pred = int(np.ceil(g[3] / (g[1] - 1)))
    o = {'seed': s, 'target': [int(x) for x in vt], 'planted_derive_a_b': derived, 'least_refuted_after_planted': thr_planted,
         'least_refuted_conditioned': thr_cond, 'conditioned_dims': d, 'conditioned_graded': g, 'predicted': pred}
    res['runs'].append(o); print(o, flush=True)
json.dump(res, open(opt.out, 'w'), indent=1, default=int)
