"""On kE = F_p[y_1..y_r]/(y_i^p) (raising operators y_i), graded by degree e: compare
 closed tuples, symmetric tuples (y_i z_a / mult(a) depends only on a+e_i, and y_i z_{(p-1)e_i} = 0), and lifts.
Symmetric tuples are exactly those satisfying every first-order necessary condition for z_a = mult(a) y^a w."""
import itertools, sys, json
from math import factorial
import numpy as np
sys.path.insert(0, __file__.rsplit('/', 1)[0])
from free_module_lift_graded import rref_mod, nullspace_mod
def run(p, r):
    d = p - 1
    mons = lambda e: [b for b in itertools.product(range(p), repeat=r) if sum(b) == e]
    A = [a for a in itertools.product(range(d + 1), repeat=r) if sum(a) == d]
    mult = {a: (factorial(d) // np.prod([factorial(x) for x in a])) % p for a in A}
    inv = {a: pow(int(mult[a]), p - 2, p) for a in A}
    B = [b for b in itertools.product(range(d + 2), repeat=r) if sum(b) == d + 1]
    out = []
    for e in range(r * d + 1):
        Me, Me1 = mons(e), mons(e + 1); ie = {b: i for i, b in enumerate(Me)}; ie1 = {b: i for i, b in enumerate(Me1)}
        m, m1 = len(Me), len(Me1); n = len(A) * m
        rows = []
        for b in B:
            pre = [(A.index(tuple(b[j] - (j == i) for j in range(r))), i) for i in range(r) if b[i] >= 1]
            # closed: sum_i y_i z_{b-e_i} = 0 ; symmetric: inv(a) y_i z_a equal across preimages, and 0 if single preimage
            def vec(ai, i, coef):
                v = np.zeros((m1, n), dtype=np.int64)
                for mono in Me:
                    if mono[i] + 1 < p:
                        c = list(mono); c[i] += 1; v[ie1[tuple(c)], ai * m + ie[mono]] = coef
                return v
            if len(pre) == 1:
                ai, i = pre[0]; rows.append(vec(ai, i, 1))
            else:
                (a0, i0) = pre[0]
                for (ai, i) in pre[1:]:
                    rows.append((vec(a0, i0, inv[A[a0]]) - vec(ai, i, inv[A[ai]])) % p)
        S = np.vstack(rows) if m1 else np.zeros((0, n), dtype=np.int64)
        sym = n - (len(rref_mod(S, p)[1]) if len(S) else 0)
        W = mons(e - d) if e >= d else []
        L = np.zeros((max(len(W), 1), n), dtype=np.int64)
        for wi, w in enumerate(W):
            for ai, a in enumerate(A):
                t = tuple(w[j] + a[j] for j in range(r))
                if all(x < p for x in t): L[wi, ai * m + ie[t]] = mult[a]
        lift = len(rref_mod(L, p)[1])
        out.append({'degree': e, 'symmetric': sym, 'lifted': lift})
    return {'p': p, 'r': r, 'by_degree': out}
res = []
for p, r in [(3, 3), (3, 4), (5, 3), (7, 3), (5, 4)]:
    o = run(p, r); res.append(o)
    bad = [(x['degree'], x['symmetric'], x['lifted']) for x in o['by_degree'] if x['symmetric'] != x['lifted']]
    print(p, r, 'symmetric != lifted at', bad if bad else 'no degree')
json.dump(res, open(sys.argv[1], 'w'), indent=1)
