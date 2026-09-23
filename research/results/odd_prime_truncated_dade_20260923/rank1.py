"""Truncated Dade test on rank-one columns (the pure selector model).  X = F_3[t_1..t_m]/(t_c^2), graded, acted on by
z_i = sum_c lam[c][i] t_c (i = 1..r) with random lam[c] in F_3^r (nonzero).  X is free over u = F_3[z]/(z^3)^{(x)r} through
D iff dim (X/(z_1..z_r)X)_k = W_k = [t^k](1+t)^m/(1+t+t^2)^r for k <= D (graded Nakayama).
Single-element bound: for z in F_3bar^r, X|z = V_2^{(x) c(z)} (x) trivial with c(z) = #{c : lam_c(z) != 0}; the F_3-points of
an F_3bar-hyperplane lie in an F_3-hyperplane, so min c(z) = m - (max number of lam_c in an F_3-hyperplane); the single-element
Nakayama range is c/2 (c even) or (c+1)/2 (c odd).  Positivity: W_k >= 0.  Reports instances where measured freeness is
below min(single-element range, positivity range).  Usage: --rs --ms --trials --seed"""
import argparse, itertools, json, os, sys
import numpy as np
from math import comb
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', 'odd_prime_alignment_mechanism_20260922'))
import gf3
ap = argparse.ArgumentParser(); ap.add_argument('--rs', default='2,3,4,5'); ap.add_argument('--ms', default='6,8,10,12')
ap.add_argument('--trials', type=int, default=5); ap.add_argument('--seed', type=int, default=0); ap.add_argument('--out')
opt = ap.parse_args(); rng = np.random.default_rng(opt.seed)
def W(r, m):
    inv = [{0: 1, 1: -1, 2: 0}[i % 3] for i in range(m + 1)]; c = [1] + [0] * m
    for _ in range(r): c = [sum(c[i] * inv[k - i] for i in range(k + 1)) for k in range(m + 1)]
    X = [comb(m, k) for k in range(m + 1)]
    return [sum(X[i] * c[k - i] for i in range(k + 1)) for k in range(m + 1)]
def hyperplanes(r):
    seen = set(); out = []
    for v in itertools.product(range(3), repeat=r):
        if any(v):
            f = next(x for x in v if x); w = tuple((x * f) % 3 for x in v)   # normalize first nonzero to 1
            if w not in seen: seen.add(w); out.append(np.array(w))
    return out
res = []; bad = []
for r in map(int, opt.rs.split(',')):
    H = hyperplanes(r)
    for m in map(int, opt.ms.split(',')):
        w = W(r, m)
        for t in range(opt.trials):
            lam = np.array([rng.integers(0, 3, size=r) for _ in range(m)])
            while (lam == 0).all(axis=1).any():
                z = (lam == 0).all(axis=1); lam[z] = rng.integers(0, 3, size=(z.sum(), r))
            cmin = m - max(int(((lam @ h) % 3 == 0).sum()) for h in H)
            single = cmin // 2 if cmin % 2 == 0 else (cmin + 1) // 2
            pos = next((k - 1 for k in range(m + 1) if w[k] < 0), m)
            quot = [1]
            for k in range(1, min(m, min(single, pos) + 1) + 1):
                Bk = list(itertools.combinations(range(m), k)); idx = {b: j for j, b in enumerate(Bk)}
                Bp = list(itertools.combinations(range(m), k - 1))
                rows = np.zeros((r * len(Bp), len(Bk)), dtype=np.uint8)
                for j, S in enumerate(Bp):
                    for c in range(m):
                        if c in S: continue
                        col = idx[tuple(sorted(S + (c,)))]
                        for i in range(r): rows[i * len(Bp) + j, col] = (rows[i * len(Bp) + j, col] + lam[c][i]) % 3
                quot.append(len(Bk) - gf3.rank(rows))
            free = 0
            for k in range(len(quot)):
                if quot[k] == w[k]: free = k
                else: break
            row = dict(r=r, m=m, trial=t, lam=lam.tolist(), cmin=cmin, single=single, positive=pos, free=free, predicted=min(single, pos), quotient=quot, W=w)
            res.append(row)
            if free < min(single, pos, len(quot) - 1): bad.append(row)
            row['strict_positive_at_failure'] = bool(free + 1 < len(quot) and w[free + 1] > 0)
        print(r, m, [(x['free'], x['single'], x['positive']) for x in res if x['r'] == r and x['m'] == m], flush=True)
print('mismatches:', len(bad), 'with strictly positive W at the failing degree:', sum(1 for b in bad if b.get('strict_positive_at_failure')))
for b in bad[:10]: print(b)
if opt.out: json.dump(dict(runs=res, mismatches=bad), open(opt.out, 'w'), indent=1, default=int)
