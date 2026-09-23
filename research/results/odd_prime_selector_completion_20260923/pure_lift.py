"""Pure (selector) lifting at lemma degree d = 2, p = 3, three forms, in the matching complex.

Endpoint data (z_1, z_2, z_3) in K_2 with D_i z_i = 0 and D_i^2 z_j = D_j^2 z_i; lifts are
(D_1^2 w, D_2^2 w, D_3^2 w), w in K_4.  Compares the rank of the lift map with the dimension of the
endpoint data, exactly over GF(3).  Reuses the matching-complex code of second_degree_lift.py.
Usage: python3 pure_lift.py OUT.json"""
import itertools, json, os, random, sys, time
import numpy as np
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'odd_prime_short_generation_20260923'))
from short_generation import nullspace, make_forms, gf3
from second_degree_lift import marg_basis
P = 3; r = 3

def run(kind, R, N, seed):
    t0 = time.time(); F = make_forms(kind, R, N, r, random.Random(seed))
    inj2 = list(itertools.permutations(range(N), 2)); p2 = {t: k for k, t in enumerate(inj2)}
    pairs = list(itertools.combinations(range(R), 2)); pp = {p: k for k, p in enumerate(pairs)}
    n2 = len(pairs) * len(inj2)
    def c2(rows, labs): return pp[rows] * len(inj2) + p2[labs]
    inj4, B4 = marg_basis(N, 4)
    blocks = []
    for S in itertools.combinations(range(R), 4):
        L = np.zeros((r * n2, len(inj4)), np.int64)
        for k, t in enumerate(inj4):
            for i in range(r):                       # D_i^2: two distinct rows contracted by form i
                for x, y in itertools.permutations(range(4), 2):
                    v = F[i][S[x]][t[x]] * F[i][S[y]][t[y]] % P
                    if v:
                        rest = [z for z in range(4) if z not in (x, y)]
                        L[i * n2 + c2((S[rest[0]], S[rest[1]]), (t[rest[0]], t[rest[1]])), k] += v
        blocks.append(((L @ B4) % P).astype(np.uint8))
    img = np.ascontiguousarray(np.concatenate(blocks, axis=1).T)
    rk = gf3.rank(img)
    # endpoint data: z_i in K_2 (zero marginals), D_i z_i = 0 (in K_1), D_i^2 z_j - D_j^2 z_i = 0 (in K_0)
    n1 = R * N
    def Dmat(j):
        M = np.zeros((n1, n2), np.int64)
        for (i, i2) in pairs:
            for (a, b) in inj2:
                col = c2((i, i2), (a, b)); M[i * N + a, col] += F[j][i2][b]; M[i2 * N + b, col] += F[j][i][a]
        return M % P
    def D1mat(j):                                     # K_1 (full coords) -> K_0 = k
        M = np.zeros((1, n1), np.int64)
        for i in range(R):
            for a in range(N): M[0, i * N + a] = F[j][i][a]
        return M
    Ds = [Dmat(j) for j in range(r)]; D1 = [D1mat(j) for j in range(r)]
    Mg = np.zeros((2 * N * len(pairs), n2), np.int64)
    for (i, i2) in pairs:
        q = pp[(i, i2)]
        for (a, b) in inj2:
            col = c2((i, i2), (a, b)); Mg[(2 * q) * N + b, col] = 1; Mg[(2 * q + 1) * N + a, col] = 1
    eqs = []
    for i in range(r):
        blk = np.zeros((Mg.shape[0], r * n2), np.int64); blk[:, i * n2:(i + 1) * n2] = Mg; eqs.append(blk)
        blk = np.zeros((n1, r * n2), np.int64); blk[:, i * n2:(i + 1) * n2] = Ds[i]; eqs.append(blk)
    for i, j in itertools.combinations(range(r), 2):
        row = np.zeros((1, r * n2), np.int64)
        row[:, j * n2:(j + 1) * n2] += (D1[i] @ Ds[i]) % P
        row[:, i * n2:(i + 1) * n2] -= (D1[j] @ Ds[j]) % P
        eqs.append(row % P)
    C = (np.concatenate(eqs) % P).astype(np.uint8)
    dim_data = r * n2 - gf3.rank(C)
    assert not ((C.astype(np.int64) @ img.T.astype(np.int64)) % P).any()   # lifts satisfy the relations
    out = dict(kind=kind, rows=R, labels=N, seed=seed, rank_lift=int(rk), dim_endpoint_data=int(dim_data),
               onto=bool(rk == dim_data), seconds=time.time() - t0)
    print(out, flush=True); return out

if __name__ == '__main__':
    res = [run(k, R, 7, 1) for k in ('generic', 'rowdep') for R in (5, 6, 7)]
    json.dump(dict(results=res), open(sys.argv[1], 'w'), indent=1)
