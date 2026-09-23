"""Homology hypothesis of the edge Castelnuovo sequence in degree 3: reduced H_1 of the matching complex of the 3 x n
chessboard minus one cell (the row set S = {i, r, s} of Gamma minus e), over GF(3) and Q, for n = 4..10.
H~_1 = dim C_1 - rank d_1 - rank d_2 (faces: cells, 2-matchings, 3-matchings; signs by row order).
Also prints the row-split trace capacity gamma'_3/(gamma'_1 - 1) of the PHP board (R = n+1, N = n) for n = 6..10.
Usage: python3 edge_homology.py --out OUT.json"""
import argparse, itertools, json, math
import numpy as np
from edge_sequence import rank_mod
def homology1(n, field):
    allowed = {0: set(range(n)) - {0}, 1: set(range(n)), 2: set(range(n))}      # row 0 misses label 0
    faces = {k: [] for k in (1, 2, 3)}
    for k in (1, 2, 3):
        for S in itertools.combinations(range(3), k):
            for lab in itertools.product(*[sorted(allowed[r]) for r in S]):
                if len(set(lab)) == k: faces[k].append(tuple(zip(S, lab)))
    idx = {k: {f: j for j, f in enumerate(faces[k])} for k in faces}
    def bd(k):
        M = np.zeros((len(faces[k - 1]), len(faces[k])), np.int64)
        for j, f in enumerate(faces[k]):
            for x in range(k):
                M[idx[k - 1][f[:x] + f[x + 1:]], j] = (-1) ** x
        return M
    rk = (lambda M: rank_mod(M, 3)) if field == 3 else (lambda M: int(np.linalg.matrix_rank(M.astype(float))))
    return len(faces[2]) - rk(bd(2)) - rk(bd(3))
def delta(t, N): return sum((-1) ** j * math.comb(t, j) * math.perm(N, t - j) for j in range(t + 1))
ap = argparse.ArgumentParser(); ap.add_argument('--out', required=True); a = ap.parse_args(); res = []
for n in range(4, 11):
    r = dict(n=n, H1_gf3=homology1(n, 3), H1_Q=homology1(n, 0))
    if n >= 6:
        R, N = n + 1, n; g3t = math.comb(R - 1, 3) * delta(3, N); r['row_trace_capacity'] = round(g3t / ((R - 1) * (N - 1) - 1), 1)
    res.append(r); print(r, flush=True)
json.dump(res, open(a.out, 'w'), indent=1)
