"""Column component plus random forms on the weak unary PHP top algebra A over F_3, through degree 3.

Tested statement (conj:column-component-splitting, both directions as stated in the notebook's next step): a column
component whose span has every nonzero form with column count c >= Q+1 splits off from generic forms through degree t
exactly when Q >= 2t-2 (here t = 3, Q >= 4); splitting's prediction for k appended random forms is
HS(A/(S, r_1..r_k)A) = [q^t] HS(A/SA)(q)/(1+q+q^2)^k.  The member S is given by hole functions (column-type forms, the same
function on every row).  One incremental pass per degree; rows are a4lib normal forms, ranks by the compiled prefix kernel.
Usage: python3 col_member_random.py --n 8 --phis '0,2,2,2,0,2,0,2' --k 4 --seed 1 --out OUT.json"""
import json, os, sys, time, itertools
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); RES = os.path.join(HERE, '..'); BA = os.path.join(RES, 'odd_prime_board_affine_20260923')
a = dict(zip(sys.argv[1::2], sys.argv[2::2])); nn = a['--n']; kr = int(a['--k']); sd = int(a['--seed']); outp = a['--out']
PH = [np.array([int(x) for x in s.split(',')]) for s in a['--phis'].split(';')]
sys.argv = [sys.argv[0], '--n', nn, '--K', '3', '--rs', '', '--family', 'random']
t0 = time.time(); exec(open(os.path.join(BA, 'board_affine.py')).read().split("res = []\nif opt.phis:")[0])
sys.path.insert(0, os.path.join(RES, 'odd_prime_permutation_forms_20260923')); from gf3_prefix import prefix_ranks
assert all(len(p) == n for p in PH)
dirs = [np.array(c) for c in itertools.product(range(3), repeat=len(PH)) if any(c) and c[next(i for i, x in enumerate(c) if x)] == 1]
minc = int(min(n - np.bincount(sum(u[b] * PH[b] for b in range(len(PH))) % 3, minlength=3).max() for u in dirs))
def rows_for(F, t):
    lin = {(i * n + j,): int(F[i, j]) for i in range(P1) for j in range(n) if F[i, j] % 3}
    R_ = np.zeros((len(basis[t - 1]), g[t]), dtype=np.uint8)
    for r_, m in enumerate(basis[t - 1]): R_[r_] = L.normal_form(L.mul({m: 1}, lin) if m else lin, Q[t], g[t]) % 3
    return R_
rng2 = np.random.default_rng(1300 + sd); rand = [rng2.integers(0, 3, size=(P1, n)) for _ in range(kr)]
forms = [np.tile(p, (P1, 1)) for p in PH] + rand; m = len(PH); H = {}
for t in (1, 2, 3):
    blocks = [rows_for(F, t) for F in forms]
    P_, W_ = L.gf3.pack(np.vstack(blocks))[:2]
    H[t] = [g[t] - int(x) for x in prefix_ranks(np.ascontiguousarray(P_, dtype=np.uint64), W_, g[t], np.cumsum([b.shape[0] for b in blocks]).tolist())]
def divq(base, r):
    inv = [{0: 1, 1: -1, 2: 0}[i % 3] for i in range(4)]; c = [1, 0, 0, 0]
    for _ in range(r): c = [sum(c[i] * inv[s - i] for i in range(s + 1)) for s in range(4)]
    return [sum(base[i] * c[s - i] for i in range(s + 1)) for s in range(4)]
gam = [1, g[1], g[2], g[3]]; HS_ = [1] + [H[t][m - 1] for t in (1, 2, 3)]
rows = [dict(random_forms=j, H=[1] + [H[t][m - 1 + j] for t in (1, 2, 3)], predicted=divq(HS_, j)) for j in range(kr + 1)]
for r in rows: r['excess'] = [x - y for x, y in zip(r['H'], r['predicted'])]
res = dict(n=n, phis=[p.tolist() for p in PH], min_c=minc, Q=minc - 1, HS_A=gam, H_member=HS_, member_free_prediction=divq(gam, m),
           seed=sd, rows=rows, splits=all(r['excess'] == [0, 0, 0, 0] for r in rows))
print(dict(n=n, min_c=minc, H_member=HS_, free_pred=res['member_free_prediction'], excess=[r['excess'][3] for r in rows], splits=res['splits']),
      f'({time.time()-t0:.0f}s)', flush=True)
json.dump(res, open(outp, 'w'), indent=1)
