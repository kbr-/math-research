"""Check of the quiet-members lemma over F_3.

Statement: if P in F_3^d is the common zero set of m clauses prod_{j in S} L_j^2 (width k, linear parts independent),
every nonzero reduced polynomial vanishing on P has degree r >= 2 log_3(1/(m (2/3)^k)).
For random families at d = 3..5, k = 1..3, m = 1..12, compute the least degree of a nonzero reduced polynomial vanishing
on P exactly (GF(3) rank of the evaluation matrix on P, monomials by degree), and compare with the bound.
Asserted: each clause's linear parts are independent.  Also recorded: the least degree when P is the whole space
(no such polynomial) is reported as None.
Usage: python3 quiet_members.py --out OUT.json"""
import argparse, itertools, json, math, os, sys
import numpy as np
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'odd_prime_aligned_induction_20260923'))
from edge_sequence import rank_mod
def least_degree(P, d):
    mons = sorted(itertools.product(range(3), repeat=d), key=sum)
    E = np.array([[int(np.prod([pt[i] ** e[i] for i in range(d)]) % 3) for e in mons] for pt in P], dtype=np.int64).reshape(len(P), len(mons))
    for r in range(0, 2 * d + 1):
        cols = [j for j, e in enumerate(mons) if sum(e) <= r]
        rk = rank_mod(E[:, cols], 3) if len(P) else 0
        if rk < len(cols): return r
    return None
ap = argparse.ArgumentParser(); ap.add_argument('--out', required=True); a = ap.parse_args()
rng = np.random.default_rng(3); res = []; viol = 0
for d in (3, 4, 5):
    pts = list(itertools.product(range(3), repeat=d))
    for k in range(1, min(3, d) + 1):
        for m in (1, 2, 3, 4, 6, 8, 12):
            for trial in range(3):
                clauses = []
                while len(clauses) < m:
                    A = rng.integers(0, 3, size=(k, d)); c = rng.integers(0, 3, size=k)
                    if rank_mod(A.copy(), 3) == k: clauses.append((A, c))
                P = [pt for pt in pts if all(any((A[j] @ np.array(pt) + c[j]) % 3 == 0 for j in range(k)) for A, c in clauses)]
                r = least_degree(P, d); frac = m * (2 / 3) ** k
                bound = 2 * math.log(1 / frac, 3) if frac < 1 else 0.0
                ok = r is None or r >= bound - 1e-9; viol += not ok
                res.append(dict(d=d, k=k, m=m, trial=trial, allowed=len(P), least_degree=r, bound=round(bound, 3), ok=ok))
    print(f'd={d} done; violations so far {viol}', flush=True)
json.dump(dict(violations=viol, rows=res), open(a.out, 'w'), indent=1)
tight = [x for x in res if x['least_degree'] is not None and x['least_degree'] - x['bound'] < 1]
print('cases', len(res), 'violations', viol, 'within 1 of the bound', len(tight))
