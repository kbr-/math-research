"""Independent check of the strictly positive mismatch in rank1_large.json (r=6, m=14): recomputes dim (X/(z)X)_k for
k <= 3 with a plain NumPy mod-3 elimination (no gf3 library), and max_h #{c : lam_c . h = 0} over all nonzero h in F_3^6."""
import itertools, json, os
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
b = [x for x in json.load(open(os.path.join(HERE, 'rank1_large.json')))['mismatches'] if x['strict_positive_at_failure']][0]
lam = np.array(b['lam']); m, r = lam.shape
def rank3(M):
    M = M.copy() % 3; rk = 0
    for c in range(M.shape[1]):
        piv = next((i for i in range(rk, M.shape[0]) if M[i, c]), None)
        if piv is None: continue
        M[[rk, piv]] = M[[piv, rk]]; M[rk] = (M[rk] * M[rk, c]) % 3          # inverse of 1 is 1, of 2 is 2
        nz = np.nonzero(M[:, c])[0]
        for i in nz:
            if i != rk: M[i] = (M[i] - M[i, c] * M[rk]) % 3
        rk += 1
    return rk
dims = [1]
for k in range(1, 4):
    Bk = list(itertools.combinations(range(m), k)); idx = {s: j for j, s in enumerate(Bk)}
    rows = []
    for S in itertools.combinations(range(m), k - 1):
        for i in range(r):
            v = np.zeros(len(Bk), dtype=np.int64)
            for c in range(m):
                if c not in S: v[idx[tuple(sorted(S + (c,)))]] += lam[c, i]
            rows.append(v % 3)
    dims.append(len(Bk) - rank3(np.array(rows)))
hmax = max(int(((lam @ np.array(h)) % 3 == 0).sum()) for h in itertools.product(range(3), repeat=r) if any(h))
print(dict(r=r, m=m, quotient_dims=dims, W=b['W'][:4], max_forms_in_a_hyperplane=hmax, cmin=m - hmax))
