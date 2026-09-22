"""Forced-forms exactness and cocycle lifting in the matching complex, p=3, r forms, levels s=2,3.
K_s: arrays on injections S -> labels (|S|=s) with zero ordinary marginal in every row, summed over s-row sets.
D_l = sum over rows x of the F[l][x]-weighted marginal.  All ranks exact over GF(3) (bit-sliced gf3 library).
Checks, for each level s and j = r..1 with M_j = joint kernel of D_l (l>j):
  forced-forms exactness:  dim(ker D_j^2 on M_j in K_{s-1})  ==  dim D_j(M_j in K_s)
  cocycle lifting:         dim(cocycles in K_{s-1}^r)          ==  dim(gradients of K_s)
Usage: --r R --t T --labels N [--dense] --seed S --out PATH"""
import argparse, itertools, json, os, sys, time
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', 'odd_prime_alignment_mechanism_20260922'))
import gf3
P = 3
def rank(M):
    M = np.ascontiguousarray(np.asarray(M) % P, dtype=np.uint8)
    if M.shape[0] == 0 or M.shape[1] == 0: return 0
    return int(gf3.rank(M, parallel=True))
def nullspace_small(A, n):
    A = A.copy() % P; r = 0; piv = []
    for c in range(n):
        nz = np.nonzero(A[r:, c])[0]
        if len(nz) == 0: continue
        k = r + nz[0]; A[[r, k]] = A[[k, r]]
        if A[r, c] != 1: A[r] = (A[r] * 2) % P
        col = A[:, c].copy(); col[r] = 0; z = np.nonzero(col)[0]
        if len(z): A[z] = (A[z] - np.outer(col[z], A[r])) % P
        piv.append(c); r += 1
        if r == A.shape[0]: break
    free = [c for c in range(n) if c not in set(piv)]
    out = np.zeros((len(free), n), dtype=np.int64)
    for t, f in enumerate(free):
        out[t, f] = 1
        for i, c in enumerate(piv): out[t, c] = (-A[i, f]) % P
    return out
ap = argparse.ArgumentParser(); ap.add_argument('--r', type=int, default=3); ap.add_argument('--t', type=int, default=4)
ap.add_argument('--labels', type=int, default=7); ap.add_argument('--dense', action='store_true'); ap.add_argument('--seed', type=int, default=0)
ap.add_argument('--out'); a = ap.parse_args()
r, N = a.r, a.labels; Rr = r * a.t
rng = np.random.default_rng(a.seed)
F = np.zeros((r, Rr, N), dtype=np.int64)
for i in range(Rr):
    for l in range(r):
        if a.dense or i // a.t == l: F[l, i] = rng.integers(0, P, size=N)
inj = {s: list(itertools.permutations(range(N), s)) for s in range(4)}
iidx = {s: {x: q for q, x in enumerate(inj[s])} for s in range(4)}
sets = {s: list(itertools.combinations(range(Rr), s)) for s in range(4)}
sidx = {s: {S: q for q, S in enumerate(sets[s])} for s in range(4)}
# per-set marginal-zero basis Z_s (rows = basis vectors over injections)
Z = {0: np.ones((1, 1), dtype=np.int64)}
for s in (1, 2, 3):
    marg = []
    for pos in range(s):
        for rest in inj[s - 1]:
            v = np.zeros(len(inj[s]), dtype=np.int64)
            for w in range(N):
                if w in rest: continue
                x = list(rest); x.insert(pos, w); v[iidx[s][tuple(x)]] = 1
            marg.append(v)
    Z[s] = nullspace_small(np.array(marg), len(inj[s]))
dimU = {s: len(sets[s]) * len(inj[s]) for s in range(4)}
dimK = {s: len(sets[s]) * Z[s].shape[0] for s in range(4)}
# W[s][pos]: map from arrays on s injections to s-1 injections, weighted by label at pos: returns function f -> matrix
def Wmat(s, pos, f):
    M = np.zeros((len(inj[s - 1]), len(inj[s])), dtype=np.int64)
    for q, x in enumerate(inj[s]):
        y = x[:pos] + x[pos + 1:]; M[iidx[s - 1][y], q] = f[x[pos]]
    return M
