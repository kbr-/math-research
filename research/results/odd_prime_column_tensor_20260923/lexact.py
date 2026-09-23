"""Exactness of multiplication by a linear form l on the weak unary PHP top algebra A over F_3 (component-wise normal
forms from a4lib.py).  Computes r_k = rank(l: A_k -> A_{k+1}) and s_k = rank(l^2: A_k -> A_{k+2}) and reports
S1(k): dim Ann_{A_k}(l) = gamma_k - r_k  versus  dim l^2 A_{k-2} = s_{k-2},
S2(k): dim Ann_{A_k}(l^2) = gamma_k - s_k  versus  dim l A_{k-1} = r_{k-1},
and the Hilbert function of A/lA against HS_A/(1+t+t^2).  Usage: --n N --top K --samples S --seed SEED"""
import argparse, json, os, sys
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', 'odd_prime_degree_four_20260923'))
import a4lib as L
ap = argparse.ArgumentParser(); ap.add_argument('--n', type=int); ap.add_argument('--top', type=int, default=4)
ap.add_argument('--samples', type=int, default=1); ap.add_argument('--seed', type=int, default=0)
ap.add_argument('--workers', type=int, default=2); ap.add_argument('--out'); opt = ap.parse_args(); L.setup(opt.n)
Q = {}; g = {}
for k in range(opt.top + 1): Q[k], g[k] = L.quotient(k, opt.workers) if k else ({(): dict(I={(): 0}, cols=[()], piv=np.zeros(0, dtype=np.int32), nonp=np.array([0]), E=np.zeros((0, 1), dtype=np.int32), off=0)}, 1)
basis = {k: [q['cols'][c] for q in Q[k].values() for c in q['nonp']] for k in Q}
def rank_of(k, poly, deg):
    """rank of multiplication by the homogeneous poly (degree deg) from A_k to A_{k+deg}, chunked packing."""
    tgt = k + deg; W = (g[tgt] + 63) // 64; packs = []
    for c0 in range(0, len(basis[k]), 2000):
        ch = basis[k][c0:c0 + 2000]; rows = np.zeros((len(ch), g[tgt]), dtype=np.uint8)
        for t, m in enumerate(ch): rows[t] = L.normal_form(L.mul({m: 1}, poly), Q[tgt], g[tgt])
        packs.append(L.gf3.pack(rows)[0])
    P = np.vstack(packs); return L.gf3.rref(None, parallel=True, packed=(P, W, g[tgt]))[2].shape[0]
rng = np.random.default_rng(opt.seed); res = dict(n=opt.n, gamma=[g[k] for k in range(opt.top + 1)], samples=[])
w = []  # coefficients of HS_A/(1+t+t^2): 1/(1+t+t^2) = 1 - t + t^3 - t^4 + t^6 - ...
inv = [ {0: 1, 1: -1, 2: 0}[i % 3] for i in range(opt.top + 1)]
for k in range(opt.top + 1): w.append(sum(g[k - i] * inv[i] for i in range(k + 1)))
for s in range(opt.samples):
    l = rng.integers(0, 3, size=L.v); lin = {(int(u),): int(l[u]) for u in np.nonzero(l)[0]}
    sq = L.square(l)
    r = [rank_of(k, lin, 1) for k in range(opt.top)]
    sr = [rank_of(k, sq, 2) for k in range(opt.top - 1)]
    S1 = {k: (g[k] - r[k], sr[k - 2] if k >= 2 else 0) for k in range(opt.top)}
    S2 = {k: (g[k] - sr[k], r[k - 1] if k >= 1 else 0) for k in range(opt.top - 1)}
    quot = [g[0]] + [g[k] - r[k - 1] for k in range(1, opt.top + 1)]
    res['samples'].append(dict(r=r, s=sr, S1_ann_vs_expected=S1, S2_ann_vs_expected=S2, HS_A_mod_l=quot, HS_A_over_1tt2=w))
    print(res['samples'][-1], flush=True)
if opt.out: json.dump(res, open(opt.out, 'w'), indent=1, default=int)
