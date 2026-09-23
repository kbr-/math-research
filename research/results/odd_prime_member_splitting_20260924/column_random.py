"""Does the grouped column component split off from random forms?  Weak unary PHP top algebra A (n = 8, F_3), through
degree 3.  Member: the recorded occupancy pair plus the column-type form of split_col_c5_s1.json (one column component);
then k = 1..5 uniform random linear forms.  Tested statement (splitting A = M_col (x) T_rand (x) C): the Hilbert function
of A/(member, r_1..r_k)A is [q^t] H_member(q) / (1+q+q^2)^k.  One incremental pass; the pair's rows come from the cache.
Usage: python3 column_random.py --k 5 --seed 1 --cache DIR --out OUT.json"""
import json, os, sys, time
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); RES = os.path.join(HERE, '..'); BA = os.path.join(RES, 'odd_prime_board_affine_20260923')
a = dict(zip(sys.argv[1::2], sys.argv[2::2])); kr = int(a['--k']); sd = int(a['--seed']); cache = a['--cache']; outp = a['--out']
sys.argv = [sys.argv[0], '--n', '8', '--K', '3', '--rs', '', '--family', 'random']
exec(open(os.path.join(BA, 'board_affine.py')).read().split("res = []\nif opt.phis:")[0])
sys.path.insert(0, os.path.join(RES, 'odd_prime_permutation_forms_20260923')); from gf3_prefix import prefix_ranks
t0 = time.time(); z = np.load(os.path.join(cache, 'pair_rows.npz')); pair_rows = {t: z[f'r{t}'] for t in (1, 2, 3)}
col = np.array(json.load(open(os.path.join(HERE, 'split_col_c5_s1.json')))['second'][0])
def rows_for(F, t):
    lin = {(i * n + j,): int(F[i, j]) for i in range(P1) for j in range(n) if F[i, j] % 3}
    R_ = np.zeros((len(basis[t - 1]), g[t]), dtype=np.uint8)
    for r_, m in enumerate(basis[t - 1]): R_[r_] = L.normal_form(L.mul({m: 1}, lin) if m else lin, Q[t], g[t]) % 3
    return R_
rng2 = np.random.default_rng(900 + sd); rand = [rng2.integers(0, 3, size=(P1, n)) for _ in range(kr)]
H = {}
for t in (1, 2, 3):
    blocks = [pair_rows[t], rows_for(np.tile(col, (P1, 1)), t)] + [rows_for(F, t) for F in rand]
    P_, W_ = L.gf3.pack(np.vstack(blocks))[:2]
    rk = prefix_ranks(np.ascontiguousarray(P_, dtype=np.uint64), W_, g[t], np.cumsum([b.shape[0] for b in blocks]).tolist())
    H[t] = [g[t] - int(x) for x in rk]
Hm = [1, H[1][1], H[2][1], H[3][1]]
def divide(base, r):
    inv = [{0: 1, 1: -1, 2: 0}[i % 3] for i in range(4)]; c = [1, 0, 0, 0]
    for _ in range(r): c = [sum(c[i] * inv[s - i] for i in range(s + 1)) for s in range(4)]
    return [sum(base[i] * c[s - i] for i in range(s + 1)) for s in range(4)]
rows = [dict(random_forms=j, H=[1, H[1][1 + j], H[2][1 + j], H[3][1 + j]], predicted=divide(Hm, j)) for j in range(kr + 1)]
for r in rows: r['excess'] = [x - y for x, y in zip(r['H'], r['predicted'])]; print(r, flush=True)
json.dump(dict(n=8, column_form=col.tolist(), seed=sd, H_member=Hm, rows=rows), open(outp, 'w'), indent=1)
print(f'({time.time()-t0:.0f}s)')
