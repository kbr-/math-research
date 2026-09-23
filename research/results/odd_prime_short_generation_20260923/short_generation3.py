"""Short generation of the level-three joint kernel Z_3 = {x in K_3 : D_j x = 0 for all j} (p = 3).

Compares dim Z_3 with the span of Z_3(U), the elements supported on triples inside an m-row set U.
K_3 is exact (nullspace of the marginal map per triple); D_j x is taken in full coordinates of
2-row arrays.  Exact GF(3) ranks.  Usage: python3 short_generation3.py OUT.json
"""
import itertools, json, os, random, sys, time
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from short_generation import nullspace, make_forms, gf3
from second_degree_lift import marg_basis
P = 3

def run(kind, R, N, r, seed, ms):
    t0 = time.time(); rng = random.Random(seed); F = make_forms(kind, R, N, r, rng)
    inj3, B3 = marg_basis(N, 3); dK = B3.shape[1]
    inj2 = list(itertools.permutations(range(N), 2)); p2 = {t: k for k, t in enumerate(inj2)}
    pairs = list(itertools.combinations(range(R), 2)); pp = {p: k for k, p in enumerate(pairs)}
    ncoord = r * len(pairs) * len(inj2)
    trip = list(itertools.combinations(range(R), 3)); tp = {t: k for k, t in enumerate(trip)}
    cols = []
    for S in trip:
        L = np.zeros((ncoord, len(inj3)), np.int64)
        for k, t in enumerate(inj3):
            for x in range(3):
                rest = [y for y in range(3) if y != x]
                pr = (S[rest[0]], S[rest[1]]); lab = (t[rest[0]], t[rest[1]])
                for j in range(r):
                    v = F[j][S[x]][t[x]]
                    if v: L[(j * len(pairs) + pp[pr]) * len(inj2) + p2[lab], k] += v
        cols.append(((L @ B3) % P).astype(np.uint8))
    Phi = np.concatenate(cols, axis=1); dimK3 = Phi.shape[1]
    dimZ = dimK3 - gf3.rank(np.ascontiguousarray(Phi))
    out = dict(kind=kind, rows=R, labels=N, forms=r, seed=seed, dimK3=dimK3, dimZ3=int(dimZ), span={})
    for m in ms:
        vecs = []
        for U in itertools.combinations(range(R), m):
            sel = [tp[T] for T in itertools.combinations(U, 3)]
            colsel = np.concatenate([np.arange(s * dK, (s + 1) * dK) for s in sel])
            sub = Phi[:, colsel]; sub = sub[sub.any(axis=1)]      # only rows the sub-board touches
            ZU = nullspace(sub)
            if ZU.shape[1] == 0: continue
            full = np.zeros((ZU.shape[1], dimK3), np.uint8); full[:, colsel] = ZU.T % P
            vecs.append(full)
            if sum(v.shape[0] for v in vecs) > dimK3:        # compress by row reduction
                E, W, piv = gf3.rref(np.ascontiguousarray(np.concatenate(vecs, axis=0)))
                vecs = [gf3.unpack(E, W, dimK3)]
        S_ = np.concatenate(vecs, axis=0) if vecs else np.zeros((0, dimK3), np.uint8)
        out['span'][m] = int(gf3.rank(np.ascontiguousarray(S_))) if S_.shape[0] else 0
        if out['span'][m] == dimZ: break
    out['seconds'] = time.time() - t0
    print(out, flush=True); return out

if __name__ == '__main__':
    res = []
    if len(sys.argv) > 2 and sys.argv[2] == 'large':             # second batch: larger boards
        for kind in ('generic', 'rowdep'):
            res.append(run(kind, 10, 7, 3, 1, (4, 5, 6, 7)))
        res.append(run('generic', 9, 7, 4, 1, (4, 5, 6, 7)))
        json.dump(dict(results=res), open(sys.argv[1], 'w'), indent=1); sys.exit()
    for kind in ('generic', 'rowdep'):
        for seed in (1, 2):
            res.append(run(kind, 8, 7, 3, seed, (3, 4, 5, 6, 7)))
    for kind in ('generic', 'rowdep'):
        res.append(run(kind, 10, 7, 3, 1, (3, 4, 5, 6, 7)))
    res.append(run('generic', 9, 7, 4, 1, (3, 4, 5, 6, 7)))
    json.dump(dict(results=res), open(sys.argv[1], 'w'), indent=1)
