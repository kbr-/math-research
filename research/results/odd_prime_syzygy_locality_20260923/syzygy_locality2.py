"""Which subsystems generate the top syzygies of random linear forms in the functional board's top algebra.

For M row-linear forms l_1..l_M over GF(3) on a board with R rows and N labels, pairwise full
(1, l_a, l_b independent on every row), and each degree s <= D, compares
  rank Phi,  Phi: K_s -> K_(s-1)^M, w -> (D_j w)_j   (targets with one correction; dual to all syzygies)
  dim L_k,   targets whose restriction to every k-subset of forms has a correction
             (dual to the syzygies supported on k-subsets), k = 2, 3
  dim L_kos, targets with z_j in im D_j and D_j' z_j = D_j z_j' (dual to single and Koszul syzygies)
imPhi <= L_3 <= L_2 <= L_kos.  Syzygies of degree s are generated on k-subsets iff rank Phi = dim L_k.
Also counts pairs whose own targets are not Koszul-complete (pair lift fails on this board).
Usage: python3 syzygy_locality2.py OUT.json R N D M_MAX SEED [SEED ...]
"""
import itertools, json, os, random, sys, time
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', 'odd_prime_short_generation_20260923'))
sys.path.insert(0, HERE)
from short_generation import nullspace, gf3
from syzygy_locality import Board
P = 3

def rank(A):
    return 0 if A.size == 0 else gf3.rank(np.ascontiguousarray((A % P).astype(np.uint8)))

def pivots(A):
    """Pivot columns of the RREF of A (rows = vectors)."""
    E, W, piv = gf3.rref(np.ascontiguousarray((A % P).astype(np.uint8)), full=True)
    return list(piv)

def full_rank_rows(vecs, N):
    return rank(np.array(vecs, np.int64)) == len(vecs)

def pairwise_full_forms(R, N, M, rng):
    forms = []
    while len(forms) < M:
        f = [[rng.randrange(3) for _ in range(N)] for _ in range(R)]
        if all(full_rank_rows([[1] * N, f[i]], N) for i in range(R)) and \
           all(full_rank_rows([[1] * N, f[i], g[i]], N) for g in forms for i in range(R)):
            forms.append(f)
    return forms

def local_dim(A, off, subsets):
    """dim of {a : a restricted to U lies in colspace(A_U) for every U}; A = stacked coordinates."""
    rows = []
    for U in subsets:
        idx = np.concatenate([np.arange(off[j], off[j + 1]) for j in U])
        Y = nullspace(A[idx, :].T)                           # columns y with y^T A_U = 0
        if Y.shape[1] == 0: continue
        blk = np.zeros((Y.shape[1], off[-1]), np.int64); blk[:, idx] = Y.T
        rows.append(blk)
    return off[-1] - (rank(np.concatenate(rows)) if rows else 0)

def run(R, N, D, M_max, seed):
    t0 = time.time(); rng = random.Random(seed); b = Board(R, N)
    forms = pairwise_full_forms(R, N, M_max, rng)
    Kb = {s: b.Kbasis(s) for s in range(1, D + 1)}
    Dop = {(j, t): b.D(forms[j], t) for j in range(M_max) for t in range(1, D + 1)}
    out = dict(rows=R, labels=N, D=D, seed=seed, forms=forms, dimK={s: int(Kb[s].shape[1]) for s in Kb}, by_M={})
    first = {}
    for M in range(2, M_max + 1):
        jfull = all(full_rank_rows([[1] * N] + [forms[j][i] for j in range(M)], N) for i in range(R))
        res = {}
        for s in range(1, D + 1):
            DK = [(Dop[(j, s)] @ Kb[s]) % P for j in range(M)]
            pv = [pivots(X.T) for X in DK]
            A = np.concatenate([DK[j][pv[j], :] for j in range(M)])   # coordinates of D_j w in im D_j
            r = [len(p) for p in pv]; off = np.cumsum([0] + r)
            rank_phi = rank(A)
            pairs = list(itertools.combinations(range(M), 2))
            L2 = local_dim(A, off, pairs)
            if s >= 2:
                blocks = []; incomplete = 0
                for j, jp in pairs:
                    rowblk = np.zeros((Dop[(0, s - 1)].shape[0], off[-1]), np.int64)
                    # z_j = DK_j w has pivot coordinates a_j; recover z_j from a_j via a basis of im D_j
                    rowblk[:, off[j]:off[j + 1]] = (Dop[(jp, s - 1)] @ basis_from_pivots(DK[j], pv[j])) % P
                    rowblk[:, off[jp]:off[jp + 1]] = (-(Dop[(j, s - 1)] @ basis_from_pivots(DK[jp], pv[jp]))) % P
                    blocks.append(rowblk)
                    kos_pair = r[j] + r[jp] - rank(rowblk[:, np.r_[off[j]:off[j + 1], off[jp]:off[jp + 1]]])
                    if kos_pair != rank(A[np.r_[off[j]:off[j + 1], off[jp]:off[jp + 1]], :]): incomplete += 1
                Lkos = off[-1] - rank(np.concatenate(blocks))
            else:
                Lkos, incomplete = off[-1], 0
            L3 = local_dim(A, off, list(itertools.combinations(range(M), 3))) if (M >= 4 and L2 != rank_phi) else None
            res[s] = dict(rank_phi=int(rank_phi), L3=None if L3 is None else int(L3), L2=int(L2),
                          Lkos=int(Lkos), incomplete_pairs=incomplete)
            for key, val in (('kos', Lkos), ('pair', L2)):
                if val != rank_phi and key not in first: first[key] = (M, s)
            if L3 is not None and L3 != rank_phi and 'triple' not in first: first['triple'] = (M, s)
        out['by_M'][M] = dict(jointly_full=jfull, degrees=res)
        print(dict(R=R, N=N, seed=seed, M=M, jointly_full=jfull,
                   d={s: (v['rank_phi'], v['L3'], v['L2'], v['Lkos'], v['incomplete_pairs']) for s, v in res.items()},
                   sec=round(time.time() - t0)), flush=True)
        if 'pair' in first and M >= first['pair'][0] + 2: break
    out['first_nonlocal'] = first; out['seconds'] = time.time() - t0
    return out

def basis_from_pivots(DKj, piv):
    """Columns z in full(s-1) coordinates with pivot coordinates the unit vectors: z = E^T e."""
    E, W, pv = gf3.rref(np.ascontiguousarray(DKj.T.astype(np.uint8) % P), full=True)
    U = gf3.unpack(E, W, DKj.shape[0]).astype(np.int64)[:len(pv)]
    assert list(pv) == list(piv)
    return U.T

if __name__ == '__main__':
    outp, R, N, D, Mmax = sys.argv[1], *map(int, sys.argv[2:6])
    res = [run(R, N, D, Mmax, int(sd)) for sd in sys.argv[6:]]
    json.dump(dict(results=res), open(outp, 'w'), indent=1)
