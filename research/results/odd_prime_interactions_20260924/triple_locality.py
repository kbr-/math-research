"""Pairwise determination of low-degree vanishing ideals for triples of selector allowed sets on the occupancy slice.

Tested statement: for allowed sets U_1, U_2, U_3 (U_i = slice points with l_i != v_i, dense random forms over F_3),
I_d(U_1 n U_2 n U_3) = sum over i<j of I_d(U_i n U_j), where I_d(X) is the space of multilinear polynomials of degree
<= d vanishing on X.  Also records the pair defect dim I_d(U_i n U_j) - dim(I_d(U_i) + I_d(U_j)) for each pair.
Usage: python3 triple_locality.py OUT.json N:dmax:m:seed [...]"""
import itertools, json, random, sys, time
import numpy as np
p = 3
def rref(M):
    M = M.copy() % 3; r = 0; piv = []
    for c in range(M.shape[1]):
        k = next((i for i in range(r, M.shape[0]) if M[i, c]), None)
        if k is None: continue
        M[[r, k]] = M[[k, r]]; M[r] = (M[r] * (1 if M[r, c] == 1 else 2)) % 3
        nz = np.nonzero(M[:, c])[0]; nz = nz[nz != r]; M[nz] = (M[nz] - np.outer(M[nz, c], M[r])) % 3
        piv.append(c); r += 1
        if r == M.shape[0]: break
    return M[:r], piv
def null_left(E):
    """basis of {a : a E = 0} for E (monomials x points)"""
    R, piv = rref(E.T.copy())  # rows span of columns; solve E^T a = 0
    n = E.shape[0]; free = [c for c in range(n) if c not in piv]; B = []
    for f in free:
        a = np.zeros(n, dtype=np.int64); a[f] = 1
        for i, c in enumerate(piv): a[c] = (-R[i, f]) % 3
        B.append(a)
    return np.array(B, dtype=np.int64).reshape(len(B), n)
def rank(M): return 0 if M.size == 0 else len(rref(M)[1])
out = sys.argv[1]; res = []
for case in sys.argv[2:]:
    N, dmax, m, seed = map(int, case.split(':')); rnd = random.Random(seed)
    L = []
    while len(L) < 3:
        f = [rnd.randrange(1, p) for _ in range(N)]
        if len(set(f)) > 1: L.append((f, rnd.randrange(p)))
    pts = [c for c in itertools.product((0, 1), repeat=N) if sum(c) % p == m % p]
    ok = lambda c, i: sum(a * x for a, x in zip(L[i][0], c)) % p != L[i][1]
    t0 = time.time()
    for d in range(2, dmax + 1):
        mons = [T for e in range(d + 1) for T in itertools.combinations(range(N), e)]
        ev = lambda X: np.array([[int(all(c[j] for j in T)) for c in X] for T in mons], dtype=np.int64)
        I = {}
        for s in [(0,), (1,), (2,), (0, 1), (0, 2), (1, 2), (0, 1, 2)]:
            I[s] = null_left(ev([c for c in pts if all(ok(c, i) for i in s)]))
        sumdim = lambda keys: rank(np.vstack([I[k] for k in keys]))
        pair_def = {f'{a}{b}': len(I[(a, b)]) - sumdim([(a,), (b,)]) for a, b in [(0, 1), (0, 2), (1, 2)]}
        tri_pairs = len(I[(0, 1, 2)]) - sumdim([(0, 1), (0, 2), (1, 2)])
        tri_singles = len(I[(0, 1, 2)]) - sumdim([(0,), (1,), (2,)])
        row = dict(case=case, d=d, points=len(pts), dimI_triple=len(I[(0, 1, 2)]), pair_defects=pair_def,
                   triple_minus_pairwise_sum=tri_pairs, triple_minus_single_sum=tri_singles, seconds=round(time.time() - t0, 1))
        res.append(row); print(json.dumps(row), flush=True); json.dump(res, open(out, 'w'), indent=1)
