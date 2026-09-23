"""Overlapping members on the functional top algebra G (R = n+1, N = n, GF(3)), degrees 2 and 3.

Two members U1, U2 = all directions of subspaces W1, W2 of linear parts with dim W1 = d1, dim W2 = d2 and a shared
subspace of dimension k (random otherwise); S = U1 cap U2 = the directions of the shared subspace.  Tested statement
(member-locality for the given members): ker mu_{U1 cup U2} = ker mu_{U1} + ker mu_{U2}, i.e. in each degree
   rank(U1 cup U2) = rank(U1) + rank(U2) - rank(S).
Predicted to FAIL for k >= 1 by the identity (ab)c = (ac)b across the members, which would make the span of the
union, not the given members, the unit of locality.  Also reported: the ranks of all directions of W1 + W2 (the span
closure), and the rank after M_rand random forms appended to U1 cup U2, compared with min(gamma, rank + M_rand(gamma_1-1)).
Usage: python3 overlap.py --n 6 --seed 1 --Mrand 40 --out OUT.json"""
import argparse, itertools, json, os, sys, time
import numpy as np
from scipy import sparse
HERE = os.path.dirname(os.path.abspath(__file__)); RES = os.path.join(HERE, '..')
sys.path.insert(0, os.path.join(RES, 'odd_prime_horace_pieces_20260923'))
from horace_pieces import Board, series
from second_degree_lift import marg_basis
from freeness import predict
P = 3
def ok(f): return all(len(set(f[x])) > 1 for x in range(f.shape[0]))
def dirs(d):
    return [np.array(c) for c in itertools.product(range(3), repeat=d) if any(c) and c[next(i for i, x in enumerate(c) if x)] == 1]
ap = argparse.ArgumentParser(); ap.add_argument('--n', type=int, default=6); ap.add_argument('--seed', type=int, default=1)
ap.add_argument('--Mrand', type=int, default=40); ap.add_argument('--out', required=True); a = ap.parse_args(); t0 = time.time()
n = a.n; R, N = n + 1, n; b = Board(R, N)
inj2, B2 = marg_basis(N, 2); assert inj2 == b.inj[2]
Kb2 = sparse.kron(sparse.identity(len(b.sets[2]), format='csr', dtype=np.int64), sparse.csr_matrix(B2 % P), format='csc')
g1, g2, g3 = R * (N - 1), Kb2.shape[1], b.Kb.shape[1]; all3 = np.arange(g3)
def blk2(f): return ((b.D(f, 1) @ (b.D(f, 2) @ Kb2)).toarray() % P).astype(np.uint8)
def blk3(f): return b.D2K(f, all3)
def ranks(forms): return [int(x) for x in series([blk2(f) for f in forms], g2)], [int(x) for x in series([blk3(f) for f in forms], g3)]
rng = np.random.default_rng(2000 + a.seed); rand = []
while len(rand) < a.Mrand:
    f = rng.integers(0, 3, size=(R, N))
    if ok(f): rand.append(f)
out = dict(n=n, seed=a.seed, gamma1=g1, gamma2=g2, gamma3=g3, runs=[])
for d1, d2, k in [(2, 2, 1), (3, 3, 1), (3, 3, 2), (2, 3, 1), (2, 2, 0), (3, 3, 0)]:
    while True:
        Bv = rng.integers(0, 3, size=(d1 + d2 - k, R, N))
        E1 = list(range(d1)); E2 = list(range(k)) + list(range(d1, d1 + d2 - k))
        comb = lambda c, E: np.tensordot(c, Bv[E], axes=1) % 3
        U1 = [comb(c, E1) for c in dirs(d1)]; U2 = [comb(c, E2) for c in dirs(d2)]
        S = [comb(c, list(range(k))) for c in dirs(k)] if k else []
        key = lambda f: f.tobytes(); seen = {key(f) for f in U1}; U = U1 + [f for f in U2 if key(f) not in seen]
        span = [comb(c, list(range(d1 + d2 - k))) for c in dirs(d1 + d2 - k)] if d1 + d2 - k <= 4 else []   # closure only when small
        if all(ok(f) for f in U + span): break
    assert len(U) == len(U1) + len(U2) - len(S)
    r1, r2_, rS = ranks(U1), ranks(U2), (ranks(S) if S else ([0], [0])); rspan = ranks(span) if span else ([None], [None])
    dd = d1 + d2 - k; coords = lambda c, E: [int(c[E.index(t)]) if t in E else 0 for t in range(dd)]
    fv = [coords(c, E1) for c in dirs(d1)] + [coords(c, E2) for c in dirs(d2)]     # duplicates do not change the spans
    fp = list(predict(fv, dd, g1))
    rU = ranks(U + rand); kU = len(U)
    pred = [r1[t][-1] + r2_[t][-1] - rS[t][-1] for t in (0, 1)]
    got = [rU[0][kU - 1], rU[1][kU - 1]]
    dev3 = [M for M in range(a.Mrand + 1) if rU[1][kU - 1 + M] != min(g3, got[1] + M * (g1 - 1))]
    dev2 = [M for M in range(a.Mrand + 1) if rU[0][kU - 1 + M] != min(g2, got[0] + M)]
    run = dict(d1=d1, d2=d2, k=k, sizes=[len(U1), len(U2), len(S), len(U)], rank_U1=[r1[0][-1], r1[1][-1]], rank_U2=[r2_[0][-1], r2_[1][-1]],
               rank_S=[rS[0][-1], rS[1][-1]], local_prediction=pred, rank_union=got, local=(pred == got), freeness_prediction=fp, freeness_ok=(fp == got),
               rank_span_closure=[rspan[0][-1], rspan[1][-1]], span_closure_size=len(span), random_dev2=dev2, random_dev3=dev3)
    out['runs'].append(run)
    print(f'd1={d1} d2={d2} shared k={k}: sizes {run["sizes"]}; union ranks (deg2, deg3) {got} vs local prediction {pred} '
          f'(local {run["local"]}); freeness prediction {fp}; span closure ({len(span)} forms) ranks {run["rank_span_closure"]}; random appended: '
          f'deviations deg2 {len(dev2)}, deg3 {len(dev3)} ({time.time()-t0:.0f}s)', flush=True)
json.dump(out, open(a.out, 'w'), indent=1)
