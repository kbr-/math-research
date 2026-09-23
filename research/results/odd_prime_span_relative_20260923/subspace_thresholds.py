"""Selectors 1-L^2 over F_3, weak unary PHP^{n+1}_n, degree D=3, with linear parts drawn uniformly from the NONZERO
vectors of a random d-dimensional subspace V of cell forms (random constants).  For each (d, seed):
  exact dims in the top algebra A: dim V^2, dim A_1 V^2, dim V^3;  counts M_3 = dim(A_1V^2)/(gamma_1-1),
  M_V = dim(V^3)/(d-1), forced value = least M with M(d-1) > dim V^3;
  a LINEAR scan over M of the fall excess E(M) = (dim of the closure's degree<=2 part) - (base value) - M,
  up to the first refutation; first fall = least M with E(M) > 0;
  rank of the squares l_b^2 in A_2 at the first fall; size of the smallest linearly dependent subset of the
  linear parts among the first (first fall) forms.
Usage: --n N --dims 5,8,... --seeds S --hi H --out PATH"""
import argparse, itertools, json, os, sys
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
ap = argparse.ArgumentParser(); ap.add_argument('--n', type=int, default=6); ap.add_argument('--dims')
ap.add_argument('--seeds', type=int, default=2); ap.add_argument('--hi', type=int, default=200); ap.add_argument('--out')
opt = ap.parse_args()
sys.argv = [sys.argv[0], '--n', str(opt.n), '--samples', '0', '--out', os.devnull]
src = open(os.path.join(HERE, '..', 'odd_prime_spread_event_20260923', 'annihilators.py')).read()
exec(compile(src[:src.index("rng = np.random.default_rng(a.seed)")], 'annihilators.py', 'exec'))
sys.path.insert(0, os.path.join(HERE, '..', 'odd_prime_one_count_20260922'))
from random_conditioning_fast import QSpace, closure_of, refuted, base_rows
n = opt.n; space = QSpace(n, 3); I2 = {m: i for i, m in enumerate(M2)}
def vec2(poly):
    x = np.zeros(len(M2), dtype=np.uint8)
    for m, c in poly.items():
        if c % 3: x[I2[m]] = c % 3
    return x
rel2 = []
for i in range(P1):
    R = np.zeros(v, dtype=np.int64); R[i * n:(i + 1) * n] = 1
    for u in range(v): rel2.append(vec2(mul({(u,): 1}, R)))
P2, W2, _ = gf3.rref(np.array(rel2, dtype=np.uint8), parallel=True); r2 = P2.shape[0]
def rank_mod(rel_P, rel_W, rel_r, ncols, rows):
    Q, _ = gf3.pack(np.array(rows, dtype=np.uint8))
    return gf3.rref(None, parallel=True, packed=(np.vstack([rel_P, Q]), rel_W, ncols))[2].shape[0] - rel_r
def prod2(a, b):
    q = {}
    for u in np.nonzero(a)[0]:
        for w in np.nonzero(b)[0]:
            if u != w and hole(u) != hole(w):
                mm = tuple(sorted((int(u), int(w)))); q[mm] = (q.get(mm, 0) + int(a[u]) * int(b[w])) % 3
    return q
def rank3(rows):  # plain rank over F_3 of small integer rows
    if not rows: return 0
    return int(gf3.rank(np.array(rows, dtype=np.uint8) % 3, parallel=False))
def smallest_dependent(coefs):
    for size in range(1, len(coefs) + 1):
        for sub in itertools.combinations(range(len(coefs)), size):
            if rank3([coefs[i] for i in sub]) < size: return size
        if size >= 5: return None
    return None
def low_dim(M, cons):
    P, Wc, piv = closure_of(space, base_rows(n) + cons[:M]); piv = np.asarray(piv)
    return int((space.deg[piv] < 3).sum()), refuted(space, P, Wc)
base_low = low_dim(0, [])[0]
res = {'n': n, 'gamma_1': g1, 'base_low': base_low, 'runs': []}
for d in [int(x) for x in opt.dims.split(',')]:
    for s in range(opt.seeds):
        rng = np.random.default_rng(1000 * d + s)
        B = rng.integers(0, 3, size=(d, v))
        prods = [prod2(B[i], B[j]) for i in range(d) for j in range(i, d)]
        dimV2 = rank_mod(P2, W2, r2, len(M2), [vec2(q) for q in prods])
        dimA1V2 = rank_mod(Prel, W, rel_rank, len(M3), [vec3(mul(q, e)) for q in prods for e in basisA1])
        dimV3 = rank_mod(Prel, W, rel_rank, len(M3), [vec3(mul(q, np.asarray(B[i], dtype=np.int64))) for q in prods for i in range(d)])
        M3p = dimA1V2 / (g1 - 1); MVp = dimV3 / (d - 1); forced = dimV3 // (d - 1) + 1
        cons, coefs, lins = [], [], []
        while len(cons) < opt.hi:
            coef = rng.integers(0, 3, size=d)
            lin = (coef @ B) % 3
            if not lin.any(): continue            # nonzero linear parts only
            L = {(u,): int(lin[u]) for u in range(v) if lin[u]}; c0 = int(rng.integers(0, 3))
            if c0: L[()] = c0
            sq = {}
            for m1, a1 in L.items():
                for m2, a2 in L.items():
                    mm = tuple(sorted(set(m1 + m2))); sq[mm] = (sq.get(mm, 0) + a1 * a2) % 3
            p = {(): 1}
            for mm, c in sq.items(): p[mm] = (p.get(mm, 0) - c) % 3
            cons.append({m: c for m, c in p.items() if c}); coefs.append(list(coef)); lins.append(lin)
        excess, first_fall, least_ref = [], None, None
        for M in range(1, opt.hi + 1):
            lo_, ref = low_dim(M, cons); e = lo_ - base_low - M; excess.append(e)
            if first_fall is None and e > 0: first_fall = M
            if ref: least_ref = M; break
        sq_rank = rank_mod(P2, W2, r2, len(M2), [vec2(prod2(lins[b], lins[b])) for b in range(first_fall or 0)]) if first_fall else None
        o = {'d': d, 'seed': s, 'dimV2': dimV2, 'dimA1V2': dimA1V2, 'dimV3': dimV3, 'M_3': round(M3p, 2), 'M_V': round(MVp, 2),
             'forced_V': forced, 'first_fall': first_fall, 'least_refuted': least_ref,
             'squares_rank_at_fall': sq_rank, 'smallest_dependent_before_fall': smallest_dependent(coefs[:first_fall]) if first_fall else None,
             'excess': excess}
        res['runs'].append(o); print({k: o[k] for k in o if k != 'excess'}, flush=True)
json.dump(res, open(opt.out, 'w'), indent=1, default=int)
