"""Degree-4 glue check on the functional board (R = n+1 rows, N = n labels, GF(3)).

Tested statement (degree-4 glued theorem): if the selectors' linear parts l_j satisfy (a) squares independent in G_2,
(b) degree-3 syzygies of the squares only Frobenius (rank of w -> (D_l^2 w) on K_3 is M(gamma_1 - 1)), and (b4) the
degree-4 syzygies (kernel of (g_j) -> sum l_j^2 g_j on (+)G_2) spanned by the Frobenius syzygies l_j G_1 e_j and the
Koszul pairs l_k^2 e_j - l_j^2 e_k, then functional PHP plus the selectors has no degree-4 PC refutation.
For one uniform F_3 sequence (forms nonconstant on every row), for every prefix M: (a), (b), (b4) [dim ker = M gamma_2 -
rank(mu_4) compared with the rank of the Frobenius and Koszul generators], and whether the degree-4 closure (FSpace,
all-C kernel) contains 1.  Ranks by the compiled prefix-rank kernel, one incremental pass per series.
Usage: python3 deg4_check.py --n 7 --Mmax 30 --seed S --out OUT.json"""
import argparse, itertools, json, os, sys, time
import numpy as np
from scipy import sparse
HERE = os.path.dirname(os.path.abspath(__file__)); RES = os.path.join(HERE, '..'); sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(RES, 'odd_prime_permutation_forms_20260923')); sys.path.insert(0, os.path.join(RES, 'odd_prime_short_generation_20260923'))
sys.path.insert(0, os.path.join(RES, 'odd_prime_local_falls_20260923')); sys.path.insert(0, os.path.join(RES, 'odd_prime_alignment_mechanism_20260922'))
import gf3
from gf3_prefix import prefix_ranks
from second_degree_lift import marg_basis
from fspace import FSpace, base_rows, Closure
from local_falls import random_eq, sel
def series(blocks, cols):
    P_, W = gf3.pack(np.vstack(blocks))[:2]
    return prefix_ranks(np.ascontiguousarray(P_, dtype=np.uint64), W, cols, np.cumsum([b.shape[0] for b in blocks]).tolist())
def rank_rows(A, base):                          # rank each row of a small int array as a base-`base` integer
    return (A * base ** np.arange(A.shape[1] - 1, -1, -1)).sum(axis=1) if A.shape[1] else np.zeros(len(A), dtype=np.int64)
class Board:
    """Matching complex of the complete board, t <= T.  D-structures built by numpy index arithmetic, no Python loops
    over faces: the face (S, s) minus its x-th row is located through a lookup table on base-R / base-N codes."""
    def __init__(self, R, N, T=4):
        arr = lambda it: (lambda L: np.array(L, dtype=np.int64).reshape(len(L), -1) if L and L[0] else np.zeros((len(L), 0), dtype=np.int64))(list(it))
        self.sets = {t: arr(itertools.combinations(range(R), t)) for t in range(T + 1)}
        self.inj = {t: arr(itertools.permutations(range(N), t)) for t in range(T + 1)}
        look_s = {t: np.full(R ** t, -1, dtype=np.int64) for t in range(T + 1)}; look_i = {t: np.full(N ** t, -1, dtype=np.int64) for t in range(T + 1)}
        for t in range(T + 1):
            look_s[t][rank_rows(self.sets[t], R)] = np.arange(len(self.sets[t])); look_i[t][rank_rows(self.inj[t], N)] = np.arange(len(self.inj[t]))
        self.nfull = {t: len(self.sets[t]) * len(self.inj[t]) for t in self.sets}; self.struct = {}
        for t in range(1, T + 1):
            S, I = self.sets[t], self.inj[t]; ns, ni, nl = len(S), len(I), len(self.inj[t - 1])
            src, dst, row, lab = [], [], [], []
            for x in range(t):                                   # t <= 4 iterations; everything inside is vectorized
                a_ = look_s[t - 1][rank_rows(np.delete(S, x, axis=1), R)]; b_ = look_i[t - 1][rank_rows(np.delete(I, x, axis=1), N)]
                src.append((np.arange(ns)[:, None] * ni + np.arange(ni)[None, :]).ravel())
                dst.append((a_[:, None] * nl + b_[None, :]).ravel())
                row.append(np.repeat(S[:, x], ni)); lab.append(np.tile(I[:, x], ns))
            self.struct[t] = tuple(np.concatenate(v) for v in (src, dst, row, lab))
        self.Kb = {}
        for t in (2, 3, 4):
            inj, B = marg_basis(N, t); assert [tuple(r) for r in self.inj[t]] == inj
            self.Kb[t] = sparse.kron(sparse.identity(len(self.sets[t]), format='csr', dtype=np.int64), sparse.csr_matrix(B % 3), format='csc')
    def D(self, f, t):
        src, dst, row, lab = self.struct[t]; v = f[row, lab] % 3; nz = v != 0
        return sparse.csr_matrix((v[nz], (dst[nz], src[nz])), shape=(self.nfull[t - 1], self.nfull[t]))
    def dd(self, f, g, t):                     # D_g D_f on the K_t basis, dense uint8
        return ((self.D(g, t - 1) @ (self.D(f, t) @ self.Kb[t])).toarray() % 3).astype(np.uint8)
    def d1(self, f, t):                        # D_f on the K_t basis, into full (t-1)-coordinates
        return ((self.D(f, t) @ self.Kb[t]).toarray() % 3).astype(np.uint8)
