"""Characteristic-3 apolarity for the column model: which model defects survive in the Hasse fat-point count.

Tested statement (proved in the entry): for the column model with span W (containing the all-ones vector) and
Lambda = F_3[t_1..t_n]/(t_j^2), the model is Lambda/W.Lambda, while the Hasse fat points of multiplicity s-1 at the
Gale points [m_j] have dim (I_Z)_s = dim (Lambda/(W.Lambda + sum_i e_3(w_i).Lambda + ...))_s, with e_a(w) the a-th
elementary symmetric function of the c_j t_j (w = sum c_j t_j) and w_i a spanning set of W; for s <= 5 only a = 3 enters.
The script (1) validates the fat side against a direct Hasse-derivative computation on small random configurations,
(2) reports, for every recorded model configuration, the model HF, the fat HF and the free prediction.
Ranks are exact GF(3) (compiled gf3 kernel).  Usage: python3 frobenius_classes.py --out OUT.json [--validate N] [--validate-only 1]"""
import itertools, json, os, sys
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', 'odd_prime_alignment_mechanism_20260922')); import gf3
a = dict(zip(sys.argv[1::2], sys.argv[2::2]))
from math import comb
def combos(n, k):
    if k == 0: return np.zeros((1, 0), dtype=np.int64)
    return np.array(list(itertools.combinations(range(n), k)), dtype=np.int64).reshape(-1, k)
def colex(C):
    """Colex rank of sorted combinations (rows of C); a bijection onto 0..C(n,k)-1."""
    if C.shape[1] == 0: return np.zeros(C.shape[0], dtype=np.int64)
    tab = np.array([[comb(x, i + 1) for i in range(C.shape[1])] for x in range(64)], dtype=np.int64)
    return tab[C, np.arange(C.shape[1])].sum(axis=1)
def mult_rows(n, k, S, js, coef):
    """Rows (one per row of S) of the products t_S * (sum_j coef_j t_{js_j}) in the squarefree basis of degree k."""
    M = np.zeros((S.shape[0], comb(n, k)), dtype=np.uint8)
    for j, c in zip(js, coef):
        j = np.atleast_1d(j); U = np.concatenate([S, np.full((S.shape[0], len(j)), 0)], axis=1); U[:, S.shape[1]:] = j
        ok = ~np.isin(S, j).any(axis=1)
        if not ok.any(): continue
        M[np.nonzero(ok)[0], colex(np.sort(U[ok], axis=1))] = int(c) % 3
    return M
def hf_pair(n, W, K):
    """HF of Lambda/W.Lambda and of Lambda/(W.Lambda + e_3(w).Lambda) through K."""
    W = [np.array(w, dtype=np.int64) % 3 for w in W]; Hm, Hf = [1], [1]
    T3 = combos(n, 3)
    for k in range(1, K + 1):
        S = combos(n, k - 1)
        base = np.vstack([mult_rows(n, k, S, np.nonzero(w)[0][:, None], w[np.nonzero(w)[0]]) for w in W])
        rk_m = int(gf3.rank(base)); Hm.append(comb(n, k) - rk_m)
        if k < 3: Hf.append(Hm[-1]); continue
        S3 = combos(n, k - 3); extra = []
        for w in W:
            c = (w[T3[:, 0]] * w[T3[:, 1]] * w[T3[:, 2]]) % 3; nz = np.nonzero(c)[0]
            extra.append(mult_rows(n, k, S3, T3[nz], c[nz]))
        Hf.append(comb(n, k) - int(gf3.rank(np.vstack([base] + extra))))
    return Hm, Hf
def kernel_basis(A):
    """Basis over F_3 of {c : A c = 0} for a small integer matrix A (rows = coordinates of V)."""
    A = np.array(A, dtype=np.int64) % 3; m, n = A.shape; R = A.copy(); piv = []; r = 0
    for c in range(n):
        p = next((i for i in range(r, m) if R[i, c]), None)
        if p is None: continue
        R[[r, p]] = R[[p, r]]; R[r] = R[r] * R[r, c] % 3
        for i in range(m):
            if i != r and R[i, c]: R[i] = (R[i] - R[i, c] * R[r]) % 3
        piv.append(c); r += 1
    free = [c for c in range(n) if c not in piv]; B = []
    for f in free:
        v = np.zeros(n, dtype=np.int64); v[f] = 1
        for i, c in enumerate(piv): v[c] = (-R[i, f]) % 3
        B.append(v.tolist())
    return B
