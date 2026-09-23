"""Tests the general statement for the scalar model over GF(3): the kernel of the down map
d: M_t -> M_(t-1) on n points is spanned by the elements poly_i (x) J_(t-i)(C), for 0<=i<=t with
t-i = 0 mod 3, where poly_i is a product of i disjoint differences and J_m(C) is the constant
function on the m-subsets of a block C of size m+2 disjoint from them; and dim ker d equals
Wilson's count sum_{i<=t, 3 | t-i} (C(n,i) - C(n,i-1)).  Usage: python3 scalar_generators.py OUT"""
import itertools, json, os, sys
from math import comb
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from short_generation import gf3
from scalar_t3 import down
res = []
for t in range(1, 6):
    for n in range(2 * t, 2 * t + 4):
        if comb(n, t) > 800: continue
        ts, M = down(n, t); ti = {S: k for k, S in enumerate(ts)}
        dimK = len(ts) - gf3.rank(M)
        wilson = sum(comb(n, i) - (comb(n, i - 1) if i else 0) for i in range(t + 1) if (t - i) % 3 == 0)
        gens = []
        for i in range(t + 1):
            if (t - i) % 3: continue
            m = t - i; c = m + 2 if m else 0
            if 2 * i + c > n: continue
            for pts in itertools.permutations(range(n), 2 * i):
                if any(pts[2 * x] > pts[2 * x + 1] for x in range(i)) or any(pts[2 * x] > pts[2 * x + 2] for x in range(i - 1)): continue
                rest = [x for x in range(n) if x not in pts]
                for C in itertools.combinations(rest, c):
                    v = np.zeros(len(ts), np.int64)
                    for ch in itertools.product((0, 1), repeat=i):
                        base = [pts[2 * x + ch[x]] for x in range(i)]
                        for Tm in itertools.combinations(C, m):
                            v[ti[tuple(sorted(base + list(Tm)))]] += (-1) ** sum(ch)
                    gens.append(v % 3)
        G = np.array(gens, np.uint8)
        assert not ((M.astype(np.int64) @ G.T.astype(np.int64)) % 3).any()      # all lie in ker d
        span = gf3.rank(G)
        r = dict(t=t, n=n, dim_kernel=int(dimK), wilson=int(wilson), generator_span=int(span), max_rows=2 * t)
        print(r, flush=True); res.append(r)
json.dump(res, open(sys.argv[1], 'w'), indent=1)
