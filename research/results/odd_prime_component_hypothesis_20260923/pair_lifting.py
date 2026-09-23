"""Local no-fall check for an overlapping pair of 'forbid one value' constraints on a 3-dimensional span over F_3.
Function ring R = F_3[y1,y2,y3]/(y_i^3 - y_i) (functions on F_3^3) with the degree filtration; its top algebra is the
truncated ring B_3.  Constraint b: g_b = (1 - (mu_b - a_b)^2)(1 - (nu_b - c_b)^2), top mu_b^2 nu_b^2, zero set = the points
where (mu_b, nu_b) != (a_b, c_b), i.e. g_b forbids an affine line L_b.  The NS span N_k = span{m g_b : deg m + 4 <= k}, as
functions, is compared with the no-fall value dim P_{<=k} - sum_{j<=k} H_j(B_3/(tops)), H = (1,3,6,7,4,1,0) by the
overlapping-pair lemma.  A fall at degree k means dim N_k exceeds that value.  Enumerates all (W_1, W_2) and right-hand sides
up to the stated normalization and reports falls against whether the two forbidden lines meet.  Usage: --out JSON"""
import itertools, json, sys
import numpy as np
pts = list(itertools.product(range(3), repeat=3))
def rank3(M):
    M = np.array(M, dtype=np.int64) % 3; r = 0
    for c in range(M.shape[1]):
        piv = next((i for i in range(r, M.shape[0]) if M[i, c]), None)
        if piv is None: continue
        M[[r, piv]] = M[[piv, r]]; M[r] = (M[r] * M[r, c]) % 3
        for i in range(M.shape[0]):
            if i != r and M[i, c]: M[i] = (M[i] - M[i, c] * M[r]) % 3
        r += 1
    return r
mons = {k: [e for e in itertools.product(range(3), repeat=3) if sum(e) == k] for k in range(7)}
def ev(e, y): return int(np.prod([pow(int(y[i]), e[i], 3) if e[i] else 1 for i in range(3)])) % 3
Pk = {k: sum(len(mons[j]) for j in range(k + 1)) for k in range(7)}   # dim of polynomials of degree <= k as functions (monomials y^e, e_i <= 2, independent)
H = [1, 3, 6, 7, 4, 1, 0]; nofall = {k: Pk[k] - sum(H[:k + 1]) for k in range(7)}
def g_vals(mu, nu, a, c): return np.array([((1 - (int(np.dot(mu, y)) - a) ** 2) * (1 - (int(np.dot(nu, y)) - c) ** 2)) % 3 for y in pts])
proj = [np.array(v) for v in itertools.product(range(3), repeat=3) if any(v) and next(x for x in v if x) == 1]
res = []; e1, e2 = np.array([1, 0, 0]), np.array([0, 1, 0])
for mu2, nu2 in itertools.product(proj, repeat=2):
    if rank3([mu2, nu2]) < 2 or rank3([e1, e2, mu2, nu2]) < 3: continue
    for a1, c1, a2, c2 in itertools.product(range(3), repeat=4):
        G = [g_vals(e1, e2, a1, c1), g_vals(mu2, nu2, a2, c2)]
        L1 = {y for y in pts if (np.dot(e1, y) - a1) % 3 == 0 and (np.dot(e2, y) - c1) % 3 == 0}
        L2 = {y for y in pts if (np.dot(mu2, y) - a2) % 3 == 0 and (np.dot(nu2, y) - c2) % 3 == 0}
        falls = []
        for k in range(4, 7):
            rows = [(np.array([ev(e, y) for y in pts]) * g) % 3 for j in range(k - 3) for e in mons[j] for g in G]
            dN = rank3(rows); falls.append(dN - nofall[k])
        res.append(dict(mu2=mu2.tolist(), nu2=nu2.tolist(), rhs=[a1, c1, a2, c2], lines_meet=bool(L1 & L2), excess_dims_k4_to_6=falls))
by = {}
for r in res: by.setdefault((r['lines_meet'], tuple(r['excess_dims_k4_to_6'])), 0); by[(r['lines_meet'], tuple(r['excess_dims_k4_to_6']))] += 1
for k, v in sorted(by.items()): print('lines meet' if k[0] else 'lines disjoint', 'dim N_k - no-fall value (k=4,5,6):', list(k[1]), 'count', v)
json.dump(dict(no_fall_values=nofall, summary=[dict(lines_meet=k[0], excess=list(k[1]), count=v) for k, v in by.items()]), open(sys.argv[sys.argv.index('--out') + 1], 'w'), indent=1)
