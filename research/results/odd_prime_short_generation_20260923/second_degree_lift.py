"""Symmetric lifting at lemma degree d = 2 (p = 3, three forms) in the matching complex.

Compares rank(Lambda: K_4 -> K_2^A), w -> (D^alpha w)_{|alpha|=2}, with the dimension of symmetric
tuples in K_2 (D_i zeta_a = D_j zeta_b whenever a+e_i = b+e_j, D_i zeta_{2e_i} = 0).  K_s is computed
exactly (nullspace of the marginal map on each row set); all ranks over GF(3).
Usage: python3 second_degree_lift.py OUT.json
"""
import itertools, json, os, random, sys, time
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from short_generation import nullspace, make_forms, gf3
P = 3; r = 3
ALPHAS = [a for a in itertools.product(range(3), repeat=r) if sum(a) == 2]

def marg_basis(N, s):
    inj = list(itertools.permutations(range(N), s)); low = list(itertools.permutations(range(N), s - 1))
    lp = {t: k for k, t in enumerate(low)}
    M = np.zeros((s * len(low), len(inj)), np.uint8)
    for k, t in enumerate(inj):
        for x in range(s):
            M[x * len(low) + lp[t[:x] + t[x + 1:]], k] = 1
    return inj, nullspace(M)

def run(kind, R, N, seed):
    t0 = time.time()
    rng = random.Random(seed); F = make_forms(kind, R, N, r, rng)
    inj2 = list(itertools.permutations(range(N), 2)); p2 = {t: k for k, t in enumerate(inj2)}
    pairs = list(itertools.combinations(range(R), 2)); pp = {p: k for k, p in enumerate(pairs)}
    n2 = len(pairs) * len(inj2)                        # full coordinates of 2-row arrays
    def c2(rows, labs):                                 # rows sorted pair, labels aligned
        return pp[rows] * len(inj2) + p2[labs]
    inj4, B4 = marg_basis(N, 4)
    ncoord = len(ALPHAS) * n2
    blocks = []
    for S in itertools.combinations(range(R), 4):
        L = np.zeros((ncoord, len(inj4)), np.int64)
        for k, t in enumerate(inj4):
            for ai, al in enumerate(ALPHAS):
                ops = [j for j in range(r) for _ in range(al[j])]
                for x, y in itertools.permutations(range(4), 2):
                    v = F[ops[1]][S[x]][t[x]] * F[ops[0]][S[y]][t[y]] % P
                    if v:
                        rest = [z for z in range(4) if z not in (x, y)]
                        L[ai * n2 + c2((S[rest[0]], S[rest[1]]), (t[rest[0]], t[rest[1]])), k] += v
        blocks.append(((L @ B4) % P).astype(np.uint8))
    img = np.ascontiguousarray(np.concatenate(blocks, axis=1).T)
    rk = gf3.rank(img)
    # symmetric tuples: entries in K_2 (zero marginals) and symmetry equations via D: K_2 -> K_1 (full coords)
    n1 = R * N
    def Dmat(j):                                        # n1 x n2
        M = np.zeros((n1, n2), np.int64)
        for (i, i2) in pairs:
            for (a, b) in inj2:
                col = c2((i, i2), (a, b))
                M[i * N + a, col] += F[j][i2][b]; M[i2 * N + b, col] += F[j][i][a]
        return M % P
    Ds = [Dmat(j) for j in range(r)]
    Mg = np.zeros((2 * N * len(pairs), n2), np.int64)   # marginals of 2-row arrays
    for (i, i2) in pairs:
        for (a, b) in inj2:
            col = c2((i, i2), (a, b)); q = pp[(i, i2)]
            Mg[(2 * q) * N + b, col] = 1; Mg[(2 * q + 1) * N + a, col] = 1
    eqs = []
    for ai in range(len(ALPHAS)):
        blk = np.zeros((Mg.shape[0], ncoord), np.int64); blk[:, ai * n2:(ai + 1) * n2] = Mg; eqs.append(blk)
    groups = {}
    for ai, al in enumerate(ALPHAS):
        for j in range(r):
            b = tuple(al[t] + (t == j) for t in range(r)); groups.setdefault(b, []).append((ai, j))
    for b, lst in groups.items():
        def row(ai, j):
            m = np.zeros((n1, ncoord), np.int64); m[:, ai * n2:(ai + 1) * n2] = Ds[j]; return m
        if max(b) == 3: eqs += [row(*lst[0])] if len(lst) == 1 else [row(ai, j) for ai, j in lst]
        else: eqs += [(row(*lst[0]) - row(ai, j)) % P for ai, j in lst[1:]]
    C = (np.concatenate(eqs, axis=0) % P).astype(np.uint8)
    dsym = ncoord - gf3.rank(C)
    assert not ((C.astype(np.int64) @ img.T.astype(np.int64)) % P).any()
    out = dict(kind=kind, rows=R, labels=N, seed=seed, dimK4=int(img.shape[0]), rank_lambda=int(rk),
               dim_sym=int(dsym), onto=bool(rk == dsym), seconds=time.time() - t0)
    print(out, flush=True); return out

if __name__ == '__main__':
    res = [run(k, R, 7, 1) for k in ('generic', 'rowdep') for R in (5, 6, 7, 8)]
    json.dump(dict(results=res), open(sys.argv[1], 'w'), indent=1)
