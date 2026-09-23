"""Edge Castelnuovo sequence for top algebras of bipartite boards.

For a board Gamma (rows with allowed label sets), K_t(Gamma) = sum over t-sets S of rows of the zero-marginal arrays on
injective labelings of S inside Gamma (the top cycles of the matching complex of Gamma restricted to S).
Tested statement: for the complete board (R, N) and one edge e = (i, a),
    dim K_t(Gamma) = dim K_t(Gamma minus e) + dim K_{t-1}(Gamma / e)       (Gamma / e: delete row i and label a),
i.e. the restriction K_t(Gamma) -> K_{t-1}(Gamma/e) (coefficients on faces containing e) is onto; by the deletion-link
sequence this holds when the reduced homology of the matching complex of (Gamma minus e) restricted to each row set, in
degree t-2, vanishes.  Exact ranks over GF(3) and over Q (float rank, small sizes).
Usage: python3 edge_sequence.py --out OUT.json"""
import argparse, itertools, json
import numpy as np
def rank_mod(M, p):
    A = M % p; r = 0; rows, cols = A.shape
    for c in range(cols):
        if r == rows: break
        piv = np.nonzero(A[r:, c])[0]
        if len(piv) == 0: continue
        k = r + piv[0]; A[[r, k]] = A[[k, r]]; A[r] = A[r] * pow(int(A[r, c]), p - 2, p) % p
        nz = np.nonzero(A[:, c])[0]; nz = nz[nz != r]; A[nz] = (A[nz] - np.outer(A[nz, c], A[r])) % p; r += 1
    return r
def local_dim(allowed, S, field):
    faces = [t for t in itertools.product(*[sorted(allowed[r]) for r in S]) if len(set(t)) == len(t)]
    if not faces: return 0
    fi = {f: k for k, f in enumerate(faces)}; low = {}
    rows = []
    for k, f in enumerate(faces):
        for x in range(len(S)):
            key = (x, f[:x] + f[x + 1:]); low.setdefault(key, len(low)); rows.append((low[key], k))
    M = np.zeros((len(low), len(faces)), np.int64)
    for a, b in rows: M[a, b] = 1
    rk = rank_mod(M, 3) if field == 3 else np.linalg.matrix_rank(M.astype(float))
    return len(faces) - int(rk)
def K(allowed, t, field):
    return sum(local_dim(allowed, S, field) for S in itertools.combinations(sorted(allowed), t))
ap = argparse.ArgumentParser(); ap.add_argument('--out', required=True); a = ap.parse_args(); res = []
for (R, N) in ((4, 3), (5, 4), (6, 5), (7, 6), (5, 5), (4, 5)):
    full = {r: set(range(N)) for r in range(R)}; i, lab = R - 1, 0
    dele = {r: set(v) for r, v in full.items()}; dele[i].discard(lab)
    cont = {r: set(range(N)) - {lab} for r in range(R - 1)}
    for t in (2, 3):
        for field in (3, 0):
            kf, kd, kc = K(full, t, field), K(dele, t, field), K(cont, t - 1, field)
            res.append(dict(R=R, N=N, t=t, field=field, K=kf, K_deleted=kd, K_contracted=kc, exact=kf == kd + kc))
            print(res[-1], flush=True)
json.dump(res, open(a.out, 'w'), indent=1)
