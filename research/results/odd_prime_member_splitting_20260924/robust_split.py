"""Separating 'column-type members never split' from 'robust joint spans split' (weak unary PHP top algebra, F_3).

At n = 9 a column span of dimension 3 exists whose 13 directions all have column count c >= 5 (4-robust); hole functions
phi_1, phi_2, phi_3 below (found by random search).  Tested statement (tensor splitting, Tor_0 prediction), through degree 3:
  (i)  members P = {l_1, l_2}, P' = {l_3}: HS(A/(P,P')A) = HS(A/PA) HS(A/P'A) / HS_A;
  (ii) the whole span as one member S, then k = 1..4 random forms: HS(A/(S, r_1..r_k)A) = HS(A/SA)/(1+q+q^2)^k.
Also reported: whether S itself is free (HS(A/SA) against HS_A/(1+q+q^2)^3).  One incremental pass per series; rows are
normal forms (a4lib), ranks by the compiled prefix kernel.  Usage: python3 robust_split.py --seed 1 --out OUT.json"""
import json, os, sys, time, itertools
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); RES = os.path.join(HERE, '..'); BA = os.path.join(RES, 'odd_prime_board_affine_20260923')
a = dict(zip(sys.argv[1::2], sys.argv[2::2])); sd = int(a['--seed']); outp = a['--out']
sys.argv = [sys.argv[0], '--n', '9', '--K', '3', '--rs', '', '--family', 'random']
t0 = time.time(); exec(open(os.path.join(BA, 'board_affine.py')).read().split("res = []\nif opt.phis:")[0])
sys.path.insert(0, os.path.join(RES, 'odd_prime_permutation_forms_20260923')); from gf3_prefix import prefix_ranks
print('setup', [g[t] for t in (1, 2, 3)], f'({time.time()-t0:.0f}s)', flush=True)
PHI = np.array([[0, 2, 0, 2, 0, 2, 2, 1, 0], [2, 0, 2, 2, 1, 1, 0, 0, 1], [2, 1, 0, 2, 0, 2, 0, 0, 2]])
dirs = [np.array(c) for c in itertools.product(range(3), repeat=3) if any(c) and c[next(i for i, x in enumerate(c) if x)] == 1]
minc = min(n - np.bincount((u @ PHI) % 3, minlength=3).max() for u in dirs); assert minc >= 5, minc
def rows_for(F, t):
    lin = {(i * n + j,): int(F[i, j]) for i in range(P1) for j in range(n) if F[i, j] % 3}
    R_ = np.zeros((len(basis[t - 1]), g[t]), dtype=np.uint8)
    for r_, m in enumerate(basis[t - 1]): R_[r_] = L.normal_form(L.mul({m: 1}, lin) if m else lin, Q[t], g[t]) % 3
    return R_
cols = [np.tile(PHI[b], (P1, 1)) for b in range(3)]
rng2 = np.random.default_rng(1100 + sd); rand = [rng2.integers(0, 3, size=(P1, n)) for _ in range(4)]
def series(blocks, t):
    P_, W_ = L.gf3.pack(np.vstack(blocks))[:2]
    return [g[t] - int(x) for x in prefix_ranks(np.ascontiguousarray(P_, dtype=np.uint64), W_, g[t], np.cumsum([b.shape[0] for b in blocks]).tolist())]
H_main, H_third = {}, {}
for t in (1, 2, 3):
    R = [rows_for(F, t) for F in cols + rand]
    H_main[t] = series(R, t)                      # after l1, l2 (=P), l3 (=S), then randoms
    H_third[t] = series([R[2]], t)[0]             # A/(l3)
    print('degree', t, H_main[t], H_third[t], f'({time.time()-t0:.0f}s)', flush=True)
gam = [1, g[1], g[2], g[3]]
col = lambda idx: [1] + [H_main[t][idx] for t in (1, 2, 3)]
HP, HS_, Hth = col(1), col(2), [1] + [H_third[t] for t in (1, 2, 3)]
def mul(x, y): return [sum(x[i] * y[k - i] for i in range(k + 1)) for k in range(4)]
def div(x, y):
    q = []
    for k in range(4): q.append((x[k] - sum(q[i] * y[k - i] for i in range(k))) // y[0])
    return q
def divq(base, r):
    inv = [{0: 1, 1: -1, 2: 0}[i % 3] for i in range(4)]; c = [1, 0, 0, 0]
    for _ in range(r): c = [sum(c[i] * inv[s - i] for i in range(s + 1)) for s in range(4)]
    return [sum(base[i] * c[s - i] for i in range(s + 1)) for s in range(4)]
res = dict(n=9, phis=PHI.tolist(), min_c=int(minc), HS_A=gam, H_P=HP, H_third=Hth, H_span=HS_,
           i_predicted=div(mul(HP, Hth), gam), span_free_prediction=divq(gam, 3),
           ii=[dict(random_forms=k, H=col(2 + k), predicted=divq(HS_, k)) for k in range(5)])
res['i_excess'] = [x - y for x, y in zip(HS_, res['i_predicted'])]
res['span_excess'] = [x - y for x, y in zip(HS_, res['span_free_prediction'])]
for r in res['ii']: r['excess'] = [x - y for x, y in zip(r['H'], r['predicted'])]
print({k: res[k] for k in ('min_c', 'H_P', 'H_third', 'H_span', 'i_predicted', 'i_excess', 'span_excess')}, flush=True)
print([r['excess'] for r in res['ii']], f'({time.time()-t0:.0f}s)', flush=True)
json.dump(res, open(outp, 'w'), indent=1)
