"""Rank-drop locus over the algebraic closure for the pencil z_w = l_a + w l_b of a pair of forms in the weak unary PHP top
algebra A over F_3 (n = 8).  In degree k, G(w) = G_a + w G_b is the matrix of multiplication by z_w from A_{k-1} to A_k
(rows: basis of A_{k-1}).  Single-element freeness of z_w through degree 3 holds iff rank G(w) = gamma_k - T_k for k = 2, 3.
A pencil's rank at a point w of the closure (including w = infinity, the form l_b) falls below its normal rank rho exactly at
its eigenvalues.  By the Kronecker form, rho = sum(eps) + sum(eta) + k_reg, with eps / eta the right / left minimal indices
and k_reg the total size of the regular part (finite plus infinite eigenvalues with multiplicity).  Block-Toeplitz ranks give
sum(eps) = rank T_d - (d+1) rho once rank T_d - rank T_{d-1} = rho (all eps <= d), and likewise sum(eta) from the left
Toeplitz matrix.  So k_reg, and hence the number of finite eigenvalues, is computed exactly over F_3.  Also records ranks at
the four F_3-points and the six F_9-points (w = a + b i, i^2 = -1).  Usage: --inp JSON --out JSON"""
import json, os, sys
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
inp = sys.argv[sys.argv.index('--inp') + 1]; outp = sys.argv[sys.argv.index('--out') + 1]
sys.argv = [sys.argv[0], '--n', '8', '--K', '3', '--rs', '', '--family', 'random']
exec(open(os.path.join(HERE, 'board_affine.py')).read().split("res = []\nif opt.phis:")[0])
def mult_matrix(Fb, k):
    lin = {(i * n + j,): int(Fb[i, j]) for i in range(P1) for j in range(n) if Fb[i, j]}
    G = np.zeros((len(basis[k - 1]), g[k]), dtype=np.uint8)
    for t, m in enumerate(basis[k - 1]): G[t] = L.normal_form(L.mul({m: 1}, lin) if m else lin, Q[k], g[k])
    return G
def rank_blocks(block_rows, ncols):   # block_rows: list of lists of (column offset, matrix)
    packs = []
    for br in block_rows:
        R = np.zeros((br[0][1].shape[0], ncols), dtype=np.uint8)
        for off, M in br: R[:, off:off + M.shape[1]] = M
        packs.append(L.gf3.pack(R)[0])
    return L.gf3.rref(None, parallel=True, packed=(np.vstack(packs), (ncols + 63) // 64, ncols))[2].shape[0]
def rank(M): return rank_blocks([[(0, M)]], M.shape[1])
def toeplitz(Ga, Gb, d, left):
    m, N = Ga.shape
    if left: return rank_blocks([[(j * N, Ga), ((j + 1) * N, Gb)] for j in range(d + 1)], (d + 2) * N)
    return rank_blocks([[(k * N, Ga)] * (k <= d) + [((k - 1) * N, Gb)] * (k >= 1) for k in range(d + 2)], (d + 1) * N)
d_in = json.load(open(inp)); res = []
for run in d_in['runs']:
    if 'forms' not in run or run['r'] != 2: continue
    Fa, Fb = (np.array(f) for f in run['forms']); rec = dict(trial=run.get('trial'), excess=run['excess'], degrees={})
    W1, T1 = W_trunc(1, 3)
    for k in (2, 3):
        Ga, Gb = mult_matrix(Fa, k), mult_matrix(Fb, k); target = g[k] - T1[k]
        pts = {str(w): rank((Ga.astype(int) + w * Gb) % 3) for w in range(3)}; pts['inf'] = rank(Gb)
        f9 = {}
        for a in range(3):
            for b in (1, 2):
                A_ = (Ga.astype(int) + a * Gb) % 3; B_ = (b * Gb.astype(int)) % 3
                f9[f'{a}+{b}i'] = rank(np.block([[A_, B_], [(-B_) % 3, A_]]).astype(np.uint8)) // 2
        rho = max(list(pts.values()) + list(f9.values()))
        sums = {}
        for left in (False, True):
            prev = 0
            for d in range(0, 8):
                rk = toeplitz(Ga, Gb, d, left)
                if rk - prev == rho: sums['eta' if left else 'eps'] = dict(d=d, rank=rk, sum=rk - (d + 1) * rho); break
                prev = rk
            else: sums['eta' if left else 'eps'] = dict(d=None)
        k_reg = rho - sums['eps']['sum'] - sums['eta']['sum'] if sums['eps']['d'] is not None and sums['eta']['d'] is not None else None
        rec['degrees'][k] = dict(target_rank=target, F3_points=pts, F9_points=f9, rho_lower_bound=rho, minimal_indices=sums,
                                 k_reg=k_reg, infinite=rho - pts['inf'], finite=None if k_reg is None else k_reg - (rho - pts['inf']))
        print(run.get('trial'), k, rec['degrees'][k], flush=True)
    res.append(rec)
json.dump(dict(source=os.path.basename(inp), results=res), open(outp, 'w'), indent=1, default=int)
