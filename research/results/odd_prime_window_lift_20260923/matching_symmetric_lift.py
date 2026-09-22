"""Symmetric-lift test in the matching complex at p=3, r=3 forms, lemma degree d=1.
K_s = direct sum over s-row sets S of arrays on injections S -> labels with zero ordinary marginal in every row.
delta^f_i: (delta a)(sigma') = sum_{w not in sigma'} f(w) a(sigma' + (i->w)).  D^(j) = sum_i delta^{F[j][i]}_i.
Compares dim(symmetric 6-tuples in K_1) = 6 dim K_1 - rank(symmetry constraints in K_0 = k) with rank of
Lambda: K_3 -> K_1^6, w -> (m(a) D^a w)_{|a|=2}.  Exact arithmetic mod 3.
Usage: --rows R --labels N --mode dense|disjoint --seed S --out PATH"""
import argparse, itertools, json
import numpy as np
P = 3
def rref(A):
    A = A.copy() % P; r = 0; piv = []
    for c in range(A.shape[1]):
        nz = np.nonzero(A[r:, c])[0]
        if len(nz) == 0: continue
        k = r + nz[0]; A[[r, k]] = A[[k, r]]
        if A[r, c] != 1: A[r] = (A[r] * 2) % P   # inverse of 2 mod 3 is 2
        col = A[:, c].copy(); col[r] = 0; nzr = np.nonzero(col)[0]
        if len(nzr): A[nzr] = (A[nzr] - np.outer(col[nzr], A[r])) % P
        piv.append(c); r += 1
        if r == A.shape[0]: break
    return A[:r], piv
def nullspace(A, n):
    if A.shape[0] == 0: return np.eye(n, dtype=np.int64)
    R_, piv = rref(A); free = [c for c in range(n) if c not in set(piv)]
    out = np.zeros((len(free), n), dtype=np.int64)
    for t, f in enumerate(free):
        out[t, f] = 1
        for i, c in enumerate(piv): out[t, c] = (-R_[i, f]) % P
    return out
ap = argparse.ArgumentParser(); ap.add_argument('--rows', type=int); ap.add_argument('--labels', type=int)
ap.add_argument('--mode', default='dense'); ap.add_argument('--seed', type=int, default=0); ap.add_argument('--out')
a = ap.parse_args(); Rr, N = a.rows, a.labels
rng = np.random.default_rng(a.seed)
F = np.zeros((3, Rr, N), dtype=np.int64)
for i in range(Rr):
    for j in range(3):
        if a.mode == 'dense' or i % 3 == j: F[j, i] = rng.integers(0, P, size=N)
alphas = [(2, 0, 0), (0, 2, 0), (0, 0, 2), (1, 1, 0), (1, 0, 1), (0, 1, 1)]
mult = {al: {2: 1, 1: 2}[max(al)] for al in alphas}   # 2!/alpha!: 1 for (2,0,0), 2 for (1,1,0)
# K_1 coordinates: (row i, label w) -> i*N+w, full function space; K_1 = sum-zero per row.
n1 = Rr * N
def D1(j):  # D^(j): functions on K_1 -> k, as a vector over K_1 coords
    return F[j].reshape(-1)
# Symmetric constraints on tuples (z_alpha) in K_1 (use K_1 basis e_{i,w}-e_{i,0})
B1 = []
for i in range(Rr):
    for w in range(1, N):
        v = np.zeros(n1, dtype=np.int64); v[i * N + w] = 1; v[i * N] = P - 1; B1.append(v)
B1 = np.array(B1); k1 = len(B1)
cons = []
for b in itertools.product(range(4), repeat=3):
    if sum(b) != 3: continue
    pre = [(alphas.index(tuple(b[t] - (t == j) for t in range(3))), j) for j in range(3) if b[j] >= 1]
    def row(ai, j, c):
        v = np.zeros(6 * k1, dtype=np.int64); v[ai * k1:(ai + 1) * k1] = (c * (B1 @ D1(j))) % P; return v
    inv = lambda ai: {1: 1, 2: 2}[mult[alphas[ai]]]
    if len(pre) == 1: cons.append(row(pre[0][0], pre[0][1], 1))
    else:
        for (ai, j) in pre[1:]:
            cons.append((row(pre[0][0], pre[0][1], inv(pre[0][0])) - row(ai, j, inv(ai))) % P)
cons = np.array(cons); crank = len(rref(cons)[1]); sym_dim = 6 * k1 - crank
clo = []
for b in itertools.product(range(4), repeat=3):
    if sum(b) != 3: continue
    v = np.zeros(6 * k1, dtype=np.int64)
    for j in range(3):
        if b[j] >= 1:
            ai = alphas.index(tuple(b[t] - (t == j) for t in range(3))); v[ai * k1:(ai + 1) * k1] = (v[ai * k1:(ai + 1) * k1] + B1 @ D1(j)) % P
    clo.append(v)
closed_dim = 6 * k1 - len(rref(np.array(clo))[1])
# Lifts: per 3-row set S, arrays on injections, zero marginal kernel, then Lambda.
inj = list(itertools.permutations(range(N), 3)); iidx = {s: t for t, s in enumerate(inj)}; m3 = len(inj)
marg = []
for pos in range(3):
    for rest in itertools.permutations(range(N), 2):
        v = np.zeros(m3, dtype=np.int64)
        for w in range(N):
            if w in rest: continue
            s = list(rest); s.insert(pos, w); v[iidx[tuple(s)]] = 1
        marg.append(v)
marg = np.array(marg); Z = nullspace(marg, m3)   # basis of marginal-zero arrays on a fixed 3-row set (labels only)
span = np.zeros((0, 6 * n1), dtype=np.int64); rank = 0
for S in itertools.combinations(range(Rr), 3):
    # Lambda on arrays over S: output in K_1^6 full coords (alpha, row, label)
    L = np.zeros((6 * n1, m3), dtype=np.int64)
    for ai, al in enumerate(alphas):
        forms = [j for j in range(3) for _ in range(al[j])]   # multiset of two forms
        # D^{f1} D^{f2} w = sum over ordered pairs of distinct rows (x,y): delta^{f1}_x delta^{f2}_y w
        for (x, y) in itertools.permutations(range(3), 2):
            zr = 3 - x - y
            fx, fy = F[forms[0], S[x]], F[forms[1], S[y]]
            for t, s in enumerate(inj):
                L[ai * n1 + S[zr] * N + s[zr], t] += mult[al] * fx[s[x]] * fy[s[y]]
    img = (L % P) @ Z.T % P
    span, piv = rref(np.vstack([span, img.T]))
    rank = len(piv)
res = {'rows': Rr, 'labels': N, 'mode': a.mode, 'seed': a.seed, 'dim_K1': k1, 'symmetry_constraint_rank': crank,
       'closed_dim': closed_dim, 'symmetric_dim': sym_dim, 'lift_rank': rank, 'deficit': sym_dim - rank}
print(res)
if a.out: json.dump(res, open(a.out, 'w'), indent=1)