def D_on_U(l, s):
    """D_l: U_s -> U_{s-1} (full array coordinates)."""
    M = np.zeros((dimU[s - 1], dimU[s]), dtype=np.int64)
    for S in sets[s]:
        c0 = sidx[s][S] * len(inj[s])
        for pos in range(s):
            f = F[l, S[pos]]
            if not f.any(): continue
            T = S[:pos] + S[pos + 1:]; r0 = sidx[s - 1][T] * len(inj[s - 1])
            M[r0:r0 + len(inj[s - 1]), c0:c0 + len(inj[s])] += Wmat(s, pos, f)
    return M % P
def basisK(s):
    B = np.zeros((dimU[s], dimK[s]), dtype=np.int64); z = Z[s].shape[0]
    for q, S in enumerate(sets[s]):
        B[q * len(inj[s]):(q + 1) * len(inj[s]), q * z:(q + 1) * z] = Z[s].T
    return B
t0 = time.time()
def D_on_K(l, s):
    """D_l: K_s -> U_{s-1}, built block by block in the per-set bases Z_s (uint8)."""
    z = Z[s].shape[0]; M = np.zeros((dimU[s - 1], dimK[s]), dtype=np.uint8)
    for q, S in enumerate(sets[s]):
        for pos in range(s):
            f = F[l, S[pos]]
            if not f.any(): continue
            T = S[:pos] + S[pos + 1:]; r0 = sidx[s - 1][T] * len(inj[s - 1])
            blk = (Wmat(s, pos, f) @ Z[s].T) % P
            M[r0:r0 + len(inj[s - 1]), q * z:(q + 1) * z] = (M[r0:r0 + len(inj[s - 1]), q * z:(q + 1) * z].astype(np.int64) + blk) % P
    return M
DU = {(l, s): D_on_U(l, s) for l in range(r) for s in (1, 2)}
DK = {(l, s): D_on_K(l, s) for l in range(r) for s in (1, 2, 3)}                        # K_s -> U_{s-1}
D2K = {(l, s): ((DU[(l, s - 1)] @ DK[(l, s)].astype(np.int64)) % P).astype(np.uint8) for l in range(r) for s in (2, 3)}
def kerdim(s, mats):
    return dimK[s] - (rank(np.vstack(mats)) if mats else 0)
res = {'r': r, 't': a.t, 'labels': N, 'dense': a.dense, 'seed': a.seed, 'dimK': dimK, 'levels': {}}
for s in (2, 3):
    lev = {'forced_forms': []}
    for j in reversed(range(r)):
        later = [DK[(l, s)] for l in range(j + 1, r)]
        later_low = [DK[(l, s - 1)] for l in range(j + 1, r)]
        img = kerdim(s, later) - kerdim(s, later + [DK[(j, s)]])
        sq = [D2K[(j, s - 1)]] if s - 1 >= 2 else []   # D_j^2 on K_{s-1} lands in U_{s-3}; zero map when s-1 < 2
        ker = kerdim(s - 1, later_low + sq)
        lev['forced_forms'].append({'j': j + 1, 'kernel': int(ker), 'image': int(img), 'exact': ker == img})
    # cocycles in K_{s-1}^r
    n = dimK[s - 1]; rows = []
    for i, j in itertools.combinations(range(r), 2):
        blk = np.zeros((dimU[s - 2], r * n), dtype=np.int64)
        blk[:, j * n:(j + 1) * n] = DK[(i, s - 1)]; blk[:, i * n:(i + 1) * n] = (P - DK[(j, s - 1)].astype(np.int64)) % P
        rows.append(blk)
    if s - 1 >= 2:
        for i in range(r):
            blk = np.zeros((dimU[s - 3], r * n), dtype=np.int64); blk[:, i * n:(i + 1) * n] = D2K[(i, s - 1)]; rows.append(blk)
    Zdim = r * n - rank(np.vstack(rows))
    Bdim = rank(np.vstack([DK[(l, s)] for l in range(r)]))
    lev['cocycles'] = int(Zdim); lev['gradients'] = int(Bdim); lev['cocycle_lifting'] = Zdim == Bdim
    res['levels'][s] = lev
    print(s, lev, f'{time.time() - t0:.0f}s', flush=True)
if a.out: json.dump(res, open(a.out, 'w'), indent=1)
