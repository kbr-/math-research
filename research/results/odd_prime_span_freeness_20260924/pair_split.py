"""Tensor splitting of the weak unary PHP top algebra A (n = 8, F_3) for the recorded occupancy pair plus random forms.

Tested statement: A splits through degree 3 as (A over the pair's algebra) (x) (free over the random forms' algebra), i.e.
k uniform random linear forms act freely on A/(l_1, l_2): the Hilbert function of A/(l_1, l_2, r_1..r_k) is
[q^t] H_pair(q) / (1+q+q^2)^k (truncated at the first nonpositive coefficient), with H_pair = HS of A/(l_1, l_2).
This is the hypothesis of the tensor-splitting form of the Kunneth component lemma for one non-free member plus random
forms.  The pair is the recorded 4-robust occupancy pair (n8_K3_column_robust.json, first run), whose A is not free over
its own forms.  One incremental pass: rows (monomial x form) in normal form per form, prefix ranks by the compiled kernel.
Usage: python3 pair_split.py --k 4 --seed 1 --out OUT.json"""
import json, os, sys
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); RES = os.path.join(HERE, '..'); BA = os.path.join(RES, 'odd_prime_board_affine_20260923')
a = dict(zip(sys.argv[1::2], sys.argv[2::2])); kr = int(a['--k']); seed = int(a['--seed']); outp = a['--out']
sys.argv = [sys.argv[0], '--n', '8', '--K', '3', '--rs', '', '--family', 'random']
exec(open(os.path.join(BA, 'board_affine.py')).read().split("res = []\nif opt.phis:")[0])
sys.path.insert(0, os.path.join(RES, 'odd_prime_permutation_forms_20260923')); from gf3_prefix import prefix_ranks
rec = json.load(open(os.path.join(BA, 'n8_K3_column_robust.json')))['runs'][0]
pair = [np.array(f) for f in rec['forms']]
assert all(len(set(f[0])) > 1 for f in pair) and all((f == f[0]).all() for f in pair)          # column-type: same hole function on every row
rng2 = np.random.default_rng(500 + seed); rand = [rng2.integers(0, 3, size=(P1, n)) for _ in range(kr)]
forms = pair + rand
lins = [{(i * n + j,): int(Fb[i, j]) for i in range(P1) for j in range(n) if Fb[i, j]} for Fb in forms]
H = {}
for t in (1, 2, 3):
    blocks = []
    for lin in lins:
        rows = np.zeros((len(basis[t - 1]), g[t]), dtype=np.uint8)
        for r_, m in enumerate(basis[t - 1]): rows[r_] = L.normal_form(L.mul({m: 1}, lin) if m else lin, Q[t], g[t]) % 3
        blocks.append(rows)
    P_, W_ = L.gf3.pack(np.vstack(blocks))[:2]
    rk = prefix_ranks(np.ascontiguousarray(P_, dtype=np.uint64), W_, g[t], np.cumsum([b.shape[0] for b in blocks]).tolist())
    H[t] = [g[t] - int(x) for x in rk]; print('degree', t, 'H after each form:', H[t], flush=True)
Hp = [1, H[1][1], H[2][1], H[3][1]]
assert Hp == rec['H'], (Hp, rec['H'])
def divide(base, r):
    inv = [{0: 1, 1: -1, 2: 0}[i % 3] for i in range(4)]; c = [1, 0, 0, 0]
    for _ in range(r): c = [sum(c[i] * inv[s - i] for i in range(s + 1)) for s in range(4)]
    W = [sum(base[i] * c[s - i] for i in range(s + 1)) for s in range(4)]; out, dead = [], False
    for w in W: dead = dead or w <= 0; out.append(0 if dead else w)
    return out
rows = []
for j in range(kr + 1):
    got = [1, H[1][1 + j], H[2][1 + j], H[3][1 + j]]; pred = divide(Hp, j)
    rows.append(dict(random_forms=j, H=got, predicted=pred, excess=[x - y for x, y in zip(got, pred)]))
    print(rows[-1], flush=True)
json.dump(dict(n=8, pair=rec['forms'], seed=seed, random_forms=kr, gamma=[1, g[1], g[2], g[3]], H_pair=Hp, rows=rows), open(outp, 'w'), indent=1)