ap = argparse.ArgumentParser(); ap.add_argument('--n', type=int, default=7); ap.add_argument('--Mmax', type=int, default=30)
ap.add_argument('--seed', type=int, default=1); ap.add_argument('--ranks-only', action='store_true'); ap.add_argument('--out', required=True); a = ap.parse_args(); t0 = time.time()
n = a.n; R, N = n + 1, n; b = Board(R, N); g2, g3, g4 = (b.Kb[t].shape[1] for t in (2, 3, 4)); g1 = R * (N - 1)
rng = np.random.default_rng(900 + a.seed); forms = []; v = n * (n + 1)
while len(forms) < a.Mmax:
    L = random_eq(rng, v); arr = np.zeros((R, N), dtype=np.int64)
    for m, c in L.items():
        if m: arr[m[0] // n, m[0] % n] = c
    if all(len(set(arr[x])) > 1 for x in range(R)): forms.append((L, arr))
sq = [b.dd(arr, arr, 2) for _, arr in forms]                                  # l_j^2 as a functional on K_2 (1 x g2)
ra = series(sq, g2)
rb = series([b.dd(arr, arr, 3) for _, arr in forms], g3)
r4 = series([b.dd(arr, arr, 4) for _, arr in forms], g4)
print(f'n={n}: gamma1..4 = {g1},{g2},{g3},{g4}; ranks done ({time.time()-t0:.0f}s)', flush=True)
blocks = []
for j, (_, arr) in enumerate(forms):
    # Frobenius l_j * x_{r,c} for every cell: the rows of D_{l_j} on the K_2 basis, indexed by the 1-faces (r, c)
    frob = b.d1(arr, 2); kos = np.array([sq[k][0] for k in range(j)], dtype=np.uint8).reshape(-1, g2)
    Z = np.zeros((frob.shape[0] + len(kos), a.Mmax * g2), dtype=np.uint8)
    Z[:frob.shape[0], j * g2:(j + 1) * g2] = frob
    if len(kos):                                                                # Koszul l_k^2 e_j - l_j^2 e_k, k < j
        Z[frob.shape[0]:, j * g2:(j + 1) * g2] = kos
        for k in range(j): Z[frob.shape[0] + k, k * g2:(k + 1) * g2] = (3 - sq[j][0]) % 3
    blocks.append(Z)
rg = series(blocks, a.Mmax * g2)
print(f'generators done ({time.time()-t0:.0f}s)', flush=True)
if a.ranks_only:
    json.dump(dict(n=n, seed=a.seed, a=ra, b=rb, rank4=r4, gens4=rg), open(a.out, 'w')); print('ranks', r4[:20], 'gens', rg[:20]); sys.exit(0)
sp = FSpace(n, 4); C = Closure(sp, 14); C.add(base_rows(n)); base = C.split(); out = []
for M in range(1, a.Mmax + 1):
    tM = time.time(); C.add([sel(forms[M - 1][0])]); s = C.split()
    ker4 = M * g2 - r4[M - 1]
    row = dict(M=M, a=bool(ra[M - 1] == M), b=bool(rb[M - 1] == M * (g1 - 1)), ker4=int(ker4), gens4=int(rg[M - 1]),
               b4=bool(ker4 == rg[M - 1]), rank4=int(r4[M - 1]), closure_s=round(time.time() - tM, 1), **s)
    out.append(row); print(row, flush=True)
    if s['refuted']: break
hyp = [r['M'] for r in out if r['a'] and r['b'] and r['b4']]
res = dict(n=n, seed=a.seed, gammas=[g1, g2, g3, g4], base=base, rows=out, last_M_with_hypotheses=max(hyp) if hyp else None,
           first_refuted_M=next((r['M'] for r in out if r['refuted']), None))
res['prediction_holds'] = res['first_refuted_M'] is None or not hyp or res['first_refuted_M'] > max(hyp)
json.dump(res, open(a.out, 'w'), indent=1)
print(f'hypotheses hold up to {res["last_M_with_hypotheses"]}; first refuted {res["first_refuted_M"]}; prediction holds {res["prediction_holds"]} ({time.time()-t0:.0f}s)', flush=True)
