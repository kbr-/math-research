"""Short generation of the level-two joint kernel in the matching complex (p = 3).

Z_2 = {x in K_2 : D_j x = 0 for all j}, K_2 = arrays on injections of 2-row sets into N labels with
zero ordinary marginals, D_j = sum_i delta_i^{f_i^(j)}.  For each m, compares dim Z_2 with the
dimension of the span of Z_2(U) = elements of Z_2 supported on pairs inside U, over all m-row sets U.
Exact GF(3) ranks.  Usage: python3 short_generation.py OUT.json
"""
import itertools, json, os, random, sys, time
import numpy as np
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..',
                                'odd_prime_alignment_mechanism_20260922'))
import gf3
P = 3

def nullspace(M):
    """Basis (columns) of the nullspace of M over GF(3)."""
    M = np.asarray(M, np.uint8) % 3; n = M.shape[1]
    if M.shape[0] == 0: return np.eye(n, dtype=np.int64)
    E, W, piv = gf3.rref(M, full=True)
    U = gf3.unpack(E, W, n).astype(np.int64); piv = list(piv); ps = set(piv)
    free = [c for c in range(n) if c not in ps]
    B = np.zeros((n, len(free)), np.int64)
    for fi, f in enumerate(free):
        B[f, fi] = 1
        for r_, pc in enumerate(piv): B[pc, fi] = (-U[r_, f]) % P
    assert not ((M.astype(np.int64) @ B) % P).any()
    return B

def make_forms(kind, R, N, r, rng):
    F = [[[rng.randrange(3) for _ in range(N)] for _ in range(R)] for _ in range(r)]
    if kind == 'rowdep':                              # last form dependent on the others per row
        for i in range(R):
            co = [rng.randrange(3) for _ in range(r - 1)]
            F[r - 1][i] = [sum(co[j] * F[j][i][w] for j in range(r - 1)) % P for w in range(N)]
    return F

def run(kind, R, N, r, seed, ms):
    rng = random.Random(seed); F = make_forms(kind, R, N, r, rng)
    inj = list(itertools.permutations(range(N), 2))
    Mm = np.zeros((2 * N, len(inj)), np.uint8)       # marginals: sum over row-1 label, row-2 label
    for k, (a, b) in enumerate(inj): Mm[b, k] = 1; Mm[N + a, k] = 1
    B = nullspace(Mm)                                  # per-pair basis of K_2, len(inj) x dimK
    dK = B.shape[1]
    pairs = list(itertools.combinations(range(R), 2))
    ncoord = r * R * N
    cols = []
    for (i, i2) in pairs:                               # Phi on the per-pair basis
        L = np.zeros((ncoord, len(inj)), np.int64)
        for k, (a, b) in enumerate(inj):                # row i label a, row i2 label b
            for j in range(r):
                L[(j * R + i) * N + a, k] += F[j][i2][b]   # contract row i2
                L[(j * R + i2) * N + b, k] += F[j][i][a]   # contract row i
        cols.append((L @ B) % P)
    Phi = np.concatenate(cols, axis=1)                  # ncoord x (#pairs * dK)
    dimK2 = Phi.shape[1]
    Z = nullspace(Phi); dimZ = Z.shape[1]
    out = dict(kind=kind, rows=R, labels=N, forms=r, seed=seed, dimK2=dimK2, dimZ2=int(dimZ), span={})
    pidx = {p: t for t, p in enumerate(pairs)}
    for m in ms:
        vecs = []
        for U in itertools.combinations(range(R), m):
            sel = [pidx[p] for p in itertools.combinations(U, 2)]
            colsel = np.concatenate([np.arange(s * dK, (s + 1) * dK) for s in sel])
            ZU = nullspace(Phi[:, colsel])
            if ZU.shape[1] == 0: continue
            full = np.zeros((dimK2, ZU.shape[1]), np.int64); full[colsel, :] = ZU
            vecs.append(full.T)
        S = np.concatenate(vecs, axis=0).astype(np.uint8) if vecs else np.zeros((0, dimK2), np.uint8)
        out['span'][m] = int(gf3.rank(S)) if S.shape[0] else 0
    print(out, flush=True)
    return out

if __name__ == '__main__':
    t0 = time.time(); res = []
    for kind in ('generic', 'rowdep'):
        for (R, N) in ((8, 7), (10, 7), (8, 9)):
            for seed in (1, 2):
                res.append(run(kind, R, N, 3, seed, (2, 3, 4, 5, 6)))
    for r in (2, 4):
        res.append(run('generic', 9, 7, r, 1, tuple(range(2, 8))))
    json.dump(dict(results=res, seconds=time.time() - t0), open(sys.argv[1], 'w'), indent=1)