def lucas_arr(x, y):
    r = np.ones_like(x)
    for _ in range(3):
        u, v = x % 3, y % 3; r = r * np.where(v > u, 0, np.array([[1, 0, 0], [1, 1, 0], [1, 2, 1]])[u, v]) % 3; x = x // 3; y = y // 3
    return r
def fat_direct(P, s):
    """dim of degree-s forms in dim(V) variables with all Hasse derivatives of order <= s-2 zero at each point of P."""
    dv = len(P[0]); E = np.array([e for e in itertools.product(range(s + 1), repeat=dv) if sum(e) == s], dtype=np.int64)
    Bs = np.array([e for e in itertools.product(range(s - 1), repeat=dv) if sum(e) <= s - 2], dtype=np.int64)
    rows = []
    for p in np.array(P, dtype=np.int64):
        D = E[None, :, :] - Bs[:, None, :]
        val = np.where(D < 0, 0, lucas_arr(E[None, :, :] + 0 * D, np.broadcast_to(Bs[:, None, :], D.shape).copy()) * (np.where(D < 0, 0, p[None, None, :] ** np.maximum(D, 0)) % 3))
        rows.append(np.prod(val, axis=2) % 3)
    return len(E) - int(gf3.rank(np.vstack(rows).astype(np.uint8)))
def divq(base, m, K):
    inv = np.array([[1, -1, 0][i % 3] for i in range(K + 1)], dtype=np.int64); c = np.zeros(K + 1, dtype=np.int64); c[0] = 1
    for _ in range(m): c = np.convolve(c, inv)[:K + 1]
    return [int(x) for x in np.convolve(np.array(base, dtype=np.int64), c)[:K + 1]]
out = {'validation': [], 'configs': []}
# (1) validation: random point sets P in F_3^dv spanning V; U = F_3^n with t_j -> P_j, W = kernel.
rng = np.random.default_rng(3); bad = 0
for trial in range(int(a.get('--validate', 60))):
    dv = int(rng.integers(2, 5)); n = int(rng.integers(dv, dv + 4))
    while True:
        P = rng.integers(0, 3, size=(n, dv))
        if int(gf3.rank((P % 3).astype(np.uint8))) == dv and P.any(axis=1).all(): break
    W = kernel_basis(P.T.tolist()); K = 4
    Hm, Hf = hf_pair(n, W if W else [[0] * n], K)
    direct = [fat_direct(P.tolist(), s) for s in range(2, K + 1)]
    ok = Hf[2:] == direct; bad += (not ok)
    out['validation'].append(dict(dv=dv, n=n, P=P.tolist(), model=Hm, fat_lambda=Hf, fat_direct=[None, None] + direct, agree=ok))
print('validation: disagreements', bad, 'of', len(out['validation']), '; model != fat in',
      sum(v['model'] != v['fat_lambda'] for v in out['validation']), flush=True)
if '--validate-only' in a: json.dump(out, open(a['--out'], 'w'), indent=1); sys.exit(0)
# (2) recorded configurations
R = os.path.join(HERE, '..', 'odd_prime_column_gale_20260924')
cfgs = [('pair_n8', [[2, 0, 2, 0, 1, 0, 1, 2], [1, 0, 0, 2, 1, 1, 0, 2]], 3),
        ('span3_n9', [[0, 2, 0, 2, 0, 2, 2, 1, 0], [2, 0, 2, 2, 1, 1, 0, 0, 1], [2, 1, 0, 2, 0, 2, 0, 0, 2]], 3),
        ('span3_n10', [[0, 0, 1, 1, 0, 1, 0, 0, 1, 1], [1, 0, 1, 1, 0, 2, 2, 2, 1, 0], [0, 1, 1, 0, 2, 1, 0, 1, 2, 0]], 3)]
for f, K in [('model_scaling_d3.json', 4), ('model_scaling_d3_K4.json', 4), ('model_scaling_d3_K5.json', 5)]:
    for x in json.load(open(os.path.join(R, f))): cfgs.append((f'{f}:n{x["n"]}t{x["trial"]}', x['phis'], K))
for name, phis, K in cfgs:
    n = len(phis[0]); W = [[1] * n] + phis
    HR, _ = hf_pair(n, [[1] * n], K); Hm, Hf = hf_pair(n, W, K); free = divq(HR, len(phis), K)
    rec = dict(name=name, n=n, K=K, model=Hm, fat=Hf, free=free,
               model_excess=[h - w for h, w in zip(Hm, free)], fat_excess=[h - w for h, w in zip(Hf, free)])
    out['configs'].append(rec); print(name, 'model_excess', rec['model_excess'], 'fat_excess', rec['fat_excess'], flush=True)
json.dump(out, open(a['--out'], 'w'), indent=1)
