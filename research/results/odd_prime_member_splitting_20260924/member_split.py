"""Tensor splitting between two non-free members on the weak unary PHP top algebra A (n = 8, F_3), through degree 3.

Tested statement (lem:tensor-splitting-locality's Tor_0 prediction for two members): if A = M_1 (x) M_2 (x) C with the
members acting on their own factors, then HS(A/(P, P')A) = HS(A/PA) * HS(A/P'A) / HS_A (power series, through degree 3).
P is the recorded 4-robust occupancy pair.  Second members: 'perm' = the pair under a random hole permutation (so
HS(A/P'A) = HS(A/PA) by symmetry, asserted by computing it); 'col c' = one column-type form whose hole function has
c = n - (largest value multiplicity), c = 2, 3, 4 (non-free from degree ceil(c/2)+1 by the occupancy theorem).
The pair's rows (monomial x form, normal forms) are computed once and cached (shared prefix); each configuration adds
only its own rows.  Usage: python3 member_split.py --config perm|col --c C --seed S --cache DIR --out OUT.json"""
import json, os, sys, time
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); RES = os.path.join(HERE, '..'); BA = os.path.join(RES, 'odd_prime_board_affine_20260923')
a = dict(zip(sys.argv[1::2], sys.argv[2::2])); cfg = a['--config']; cc = int(a.get('--c', '0')); sd = int(a['--seed']); cache = a['--cache']; outp = a['--out']
sys.argv = [sys.argv[0], '--n', '8', '--K', '3', '--rs', '', '--family', 'random']
exec(open(os.path.join(BA, 'board_affine.py')).read().split("res = []\nif opt.phis:")[0])
sys.path.insert(0, os.path.join(RES, 'odd_prime_permutation_forms_20260923')); from gf3_prefix import prefix_ranks
t0 = time.time(); rec = json.load(open(os.path.join(BA, 'n8_K3_column_robust.json')))['runs'][0]
phis = [np.array(f[0]) for f in rec['forms']]; HP = rec['H']
def lin_of(phi): return {(i * n + j,): int(phi[j]) for i in range(P1) for j in range(n) if phi[j] % 3}
def rows_for(lin, t):
    R_ = np.zeros((len(basis[t - 1]), g[t]), dtype=np.uint8)
    for r_, m in enumerate(basis[t - 1]): R_[r_] = L.normal_form(L.mul({m: 1}, lin) if m else lin, Q[t], g[t]) % 3
    return R_
os.makedirs(cache, exist_ok=True); cf = os.path.join(cache, 'pair_rows.npz')
if os.path.exists(cf): z = np.load(cf); pair_rows = {t: z[f'r{t}'] for t in (1, 2, 3)}
else:
    pair_rows = {t: np.vstack([rows_for(lin_of(p), t) for p in phis]) for t in (1, 2, 3)}; np.savez_compressed(cf, **{f'r{t}': pair_rows[t] for t in (1, 2, 3)})
print('pair rows ready', f'({time.time()-t0:.0f}s)', flush=True)
rng = np.random.default_rng(700 + sd)
if cfg == 'perm':
    sig = rng.permutation(n); second = [p[sig] for p in phis]
else:
    while True:
        phi = rng.integers(0, 3, size=n)
        if n - np.bincount(phi, minlength=3).max() == cc: break
    second = [phi]
def rank_series(blocks, t):
    P_, W_ = L.gf3.pack(np.vstack(blocks))[:2]
    return [int(x) for x in prefix_ranks(np.ascontiguousarray(P_, dtype=np.uint64), W_, g[t], np.cumsum([b.shape[0] for b in blocks]).tolist())]
Hsec, Hboth = [1], [1]
for t in (1, 2, 3):
    srows = np.vstack([rows_for(lin_of(p), t) for p in second])
    Hsec.append(g[t] - rank_series([srows], t)[-1]); Hboth.append(g[t] - rank_series([pair_rows[t], srows], t)[-1])
gam = [1, g[1], g[2], g[3]]
def mul(x, y): return [sum(x[i] * y[k - i] for i in range(k + 1)) for k in range(4)]
def div(x, y): q = []; [q.append((x[k] - sum(q[i] * y[k - i] for i in range(k))) // y[0]) for k in range(4)]; return q
pred = div(mul(HP, Hsec), gam)
res = dict(config=cfg, c=cc, seed=sd, second=[p.tolist() for p in second], HS_A=gam, H_pair=HP, H_second=Hsec, H_both=Hboth,
           predicted=pred, excess=[x - y for x, y in zip(Hboth, pred)])
print(res, f'({time.time()-t0:.0f}s)', flush=True); json.dump(res, open(outp, 'w'), indent=1)
