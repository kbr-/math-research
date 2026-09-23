"""Local generation of top syzygies for random linear forms in the functional board's top algebra.

For M random row-linear forms l_1..l_M over GF(3) on a board with R rows and N labels, and each
degree s, compares
  rank Phi,  Phi: K_s -> K_(s-1)^M,  w -> (D_j w)_j            (image = targets with a correction)
  dim L,     L = {(z_j): z_j in im D_j, D_j' z_j = D_j z_j'}     (targets consistent with the
                                                                 single and pair syzygies)
Local generation of the degree-s top syzygies holds iff rank Phi = dim L (duality K = G^*).
Reports, for each M, the degrees s <= D where it fails.  Usage: python3 syzygy_locality.py OUT.json
"""
import itertools, json, os, random, sys, time
import numpy as np
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'odd_prime_short_generation_20260923'))
from short_generation import nullspace, gf3
from second_degree_lift import marg_basis
P = 3

class Board:
    def __init__(self, R, N):
        self.R, self.N = R, N
        self.coords = {}
    def full(self, t):                         # full coordinates of t-row injection arrays
        if t not in self.coords:
            idx = {}
            for S in itertools.combinations(range(self.R), t):
                for lab in itertools.permutations(range(self.N), t):
                    idx[(S, lab)] = len(idx)
            self.coords[t] = idx
        return self.coords[t]
    def D(self, f, t):                         # weighted marginal sum, full(t) -> full(t-1)
        src, dst = self.full(t), self.full(t - 1)
        M = np.zeros((len(dst), len(src)), np.int64)
        for (S, lab), c in src.items():
            for x in range(t):
                v = f[S[x]][lab[x]]
                if v:
                    M[dst[(S[:x] + S[x + 1:], lab[:x] + lab[x + 1:])], c] += v
        return M % P
    def Kbasis(self, t):                       # basis of K_t in full coordinates (columns)
        inj, B = marg_basis(self.N, t)
        src = self.full(t); cols = []
        for S in itertools.combinations(range(self.R), t):
            blk = np.zeros((len(src), B.shape[1]), np.int64)
            for k, lab in enumerate(inj): blk[src[(S, lab)], :] = B[k]
            cols.append(blk)
        return np.concatenate(cols, axis=1) % P

def rowspace(Mat):
    """Basis rows of the row space of Mat over GF(3)."""
    if Mat.shape[0] == 0: return Mat
    E, W, piv = gf3.rref(np.ascontiguousarray(Mat.astype(np.uint8)))
    return gf3.unpack(E, W, Mat.shape[1]).astype(np.int64)

def run(R, N, D, M_max, seed):
    t0 = time.time(); rng = random.Random(seed); b = Board(R, N)
    forms = [[[rng.randrange(3) for _ in range(N)] for _ in range(R)] for _ in range(M_max)]
    Kb = {s: b.Kbasis(s) for s in range(1, D + 1)}
    Dop = {(j, t): b.D(forms[j], t) for j in range(M_max) for t in range(1, D + 1)}
    out = dict(rows=R, labels=N, D=D, seed=seed, by_M={})
    first = None
    for M in range(2, M_max + 1):
        res = {}
        for s in range(1, D + 1):
            DK = [(Dop[(j, s)] @ Kb[s]) % P for j in range(M)]          # D_j on K_s, full(s-1) coords
            rank_phi = gf3.rank(np.ascontiguousarray(np.concatenate(DK, axis=0).astype(np.uint8)))
            Bs = [rowspace(X.T) for X in DK]                               # rows span im D_j
            r = [B_.shape[0] for B_ in Bs]
            if s >= 2:
                blocks = []
                off = np.cumsum([0] + r)
                for j, jp in itertools.combinations(range(M), 2):
                    rowblk = np.zeros((Dop[(0, s - 1)].shape[0], off[-1]), np.int64)
                    rowblk[:, off[j]:off[j + 1]] = (Dop[(jp, s - 1)] @ Bs[j].T) % P
                    rowblk[:, off[jp]:off[jp + 1]] = (-(Dop[(j, s - 1)] @ Bs[jp].T)) % P
                    blocks.append(rowblk)
                C = np.concatenate(blocks, axis=0) % P
                dimL = off[-1] - gf3.rank(np.ascontiguousarray(C.astype(np.uint8)))
            else:
                dimL = sum(r)
            res[s] = dict(rank_phi=int(rank_phi), dim_L=int(dimL), local=bool(rank_phi == dimL))
        out['by_M'][M] = res
        bad = [s for s in res if not res[s]['local']]
        print(dict(R=R, N=N, M=M, fails_at=bad, detail={s: (res[s]['rank_phi'], res[s]['dim_L']) for s in res}), flush=True)
        if bad and first is None: first = (M, bad)
        if first and M >= first[0] + 2: break
    out['first_nonlocal'] = first; out['seconds'] = time.time() - t0
    return out

if __name__ == '__main__':
    res = []
    for (R, N, D, Mmax) in ((7, 6, 3, 12), (8, 7, 3, 20)):
        for seed in (1, 2):
            res.append(run(R, N, D, Mmax, seed))
    json.dump(dict(results=res), open(sys.argv[1], 'w'), indent=1)
