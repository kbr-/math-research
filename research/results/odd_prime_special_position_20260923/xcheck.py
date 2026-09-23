"""Cross-check of pencil_cap.json instances in the rank-one column-tensor model: generators z_i = sum_c a^(i)_c t_c for a
basis a^(i) of the linear dependencies of the points mu_c, so X/(z)X = F_3[s_1..s_v]/(mu_c^2).  Compares dim (X/(z)X)_k,
k <= 2, with W_k = [t^k](1+t)^m/(1+t+t^2)^r, r = m - v."""
import itertools, json, os, sys
import numpy as np
from math import comb
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, '..', 'odd_prime_alignment_mechanism_20260922'))
import gf3
def nullspace(M):
    """basis of {a : a M = 0} over F_3 for an integer matrix M (rows = vectors)."""
    M = np.array(M, dtype=np.int64) % 3; n = M.shape[0]
    A = np.concatenate([M, np.eye(n, dtype=np.int64)], axis=1); r = 0
    for c in range(M.shape[1]):
        piv = next((i for i in range(r, n) if A[i, c]), None)
        if piv is None: continue
        A[[r, piv]] = A[[piv, r]]; A[r] = (A[r] * A[r, c]) % 3
        for i in range(n):
            if i != r and A[i, c]: A[i] = (A[i] - A[i, c] * A[r]) % 3
        r += 1
    return A[r:, M.shape[1]:]
for inst in json.load(open(os.path.join(HERE, 'pencil_cap.json'))):
    if not inst.get('found') or inst['v'] > 6: continue
    P = np.array(inst['points']); m, v = P.shape; A = nullspace(P); r = len(A)
    inv = [{0: 1, 1: -1, 2: 0}[i % 3] for i in range(3)]; c = [1, 0, 0]
    for _ in range(r): c = [sum(c[i] * inv[k - i] for i in range(k + 1)) for k in range(3)]
    W = [sum(comb(m, i) * c[k - i] for i in range(k + 1)) for k in range(3)]
    dims = [1]
    for k in (1, 2):
        Bk = list(itertools.combinations(range(m), k)); idx = {b: j for j, b in enumerate(Bk)}
        rows = []
        for S in itertools.combinations(range(m), k - 1):
            for a in A:
                row = np.zeros(len(Bk), dtype=np.uint8)
                for cc in range(m):
                    if cc not in S: row[idx[tuple(sorted(S + (cc,)))]] = (row[idx[tuple(sorted(S + (cc,)))]] + a[cc]) % 3
                rows.append(row)
        dims.append(len(Bk) - gf3.rank(np.array(rows)))
    print(dict(v=v, m=m, r=r, trial=inst['trial'], quotient=dims, W=W), flush=True)
