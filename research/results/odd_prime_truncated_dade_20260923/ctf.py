"""Freeness of the complete-column tensor X = L^{(x)m} over u(g) = F_3[z_1..z_r]/(z_i^3), where L = F_3 + g (square-zero,
z_i: 1 -> e_i) and each z_i acts diagonally (sum over columns).  X_k has basis (S, a): S a k-subset of the m columns,
a in [r]^S.  By graded Nakayama, X is free through D iff dim (X/gX)_k = W_k := [t^k] (1+rt)^m/(1+t+t^2)^r for k <= D.
Single-element bound: every nonzero z hits all m columns; each column restricts to V_2 + (r-1) trivial[1], so X restricted to
F[z]/(z^3) is a sum of V_2^{(x)c'}[m-c'] (x) trivial, c' <= m, free exactly through m/2 (m even) or (m+1)/2 (m odd).  Reports, per (r, m): measured freeness degree, positivity degree of W and the
single-element bound.  Usage: --rs 1,2,3 --ms 2,...,9 --maxcols N"""
import argparse, itertools, json, os, sys
import numpy as np
from math import comb
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', 'odd_prime_alignment_mechanism_20260922'))
import gf3
ap = argparse.ArgumentParser(); ap.add_argument('--rs', default='1,2,3,4'); ap.add_argument('--ms', default='2,3,4,5,6,7,8')
ap.add_argument('--maxcols', type=int, default=60000); ap.add_argument('--out'); opt = ap.parse_args()
def W(r, m, K):
    inv = [{0: 1, 1: -1, 2: 0}[i % 3] for i in range(K + 1)]; c = [1] + [0] * K
    for _ in range(r): c = [sum(c[i] * inv[k - i] for i in range(k + 1)) for k in range(K + 1)]
    X = [comb(m, k) * r ** k for k in range(K + 1)]
    return [sum(X[i] * c[k - i] for i in range(k + 1)) for k in range(K + 1)]
def basis(r, m, k):
    return [(S, a) for S in itertools.combinations(range(m), k) for a in itertools.product(range(r), repeat=k)]
res = []
for r in map(int, opt.rs.split(',')):
    for m in map(int, opt.ms.split(',')):
        K = m; w = W(r, m, K); quot = [1]; free_through = 0; stopped = None
        for k in range(1, K + 1):
            Bk = basis(r, m, k)
            if len(Bk) > opt.maxcols: stopped = k; break
            idx = {b: t for t, b in enumerate(Bk)}; Bp = basis(r, m, k - 1)
            rows = np.zeros((r * len(Bp), len(Bk)), dtype=np.uint8)
            for t, (S, a) in enumerate(Bp):
                d = dict(zip(S, a))
                for i in range(r):
                    for c in range(m):
                        if c in d: continue
                        d2 = dict(d); d2[c] = i; S2 = tuple(sorted(d2)); rows[i * len(Bp) + t, idx[(S2, tuple(d2[s] for s in S2))]] = 1
            quot.append(len(Bk) - gf3.rank(rows, parallel=True))
        for k in range(len(quot)):
            if quot[k] == w[k]: free_through = k
            else: break
        pos = next((k - 1 for k in range(K + 1) if w[k] < 0), K)
        single = m // 2 if m % 2 == 0 else (m + 1) // 2
        row = dict(r=r, m=m, quotient=quot, W=w[:len(quot)], free_through=free_through, computed_through=len(quot) - 1,
                   positive_through=pos, single_element_free_through=single, predicted=min(pos, single))
        res.append(row); print(row, flush=True)
if opt.out: json.dump(res, open(opt.out, 'w'), indent=1)
