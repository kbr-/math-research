"""Least rows per form at which symmetric r-tuples at lemma degree d=1 lift in the matching complex, p=3.
r forms with disjoint supports (t rows each, random F_3 row functions), N labels.  For each r and t prints
symmetric_dim, lift_rank.  Symmetric = closed for r=2 (recorded two-parameter lemma regime)."""
import argparse, itertools, json, sys
import numpy as np
sys.path.insert(0, __file__.rsplit('/', 1)[0])
P = 3
def rref(A):
    A = A.copy() % P; r = 0; piv = []
    for c in range(A.shape[1]):
        nz = np.nonzero(A[r:, c])[0]
        if len(nz) == 0: continue
        k = r + nz[0]; A[[r, k]] = A[[k, r]]
        if A[r, c] != 1: A[r] = (A[r] * 2) % P
        col = A[:, c].copy(); col[r] = 0; nzr = np.nonzero(col)[0]
        if len(nzr): A[nzr] = (A[nzr] - np.outer(col[nzr], A[r])) % P
        piv.append(c); r += 1
        if r == A.shape[0]: break
    return A[:r], piv
def nullspace(A, n):
    R_, piv = rref(A); free = [c for c in range(n) if c not in set(piv)]
    out = np.zeros((len(free), n), dtype=np.int64)
    for t, f in enumerate(free):
        out[t, f] = 1
        for i, c in enumerate(piv): out[t, c] = (-R_[i, f]) % P
    return out
def run(r, t, N, seed, dense=False):
    rng = np.random.default_rng(seed); Rr = r * t
    F = np.zeros((r, Rr, N), dtype=np.int64)
    for i in range(Rr):
        for j in range(r):
            if dense or i // t == j: F[j, i] = rng.integers(0, P, size=N)
    alphas = [al for al in itertools.product(range(3), repeat=r) if sum(al) == 2]
    mult = {al: (1 if max(al) == 2 else 2) for al in alphas}
    n1 = Rr * N
    B1 = []
    for i in range(Rr):
        for w in range(1, N):
            v = np.zeros(n1, dtype=np.int64); v[i * N + w] = 1; v[i * N] = P - 1; B1.append(v)
    B1 = np.array(B1); k1 = len(B1); nA = len(alphas)
    cons = []
    for b in itertools.product(range(4), repeat=r):
        if sum(b) != 3: continue
        pre = [(alphas.index(tuple(b[s] - (s == j) for s in range(r))), j) for j in range(r) if b[j] >= 1]
        def row(ai, j, c):
            v = np.zeros(nA * k1, dtype=np.int64); v[ai * k1:(ai + 1) * k1] = (c * (B1 @ F[j].reshape(-1))) % P; return v
        inv = lambda ai: mult[alphas[ai]]  # 1 and 2 are self-inverse mod 3
        if len(pre) == 1: cons.append(row(pre[0][0], pre[0][1], 1))
        else:
            for (ai, j) in pre[1:]:
                cons.append((row(pre[0][0], pre[0][1], inv(pre[0][0])) - row(ai, j, inv(ai))) % P)
    sym = nA * k1 - len(rref(np.array(cons))[1])
    inj = list(itertools.permutations(range(N), 3)); iidx = {s: q for q, s in enumerate(inj)}; m3 = len(inj)
    marg = []
    for pos in range(3):
        for rest in itertools.permutations(range(N), 2):
            v = np.zeros(m3, dtype=np.int64)
            for w in range(N):
                if w in rest: continue
                s = list(rest); s.insert(pos, w); v[iidx[tuple(s)]] = 1
            marg.append(v)
    Z = nullspace(np.array(marg), m3)
    span = np.zeros((0, nA * n1), dtype=np.int64); rank = 0
    for S in itertools.combinations(range(Rr), 3):
        L = np.zeros((nA * n1, m3), dtype=np.int64)
        for ai, al in enumerate(alphas):
            forms = [j for j in range(r) for _ in range(al[j])]
            for (x, y) in itertools.permutations(range(3), 2):
                z = 3 - x - y; fx, fy = F[forms[0], S[x]], F[forms[1], S[y]]
                if not fx.any() or not fy.any(): continue
                for q, s in enumerate(inj):
                    L[ai * n1 + S[z] * N + s[z], q] += mult[al] * fx[s[x]] * fy[s[y]]
        img = (L % P) @ Z.T % P
        nzc = img[:, img.any(axis=0)]
        if nzc.shape[1]:
            span, piv = rref(np.vstack([span, nzc.T])); rank = len(piv)
        if rank == sym: break
    return {'r': r, 't': t, 'labels': N, 'seed': seed, 'dense': dense, 'symmetric_dim': int(sym), 'lift_rank': int(rank)}
ap = argparse.ArgumentParser(); ap.add_argument('--labels', type=int, default=7); ap.add_argument('--out')
ap.add_argument('--rs', default='2,3,4'); ap.add_argument('--tmax', type=int, default=6); ap.add_argument('--tmin', type=int, default=1)
a = ap.parse_args(); res = []
for r in map(int, a.rs.split(',')):
    for t in range(a.tmin, a.tmax + 1):
        o = run(r, t, a.labels, 100 * r + t); res.append(o); print(o, flush=True)
        if o['lift_rank'] == o['symmetric_dim']: break
json.dump(res, open(a.out, 'w'), indent=1)
