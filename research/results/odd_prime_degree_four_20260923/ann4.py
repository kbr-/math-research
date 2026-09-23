"""Degree-four annihilators in the top algebra A of weak unary PHP over F_3 (n holes): dim Ann_{A_2}(q) for q in A_2,
computed as gamma_2 - rank(E -> E q : A_2 -> A_4).  Probes: q = l^2 for uniform l (Frobenius part l*A_1 predicted,
dimension gamma_1 when Ann_{A_1}(l)=0), and q = l1^2 + c l2^2 (span-one analogue).  Usage: --n N --samples K --out PATH"""
import argparse, itertools, json, os, sys, time
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', 'odd_prime_alignment_mechanism_20260922'))
import gf3
ap = argparse.ArgumentParser(); ap.add_argument('--n', type=int, default=6); ap.add_argument('--samples', type=int, default=5)
ap.add_argument('--out'); opt = ap.parse_args()
n = opt.n; P1 = n + 1; v = P1 * n; hole = lambda u: u % n
def mons(k): return [c for c in itertools.combinations(range(v), k) if len({hole(u) for u in c}) == k]
t0 = time.time()
M2, M3, M4 = mons(2), mons(3), mons(4); I4 = {m: i for i, m in enumerate(M4)}
def mulpoly(poly, lin):
    out = {}
    for m, c in poly.items():
        hs = {hole(u) for u in m}
        for u in np.nonzero(lin)[0]:
            u = int(u)
            if u not in m and hole(u) not in hs:
                mm = tuple(sorted(m + (u,))); out[mm] = (out.get(mm, 0) + c * int(lin[u])) % 3
    return out
def mulmon(m, q):  # monomial m times polynomial q (dict of monomials)
    out = {}
    for mq, c in q.items():
        if set(m) & set(mq) or {hole(u) for u in m} & {hole(u) for u in mq}: continue
        mm = tuple(sorted(m + mq)); out[mm] = (out.get(mm, 0) + c) % 3
    return out
def vec4(poly):
    x = np.zeros(len(M4), dtype=np.uint8)
    for m, c in poly.items():
        if c % 3: x[I4[m]] = c % 3
    return x
rows = []
for i in range(P1):
    R = np.zeros(v, dtype=np.int64); R[i * n:(i + 1) * n] = 1
    for m in M3: rows.append(vec4(mulpoly({m: 1}, R)))
Prel, W, _ = gf3.rref(np.array(rows, dtype=np.uint8), parallel=True); rel_rank = Prel.shape[0]
print(f'n={n}: |M4|={len(M4)}, relation rank {rel_rank}, gamma_4={len(M4)-rel_rank}, {time.time()-t0:.0f}s', flush=True)
gamma2 = {6: 462}.get(n)
def square(l):
    out = {}
    nz = [int(u) for u in np.nonzero(l)[0]]
    for i, u in enumerate(nz):
        for w in nz[i + 1:]:
            if hole(u) != hole(w): out[(u, w)] = (out.get((u, w), 0) + 2 * int(l[u]) * int(l[w])) % 3
    return out
def mult_rank(q):
    imgs = np.array([vec4(mulmon(m, q)) for m in M2], dtype=np.uint8)
    Q, _ = gf3.pack(imgs)
    return gf3.rref(None, parallel=True, packed=(np.vstack([Prel, Q]), W, len(M4)))[2].shape[0] - rel_rank
rng = np.random.default_rng(3); res = {'n': n, 'gamma_4': len(M4) - rel_rank, 'gamma_2': gamma2, 'probes': {}}
res['probes']['square'] = [gamma2 - mult_rank(square(rng.integers(0, 3, size=v))) for _ in range(opt.samples)]
two = []
for _ in range(opt.samples):
    q = dict(square(rng.integers(0, 3, size=v)))
    for m, x in square(rng.integers(0, 3, size=v)).items(): q[m] = (q.get(m, 0) + int(rng.integers(1, 3)) * x) % 3
    two.append(gamma2 - mult_rank(q))
res['probes']['two_squares'] = two
print(res, f'{time.time()-t0:.0f}s', flush=True); json.dump(res, open(opt.out, 'w'), indent=1, default=int)
