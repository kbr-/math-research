"""Scalar model of the level-t joint kernel (one form, P_i = k): T = kernel over GF(3) of the down map
from t-sets to (t-1)-sets of n rows, c -> (S' -> sum_{i not in S'} c(S' + i)).  Compares dim T with the
span of polytabloids (products of t disjoint differences) and with the span of T(U), kernels on m-row
subsets U.  Usage: python3 scalar_t3.py OUT.json"""
import itertools, json, os, sys
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from short_generation import nullspace, gf3
def down(n, t, rows=None):
    rows = list(range(n)) if rows is None else rows
    ts = list(itertools.combinations(rows, t)); ls = list(itertools.combinations(rows, t - 1))
    li = {s: k for k, s in enumerate(ls)}
    M = np.zeros((len(ls), len(ts)), np.uint8)
    for k, S in enumerate(ts):
        for x in range(t): M[li[S[:x] + S[x + 1:]], k] = 1
    return ts, M
res = []
for t in (2, 3, 4):
    for n in range(2 * t, 2 * t + 5):
        ts, M = down(n, t); ti = {S: k for k, S in enumerate(ts)}
        dimT = len(ts) - gf3.rank(M)
        polys = []
        for a in itertools.permutations(range(n), 2 * t):
            pairs = [tuple(sorted(a[2 * x:2 * x + 2])) for x in range(t)]
            if any(p[0] != a[2 * x] for x, p in enumerate(pairs)): continue
            v = np.zeros(len(ts), np.int64)
            for choice in itertools.product((0, 1), repeat=t):
                S = tuple(sorted(pairs[x][choice[x]] for x in range(t))); v[ti[S]] += (-1) ** sum(choice)
            polys.append(v % 3)
        dimP = gf3.rank(np.array(polys, np.uint8))
        loc = {}
        for m in range(t + 1, n + 1):
            vecs = []
            for U in itertools.combinations(range(n), m):
                tsU, MU = down(n, t, list(U)); B = nullspace(MU)
                if B.shape[1] == 0: continue
                full = np.zeros((B.shape[1], len(ts)), np.uint8)
                for k, S in enumerate(tsU): full[:, ti[S]] = B[k] % 3
                vecs.append(full)
            loc[m] = int(gf3.rank(np.concatenate(vecs))) if vecs else 0
            if loc[m] == dimT: break
        r = dict(t=t, n=n, dimT=int(dimT), polytabloid_span=int(dimP), local_span=loc); print(r, flush=True); res.append(r)
json.dump(res, open(sys.argv[1], 'w'), indent=1)
