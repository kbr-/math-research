"""Lead check, continued: where the zero-marginal dimension exceeds delta_t(N), is the excess 3-torsion?
Compares dim over GF(3) (marg_basis) with dim over Q (exact integer rank via float SVD rank of the 0/1 matrix,
cross-checked by rank mod the prime 10007).  A difference means integral homology of the chessboard complex
M_{t,N} below the top has 3-torsion that the GF(3) spaces see (the Shareshian-Wachs phenomenon).
Usage: python3 chessboard_torsion.py --out OUT.json"""
import argparse, itertools, json, math, os, sys
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', 'odd_prime_short_generation_20260923'))
from second_degree_lift import marg_basis
def marg_matrix(N, s):
    inj = list(itertools.permutations(range(N), s)); low = list(itertools.permutations(range(N), s - 1))
    lp = {t: k for k, t in enumerate(low)}; M = np.zeros((s * len(low), len(inj)), np.int64)
    for k, t in enumerate(inj):
        for x in range(s):
            M[x * len(low) + lp[t[:x] + t[x + 1:]], k] = 1
    return M
def rank_mod(M, p):
    A = M % p; r = 0; rows, cols = A.shape
    for c in range(cols):
        piv = np.nonzero(A[r:, c])[0]
        if len(piv) == 0: continue
        k = r + piv[0]; A[[r, k]] = A[[k, r]]
        A[r] = A[r] * pow(int(A[r, c]), p - 2, p) % p
        nz = np.nonzero(A[:, c])[0]; nz = nz[nz != r]
        A[nz] = (A[nz] - np.outer(A[nz, c], A[r])) % p
        r += 1
        if r == rows: break
    return r
def delta(t, N):
    return sum((-1) ** j * math.comb(t, j) * math.perm(N, t - j) for j in range(t + 1))
ap = argparse.ArgumentParser(); ap.add_argument('--out', required=True); a = ap.parse_args(); rows = []
for t, N in ((3, 4), (4, 5), (4, 6), (5, 6), (5, 7)):
    M = marg_matrix(N, t); cols = M.shape[1]
    d3 = marg_basis(N, t)[1].shape[1]; dq = cols - np.linalg.matrix_rank(M.astype(float)); dp = cols - rank_mod(M, 10007)
    rows.append(dict(t=t, N=N, dim_gf3=int(d3), dim_Q=int(dq), dim_gf10007=int(dp), delta=delta(t, N)))
    print(rows[-1], flush=True)
json.dump(rows, open(a.out, 'w'), indent=1)
