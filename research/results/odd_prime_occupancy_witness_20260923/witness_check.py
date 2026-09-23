"""Numerical check of the explicit non-freeness witnesses for column-type forms l_phi = sum_j phi(j) C_j on the weak unary
PHP top algebra A over F_3 (component normal forms from a4lib.py).  Case S1 (c even): w of degree k = c/2 with l w = 0 and
w not in l^2 A_{k-2}.  Case S2 (c odd): w of degree k = (c-1)/2 with l^2 w = 0 and w not in l A_{k-1}.
w = product over pairs (p,q) of (mu_p C_p - mu_q C_q), mu_j = phi(j) - a (a the most frequent value); pairs inside the value
classes, plus the mixed pair (r1,r2) with factor C_r1 + C_r2 when both classes are odd.  Usage: --n --cases"""
import argparse, itertools, json, os, sys, collections
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', 'odd_prime_degree_four_20260923'))
import a4lib as L
ap = argparse.ArgumentParser(); ap.add_argument('--n', type=int, default=8); ap.add_argument('--cases'); ap.add_argument('--out'); opt = ap.parse_args()
n = opt.n; L.setup(n); P1 = n + 1
def col(j, coef=1): return {(i * n + j,): coef % 3 for i in range(P1)}
def add(p, q, s=1):
    out = dict(p)
    for m, c in q.items(): out[m] = (out.get(m, 0) + s * c) % 3
    return {m: c for m, c in out.items() if c}
def polymul(p, q):
    if () in p and len(p) == 1: return {m: (c * p[()]) % 3 for m, c in q.items()}
    return L.mul(p, q) if p and q else {}
Q = {}; g = {}
def quot(k):
    if k not in Q: Q[k], g[k] = L.quotient(k, 2)
    return Q[k], g[k]
def nf(p, k): q, gk = quot(k); return L.normal_form(p, q, gk) % 3
def rank(rows): return L.gf3.rank(np.array(rows, dtype=np.uint8)) if len(rows) else 0
res = []
for s in opt.cases.split(';'):
    phi = [int(x) for x in s.split(',')]; cnt = collections.Counter(phi); a = max(cnt, key=lambda v: (cnt[v], -v))
    mu = [(x - a) % 3 for x in phi]; S1 = [j for j in range(n) if mu[j] == 1]; S2 = [j for j in range(n) if mu[j] == 2]; c = len(S1) + len(S2)
    ell = {}
    for j in range(n): ell = add(ell, col(j, phi[j]))
    factors = []; left = []
    for cls in (S1, S2):
        for t in range(0, len(cls) - 1, 2): p_, q_ = cls[t], cls[t + 1]; factors.append(add(col(p_, mu[p_]), col(q_, mu[q_]), -1))
        if len(cls) % 2: left.append(cls[-1])
    mixed = False
    if len(left) == 2: factors.append(add(col(left[0]), col(left[1]))); mixed = True; left = []
    w = {(): 1}
    for f in factors: w = polymul(w, f) if w != {(): 1} else f
    k = len(factors); case = 'S1' if not left else 'S2'
    if case == 'S1':
        killed = not nf(polymul(ell, w), k + 1).any() if k + 1 >= 1 else True
        target = nf(w, k); span = []
        if k >= 2:
            sq = L.square(np.array([phi[j % n] for j in range(P1 * n)]))
            for m in ([()] if k == 2 else None) or []: span.append(nf(sq, 2))
            if k > 2:
                q, _ = quot(k - 2); basis = [q_['cols'][cc] for q_ in q.values() for cc in q_['nonp']]
                span = [nf(L.mul({m: 1}, sq), k) for m in basis]
        outside = rank(span + [target]) > rank(span)
    else:
        sq = L.square(np.array([phi[j % n] for j in range(P1 * n)]))
        killed = not nf(polymul(sq, w), k + 2).any()
        target = nf(w, k) if k else None
        if k == 0: outside = True
        else:
            if k == 1: span = [nf(ell, 1)]
            else:
                q, _ = quot(k - 1); basis = [q_['cols'][cc] for q_ in q.values() for cc in q_['nonp']]
                span = [nf(L.mul({m: 1}, ell), k) for m in basis]
            outside = rank(span + [target]) > rank(span)
    row = dict(n=n, phi=phi, a=a, c=c, witness_degree=k, case=case, mixed_pair=mixed, killed=bool(killed), not_in_image=bool(outside),
               predicted_first_failure=(k + 1 if case == 'S1' else k + 2))
    res.append(row); print(row, flush=True)
if opt.out: json.dump(res, open(opt.out, 'w'), indent=1)
