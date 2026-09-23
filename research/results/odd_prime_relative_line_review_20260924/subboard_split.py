"""Falsification attempt for the relative line (route review): do members of forms confined to a sub-board split?
Weak unary PHP top algebra A over F_3 at n = 8 through degree 3 (a4lib normal forms, compiled prefix ranks).
A 'sub-board member' is two uniform random forms supported on the cells of a hole set H (all pigeons), nonconstant on every
row restricted to H... (rows restricted to H vary).  Tests, with splitting predictions:
  (i)  M(H) then 4 random full forms:          HS(A/(M, r_1..r_k)A) = HS(A/MA)/(1+q+q^2)^k;
  (ii) M(H1), M(H2) with H1, H2 disjoint:        HS(A/(M1,M2)A) = HS(A/M1A) HS(A/M2A)/HS_A;
  (iii) the same with |H1 cap H2| = 1.
The line's claim predicts splitting unless the members are column-type.  Usage: python3 subboard_split.py --seed 1 --out OUT.json"""
import json, os, sys, time
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); RES = os.path.join(HERE, '..'); BA = os.path.join(RES, 'odd_prime_board_affine_20260923')
a = dict(zip(sys.argv[1::2], sys.argv[2::2])); sd = int(a['--seed']); outp = a['--out']
sys.argv = [sys.argv[0], '--n', '8', '--K', '3', '--rs', '', '--family', 'random']
exec(open(os.path.join(BA, 'board_affine.py')).read().split("res = []\nif opt.phis:")[0])
sys.path.insert(0, os.path.join(RES, 'odd_prime_permutation_forms_20260923')); from gf3_prefix import prefix_ranks
rng2 = np.random.default_rng(2100 + sd)
def sub_member(H):
    F = []
    while len(F) < 2:
        f = np.zeros((P1, n), dtype=np.int64); f[:, H] = rng2.integers(0, 3, size=(P1, len(H)))
        if all(len(set(f[i, H])) > 1 for i in range(P1)): F.append(f)
    return F
def rows_for(F, t):
    lin = {(i * n + j,): int(F[i, j]) for i in range(P1) for j in range(n) if F[i, j] % 3}
    R_ = np.zeros((len(basis[t - 1]), g[t]), dtype=np.uint8)
    for r_, m in enumerate(basis[t - 1]): R_[r_] = L.normal_form(L.mul({m: 1}, lin) if m else lin, Q[t], g[t]) % 3
    return R_
def hf_series(forms):
    H = {}
    for t in (1, 2, 3):
        blocks = [rows_for(F, t) for F in forms]
        P_, W_ = L.gf3.pack(np.vstack(blocks))[:2]
        H[t] = [g[t] - int(x) for x in prefix_ranks(np.ascontiguousarray(P_, dtype=np.uint64), W_, g[t], np.cumsum([b.shape[0] for b in blocks]).tolist())]
    return [[1, H[1][k], H[2][k], H[3][k]] for k in range(len(forms))]
gam = [1, g[1], g[2], g[3]]
def mul(x, y): return [sum(x[i] * y[k - i] for i in range(k + 1)) for k in range(4)]
def div(x, y):
    q = []
    for k in range(4): q.append((x[k] - sum(q[i] * y[k - i] for i in range(k))) // y[0])
    return q
def divq(base, m):
    inv = [{0: 1, 1: -1, 2: 0}[i % 3] for i in range(4)]; c = [1, 0, 0, 0]
    for _ in range(m): c = [sum(c[i] * inv[s - i] for i in range(s + 1)) for s in range(4)]
    return [sum(base[i] * c[s - i] for i in range(s + 1)) for s in range(4)]
M1, M2d, M2o = sub_member([0, 1, 2]), sub_member([3, 4, 5]), sub_member([2, 3, 4])
rand = [rng2.integers(0, 3, size=(P1, n)) for _ in range(4)]
res = dict(n=8, seed=sd, HS_A=gam)
s1 = hf_series(M1 + rand); HM1 = s1[1]
res['i'] = [dict(k=k, H=s1[1 + k], predicted=divq(HM1, k)) for k in range(5)]
HM2d = hf_series(M2d)[1]; HM2o = hf_series(M2o)[1]
Hd = hf_series(M1 + M2d)[3]; Ho = hf_series(M1 + M2o)[3]
res['ii'] = dict(H_M1=HM1, H_M2=HM2d, H_both=Hd, predicted=div(mul(HM1, HM2d), gam))
res['iii'] = dict(H_M1=HM1, H_M2=HM2o, H_both=Ho, predicted=div(mul(HM1, HM2o), gam))
res['M1_free_excess'] = [x - y for x, y in zip(HM1, divq(gam, 2))]
for key in ('ii', 'iii'): res[key]['excess'] = [x - y for x, y in zip(res[key]['H_both'], res[key]['predicted'])]
for r in res['i']: r['excess'] = [x - y for x, y in zip(r['H'], r['predicted'])]
print('M1 free excess', res['M1_free_excess'], '| (i) excess', [r['excess'][3] for r in res['i']], '| (ii)', res['ii']['excess'], '| (iii)', res['iii']['excess'], flush=True)
json.dump(res, open(outp, 'w'), indent=1, default=int)
