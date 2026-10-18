"""No statement tested: times each step of two_level_chain.run on one sample of 4096 points, to find the slow one."""
import importlib.util, math, time
import numpy as np
from pathlib import Path
from scipy.sparse import csr_matrix, coo_matrix
from scipy.sparse.csgraph import min_weight_full_bipartite_matching

p = Path('research/results/ultimate_matching_two_level_chain_20261018/two_level_chain.py')
s = importlib.util.spec_from_file_location('tl', p); tl = importlib.util.module_from_spec(s); s.loader.exec_module(tl)
bc = tl.bc
t = time.time()
rng = np.random.default_rng(0); N = 4096
X = rng.uniform(0, 1, (N, 2)); g = 64
cells = np.stack(np.meshgrid(np.arange(g), np.arange(g), indexing='ij'), -1).reshape(-1, 2)
Y = (cells + rng.uniform(0, 1, (N, 2))) / g
s1 = math.sqrt(math.log(N) / N)
A1, A2 = bc.graph(X, Y, 0.5 * s1), bc.graph(X, Y, 0.5 * 2 ** 0.25 * s1)
print('graphs', round(time.time() - t, 2), A1.nnz, A2.nnz, flush=True); t = time.time()
rmate, cmate = bc.match(A2); nu2 = int((rmate >= 0).sum())
print('match', round(time.time() - t, 2), nu2, flush=True); t = time.time()
DY = np.nonzero(bc.missable_columns(A2, rmate, cmate))[0]
DX = np.nonzero(bc.missable_columns(A2.T.tocsr(), cmate, rmate))[0]
print('missable', round(time.time() - t, 2), len(DX), len(DY), flush=True); t = time.time()
C = coo_matrix(A2)
in1 = np.asarray(csr_matrix(A1)[C.row, C.col]).ravel() > 0
print('in1', round(time.time() - t, 2), int(in1.sum()), flush=True); t = time.time()
mx, my = N - nu2, N - nu2
rows = [C.row, np.repeat(np.arange(N, N + my), len(DY)), np.tile(DX, mx)]
cols = [C.col, np.tile(DY, my), np.repeat(np.arange(N, N + mx), len(DX))]
w = np.concatenate([np.where(in1, 1.0, 2.0), np.full(my * len(DY), 3.0), np.full(mx * len(DX), 3.0)])
w = w + np.random.default_rng(1).uniform(0, 1e-4, len(w))   # breaks ties; under 0.41 in all over 4096 edges
W = csr_matrix((w, (np.concatenate(rows), np.concatenate(cols))), shape=(N + my, N + mx))
t = time.time()
r, c = min_weight_full_bipartite_matching(W)
ww = np.asarray(W[r, c]).ravel(); real = ww < 2.5
nu1 = int((bc.maximum_bipartite_matching(A1) >= 0).sum())
print('jittered solve', round(time.time() - t, 2), 'real', int(real.sum()), 'e', int((ww[real] > 1.5).sum()), 'd', nu2 - nu1, flush=True)
