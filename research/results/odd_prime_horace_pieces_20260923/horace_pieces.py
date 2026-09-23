"""Row Horace pieces on the functional matching complex (R = n+1 rows, N = n labels, GF(3)), degree 3.

Tested statements (lem:row-horace-identity and its corollary): for M uniform random forms l_1..l_M, with row
i = R-1 removed,
  full:     rank of w -> (D_l^2 w)_l on K_3           (capacity law: = min(gamma_3, M(gamma_1 - 1)))
  trace T:  rank of w0 -> (D'_l^2 w0)_l on K'_3        (maximal rank: = min(gamma'_3, M(gamma'_1 - 1)))
  residual: rank of w1 -> (D'_l^2 w1)_l on K^{ni i}_3  ((B): = min(dim K^{ni i}_3, M(N - 1)))
  coupling rank = r_full - r_T - r_res                 ((C): = min(M(gamma'_1-1) - r_T, dim Z_res))
where D'_l is D_l with row i's coefficients zeroed.  Hypothesis asserted: every form is nonconstant (mod
constants) on every row.  All maps are built sparse (scipy, compiled); each rank series is one incremental
elimination in the compiled prefix-rank kernel gf3_prefix.c, every M at once.
Usage: python3 horace_pieces.py --ns 6,7,8 --seed S [--family uniform|function] --out OUT.json
(function: the control family, one cell per row, expected to deviate)"""
import argparse, itertools, json, os, sys, time
import numpy as np
from scipy import sparse
HERE = os.path.dirname(os.path.abspath(__file__)); RES = os.path.join(HERE, '..')
sys.path.insert(0, os.path.join(RES, 'odd_prime_permutation_forms_20260923'))
sys.path.insert(0, os.path.join(RES, 'odd_prime_short_generation_20260923'))
sys.path.insert(0, os.path.join(RES, 'odd_prime_alignment_mechanism_20260922'))
import gf3
from gf3_prefix import prefix_ranks
from second_degree_lift import marg_basis
P = 3
class Board:
    def __init__(self, R, N):
        self.R, self.N = R, N
        self.sets = {t: list(itertools.combinations(range(R), t)) for t in range(0, 4)}
        self.inj = {t: list(itertools.permutations(range(N), t)) for t in range(0, 4)}
        self.sidx = {t: {S: k for k, S in enumerate(self.sets[t])} for t in self.sets}
        self.iidx = {t: {s: k for k, s in enumerate(self.inj[t])} for t in self.inj}
        self.nfull = {t: len(self.sets[t]) * len(self.inj[t]) for t in self.sets}
        self.struct = {}
        for t in (1, 2, 3):                              # D structure full(t) -> full(t-1): src, dst, row, label
            src, dst, row, lab = [], [], [], []
            ni, nl = len(self.inj[t]), len(self.inj[t - 1])
            for a, S in enumerate(self.sets[t]):
                for b, s in enumerate(self.inj[t]):
                    for x in range(t):
                        S2 = S[:x] + S[x + 1:]; s2 = s[:x] + s[x + 1:]
                        src.append(a * ni + b); dst.append(self.sidx[t - 1][S2] * nl + self.iidx[t - 1][s2])
                        row.append(S[x]); lab.append(s[x])
            self.struct[t] = tuple(np.array(v, dtype=np.int64) for v in (src, dst, row, lab))
        inj3, B = marg_basis(N, 3)                       # local basis of one 3-set, same ordering as self.inj[3]
        assert inj3 == self.inj[3]
        self.delta3 = B.shape[1]
        self.Kb = sparse.kron(sparse.identity(len(self.sets[3]), format='csr', dtype=np.int64),
                              sparse.csr_matrix(B % P), format='csc')
        self.block_of_col = np.repeat(np.arange(len(self.sets[3])), self.delta3)
    def D(self, form, t):
        src, dst, row, lab = self.struct[t]; v = form[row, lab] % P; nz = v != 0
        return sparse.csr_matrix((v[nz], (dst[nz], src[nz])), shape=(self.nfull[t - 1], self.nfull[t]))
    def D2K(self, form, cols):
        X = (self.D(form, 2) @ (self.D(form, 3) @ self.Kb[:, cols])).toarray() % P
        return X.astype(np.uint8)
def series(blocks, cols):
    P_, W = gf3.pack(np.vstack(blocks))[:2]
    return prefix_ranks(np.ascontiguousarray(P_, dtype=np.uint64), W, cols, np.cumsum([b.shape[0] for b in blocks]).tolist())
def run(n, seed, t0, family='uniform'):
    R, N = n + 1, n; b = Board(R, N); i = R - 1
    contains = np.array([i in S for S in b.sets[3]])
    colsT = np.nonzero(~contains[b.block_of_col])[0]; colsR = np.nonzero(contains[b.block_of_col])[0]
    g3, g3T, kR = b.Kb.shape[1], len(colsT), len(colsR); g1, g1T = R * (N - 1), (R - 1) * (N - 1)
    cap = g3 / (g1 - 1); Mmax = int(1.15 * cap) + 2
    rng = np.random.default_rng(seed); forms = []
    while len(forms) < Mmax:
        if family == 'uniform':
            f = rng.integers(0, 3, size=(R, N))
        else:                                                                # control: one cell per row
            f = np.zeros((R, N), dtype=np.int64); f[np.arange(R), rng.integers(0, N, size=R)] = rng.integers(1, 3, size=R)
        if all(len(set(f[x])) > 1 for x in range(R)): forms.append(f)      # nonconstant on every row
    allc = np.arange(g3)
    full = series([b.D2K(f, allc) for f in forms], g3)
    fz = [f.copy() for f in forms]
    for f in fz: f[i, :] = 0                                                 # D' = D with row i zeroed
    trace = series([b.D2K(f, colsT) for f in fz], g3T)
    resid = series([b.D2K(f, colsR) for f in fz], kR)
    rows = []
    for M in range(1, Mmax + 1):
        rF, rT, rR = full[M - 1], trace[M - 1], resid[M - 1]
        coup = rF - rT - rR; e = M * (g1T - 1) - rT; zres = kR - rR
        rows.append(dict(M=M, full=rF, full_exp=min(g3, M * (g1 - 1)), trace=rT, trace_exp=min(g3T, M * (g1T - 1)),
                         resid=rR, resid_exp=min(kR, M * (N - 1)), coupling=coup, coupling_exp=min(max(e, 0), zres)))
    bad = {k: [r['M'] for r in rows if r[k] != r[k + '_exp']] for k in ('full', 'trace', 'resid', 'coupling')}
    print(f'{family} n={n}: gamma3={g3} trace={g3T} residual={kR} capacity={cap:.1f} Mmax={Mmax}; deviations (M lists):',
          {k: (v[:8], len(v)) for k, v in bad.items()}, f'({time.time()-t0:.0f}s)', flush=True)
    return dict(n=n, R=R, N=N, seed=seed, family=family, gamma3=g3, gamma3_trace=g3T, dim_residual=kR, gamma1=g1, gamma1_trace=g1T,
                capacity=cap, rows=rows, deviations=bad)
if __name__ == '__main__':
    ap = argparse.ArgumentParser(); ap.add_argument('--ns', default='6,7'); ap.add_argument('--seed', type=int, default=1)
    ap.add_argument('--family', default='uniform'); ap.add_argument('--out'); a = ap.parse_args(); t0 = time.time(); out = []
    for n in map(int, a.ns.split(',')):
        out.append(run(n, a.seed, t0, a.family))
        if a.out: json.dump(dict(results=out), open(a.out, 'w'), indent=1)
