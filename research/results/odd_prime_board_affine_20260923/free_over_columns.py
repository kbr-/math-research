"""Is A (weak unary PHP top algebra, n = 8, F_3) free through degree 3 over the column-sum subalgebra model
R = F_3[t_1..t_n]/(t_j^2, sum t_j), t_j -> C_j = sum_i x_ij?  Graded Nakayama: iff dim(A/(C_1..C_n)A)_k = [t^k] HS_A/HS_R for
k <= 3 (this includes injectivity of R -> A through degree 3).  HS_R from model_pair_n8.json.  Usage: --out"""
import json, os, sys
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); outp = sys.argv[sys.argv.index('--out') + 1]
sys.argv = [sys.argv[0], '--n', '8', '--K', '3', '--rs', '', '--family', 'random']
exec(open(os.path.join(HERE, 'board_affine.py')).read().split("res = []\nif opt.phis:")[0])
HR = json.load(open(os.path.join(HERE, 'model_pair_n8.json')))['HR']; gA = [g[k] for k in range(4)]
V = []
for k in range(4): V.append(gA[k] - sum(HR[i] * V[k - i] for i in range(1, k + 1)))
F = [np.tile(np.eye(n, dtype=np.int64)[j], (P1, 1)) for j in range(n)]
H = hilbert(F); print(dict(HS_A=gA, HS_R=HR[:4], quotient=H, HS_A_over_HS_R=V, free_through_3=H == V), flush=True)
json.dump(dict(HS_A=gA, HS_R=HR[:4], quotient=H, HS_A_over_HS_R=V, free_through_3=H == V), open(outp, 'w'), indent=1)
