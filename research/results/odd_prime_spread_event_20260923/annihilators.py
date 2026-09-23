"""Annihilators in the graded algebra A = F_3[x_ij]/(x_ij^2, x_ij x_i'j, row forms sum_j x_ij), weak unary PHP
top-degree algebra, n holes, n+1 pigeons.  For q in A_2 computes dim Ann_{A_1}(q) = 35-ish minus rank of a -> a q
into A_3 (exact, GF(3) bit-sliced elimination).  Probes: random l (dim Ann(l^2)), l supported on k pigeons,
column forms, and sums of two squares l1^2 + c l2^2.  Usage: --n N --samples S --out PATH"""
import argparse, itertools, json, os, sys, time
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', 'odd_prime_alignment_mechanism_20260922'))
import gf3
ap = argparse.ArgumentParser(); ap.add_argument('--n', type=int, default=6); ap.add_argument('--samples', type=int, default=100)
ap.add_argument('--seed', type=int, default=1); ap.add_argument('--out'); a = ap.parse_args()
n = a.n; P1 = n + 1; v = P1 * n; hole = lambda u: u % n; pig = lambda u: u // n
def mons(k): return [c for c in itertools.combinations(range(v), k) if len({hole(u) for u in c}) == k]
M3 = mons(3); I3 = {m: i for i, m in enumerate(M3)}; M2 = mons(2)
def mul(poly, lin):  # poly: dict mon(k)->coef, lin: vector over cells; returns dict mon(k+1)
    out = {}
    for m, c in poly.items():
        hs = {hole(u) for u in m}
        for u in range(v):
            if lin[u] and u not in m and hole(u) not in hs:
                mm = tuple(sorted(m + (u,))); out[mm] = (out.get(mm, 0) + c * lin[u]) % 3
    return out
def vec3(poly):
    x = np.zeros(len(M3), dtype=np.uint8)
    for m, c in poly.items():
        if c % 3: x[I3[m]] = c % 3
    return x
rows = []
for i in range(P1):
    R = np.zeros(v, dtype=np.int64); R[i * n:(i + 1) * n] = 1
    for m in M2: rows.append(vec3(mul({m: 1}, R)))
Rel = np.array(rows, dtype=np.uint8); Prel, W, piv = gf3.rref(Rel, parallel=True); rel_rank = Prel.shape[0]
basisA1 = []
for i in range(P1):
    for j in range(n - 1):
        e = np.zeros(v, dtype=np.int64); e[i * n + j] = 1; basisA1.append(e)
g1 = len(basisA1)
print(f'n={n}: degree-3 monomials {len(M3)}, relation rank {rel_rank}, gamma_3 = {len(M3) - rel_rank}, gamma_1 = {g1}', flush=True)
def square(l):  # l^2 as dict of degree-2 monomials (x^2 = 0, collisions dropped)
    out = {}
    for u in range(v):
        if not l[u]: continue
        for w in range(u + 1, v):
            if l[w] and hole(u) != hole(w):
                out[(u, w)] = (out.get((u, w), 0) + 2 * l[u] * l[w]) % 3
    return out
def ann_dim(q):
    imgs = np.array([vec3(mul(q, e)) for e in basisA1], dtype=np.uint8)
    Q, _ = gf3.pack(imgs)
    r = gf3.rref(None, parallel=True, packed=(np.vstack([Prel, Q]), W, len(M3)))[2].shape[0] - rel_rank
    return g1 - r
rng = np.random.default_rng(a.seed); res = {'n': n, 'gamma_1': g1, 'gamma_3': len(M3) - rel_rank, 'probes': {}}
def rand_l(pigeons):
    l = np.zeros(v, dtype=np.int64)
    for i in pigeons: l[i * n:(i + 1) * n] = rng.integers(0, 3, size=n)
    return l
t0 = time.time()
res['probes']['random'] = [ann_dim(square(rand_l(range(P1)))) for _ in range(a.samples)]
for k in range(1, P1 + 1):
    res['probes'][f'pigeons_{k}'] = [ann_dim(square(rand_l(rng.choice(P1, size=k, replace=False)))) for _ in range(max(10, a.samples // 5))]
col = np.zeros(v, dtype=np.int64); col[[i * n for i in range(P1)]] = rng.integers(1, 3, size=P1)
res['probes']['column'] = [ann_dim(square(col))]
two = []
for _ in range(a.samples):
    q1, q2 = square(rand_l(range(P1))), square(rand_l(range(P1))); c = int(rng.integers(1, 3))
    q = dict(q1)
    for m, x in q2.items(): q[m] = (q.get(m, 0) + c * x) % 3
    two.append(ann_dim(q))
res['probes']['two_squares'] = two
for k in (1, 2, 3):
    two = []
    for _ in range(max(10, a.samples // 5)):
        q1 = square(rand_l(rng.choice(P1, size=k, replace=False))); q2 = square(rand_l(rng.choice(P1, size=k, replace=False)))
        q = dict(q1)
        for m, x in q2.items(): q[m] = (q.get(m, 0) + x) % 3
        two.append(ann_dim(q))
    res['probes'][f'two_squares_pigeons_{k}'] = two
for key, val in res['probes'].items():
    print(key, 'dims:', dict(zip(*np.unique(val, return_counts=True))), flush=True)
print(f'{time.time() - t0:.0f}s')
json.dump(res, open(a.out, 'w'), indent=1, default=int)
