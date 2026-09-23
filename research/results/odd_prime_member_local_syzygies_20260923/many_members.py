"""Many generic members beyond the direct-sum range, on the functional top algebra G (R = n+1, N = n, GF(3)).

Tested statement (the component hypothesis's syzygy conclusion where the Kunneth lemma does not apply): for m members,
each all directions of an independent random subspace of dimension d, with m*d > gamma_1 (so the spans cannot form a
direct sum), the degree-2 and degree-3 ranks stay additive, rank_t = min(gamma_t, m * r_t(one member)), where
r_2 = C(d+1,2) and r_3 = C(d+1,2)(gamma_1 - d) + C(d+2,3) - d; a shortfall below saturation is a syzygy that is not
member-local.  The series is incremental over members (one pass of the compiled prefix kernel per (d, seed)).
Usage: python3 many_members.py --n 6 --d 2 --m 30 --seed 1 --out OUT.json"""
import argparse, itertools, json, math, os, sys, time
import numpy as np
from scipy import sparse
HERE = os.path.dirname(os.path.abspath(__file__)); RES = os.path.join(HERE, '..')
sys.path.insert(0, os.path.join(RES, 'odd_prime_horace_pieces_20260923'))
from horace_pieces import Board, series
from second_degree_lift import marg_basis
P = 3
def ok(f): return all(len(set(f[x])) > 1 for x in range(f.shape[0]))
def dirs(d): return [np.array(c) for c in itertools.product(range(3), repeat=d) if any(c) and c[next(i for i, x in enumerate(c) if x)] == 1]
ap = argparse.ArgumentParser(); ap.add_argument('--n', type=int, default=6); ap.add_argument('--d', type=int, default=2)
ap.add_argument('--m', type=int, default=30); ap.add_argument('--seed', type=int, default=1); ap.add_argument('--out', required=True)
a = ap.parse_args(); n = a.n; R, N = n + 1, n; b = Board(R, N)
inj2, B2 = marg_basis(N, 2); assert inj2 == b.inj[2]
Kb2 = sparse.kron(sparse.identity(len(b.sets[2]), format='csr', dtype=np.int64), sparse.csr_matrix(B2 % P), format='csc')
g1, g2, g3 = R * (N - 1), Kb2.shape[1], b.Kb.shape[1]; all3 = np.arange(g3)
rng = np.random.default_rng(4000 + 97 * a.d + a.seed); forms, ends = [], []
for _ in range(a.m):
    while True:
        A = rng.integers(0, 3, size=(a.d, R, N)); mem = [np.tensordot(c, A, axes=1) % 3 for c in dirs(a.d)]
        if all(ok(f) for f in mem): break
    forms += mem; ends.append(len(forms))
r2 = series([((b.D(f, 1) @ (b.D(f, 2) @ Kb2)).toarray() % P).astype(np.uint8) for f in forms], g2)
r3 = series([b.D2K(f, all3) for f in forms], g3)
c2 = math.comb(a.d + 1, 2); c3 = c2 * (g1 - a.d) + math.comb(a.d + 2, 3) - a.d
rows = [dict(members=k + 1, span_dims=(k + 1) * a.d, r2=int(r2[ends[k] - 1]), pred2=min(g2, (k + 1) * c2),
             r3=int(r3[ends[k] - 1]), pred3=min(g3, (k + 1) * c3)) for k in range(a.m)]
dev = [r['members'] for r in rows if r['r2'] != r['pred2'] or r['r3'] != r['pred3']]
print(f'n={n} d={a.d} seed={a.seed}: members 1..{a.m} (span dims up to {a.m*a.d}, gamma_1={g1}); deviations at member counts {dev}; '
      f'last row {rows[-1]}', flush=True)
json.dump(dict(n=n, d=a.d, seed=a.seed, gamma1=g1, gamma2=g2, gamma3=g3, one_member=[c2, c3], rows=rows, deviations=dev), open(a.out, 'w'), indent=1)
