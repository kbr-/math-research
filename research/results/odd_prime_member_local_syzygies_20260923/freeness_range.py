"""Range of freeness of G over T = Sym(W)/(cubes) through degree 3, for a random d-dimensional W of linear parts on the
functional top algebra (R = n+1, N = n, GF(3)).  Uses the C(d+1,2) forms A_i and A_i + A_j (A_1..A_d a random basis of W),
whose squares span Sym^2 W.  Freeness through degree 3 forces
   degree 2: rank = C(d+1,2),   degree 3: rank = C(d+1,2)(gamma_1 - d) + C(d+2,3) - d,
and the test reports, for d = 1..dmax, the computed ranks against these free counts (and against min(gamma_t, count)).
Usage: python3 freeness_range.py --n 6 --dmax 12 --seed 1 --out OUT.json"""
import argparse, json, math, os, sys, time
import numpy as np
from scipy import sparse
HERE = os.path.dirname(os.path.abspath(__file__)); RES = os.path.join(HERE, '..')
sys.path.insert(0, os.path.join(RES, 'odd_prime_horace_pieces_20260923'))
from horace_pieces import Board, series
from second_degree_lift import marg_basis
P = 3
def ok(f): return all(len(set(f[x])) > 1 for x in range(f.shape[0]))
ap = argparse.ArgumentParser(); ap.add_argument('--n', type=int, default=6); ap.add_argument('--dmax', type=int, default=12)
ap.add_argument('--seed', type=int, default=1); ap.add_argument('--out', required=True); a = ap.parse_args(); t0 = time.time()
n = a.n; R, N = n + 1, n; b = Board(R, N)
inj2, B2 = marg_basis(N, 2); assert inj2 == b.inj[2]
Kb2 = sparse.kron(sparse.identity(len(b.sets[2]), format='csr', dtype=np.int64), sparse.csr_matrix(B2 % P), format='csc')
g1, g2, g3 = R * (N - 1), Kb2.shape[1], b.Kb.shape[1]; all3 = np.arange(g3)
rng = np.random.default_rng(3000 + a.seed); A = []
# nested sequence: for d = 1..dmax add A_d and A_i + A_d (i < d); prefix after step d spans exactly Sym^2 <A_1..A_d>.
# A_d is resampled until all its new forms are nonconstant on every row (the hypothesis).
forms, ends = [], []
for d in range(a.dmax):
    while True:
        f = rng.integers(0, 3, size=(R, N)); new = [f] + [(A[i] + f) % 3 for i in range(d)]
        if all(ok(g) for g in new): break
    A.append(f); forms += new; ends.append(len(forms))
r2 = series([((b.D(f, 1) @ (b.D(f, 2) @ Kb2)).toarray() % P).astype(np.uint8) for f in forms], g2)
r3 = series([b.D2K(f, all3) for f in forms], g3)
out = dict(n=n, seed=a.seed, gamma1=g1, gamma2=g2, gamma3=g3, rows=[])
for d in range(1, a.dmax + 1):
    e = ends[d - 1] - 1; c2 = math.comb(d + 1, 2); c3 = c2 * (g1 - d) + math.comb(d + 2, 3) - d
    row = dict(d=d, r2=int(r2[e]), free2=c2, r3=int(r3[e]), free3=c3, free=(int(r2[e]) == c2 and int(r3[e]) == c3),
               saturated3=(int(r3[e]) == g3))
    out['rows'].append(row); print(row, flush=True)
json.dump(out, open(a.out, 'w'), indent=1)
