"""Mayer-Vietoris locality of low-degree functions for pairs of allowed sets on the occupancy slice.

Tested statement: for allowed sets U, W (complements in the slice of forbidden-value sets of dense column forms), the
restriction sequence 0 -> F_d(U u W) -> F_d(U) + F_d(W) -> F_d(U n W) -> 0 is exact at every filtration level d <= dmax,
i.e. defect_d = r_d(U u W) - r_d(U) - r_d(W) + r_d(U n W) = 0, with r_d(X) = dim of the functions of degree <= d
restricted to X (rank of the evaluation matrix of multilinear monomials of degree <= d on X).  defect_d <= 0 always;
0 means every pair of degree-<=d functions on U and W agreeing on U n W glues to a degree-<=d function on U u W.
Pairs: two selectors (forbid l_1 = v_1, forbid l_2 = v_2) and two two-form clauses, on independent dense random forms
(coefficients in {1, 2}), over F_3; also the specialized pairs Z_S for |S| = 1 (holes of S occupied), which the
direct-sum form needs.  Usage: python3 mv_locality.py OUT.json N:dmax:m:seed:kind [...]"""
import itertools, json, random, sys, time
import numpy as np
p = 3
def rank3(M):
    M = M.copy() % 3; r = 0
    for c in range(M.shape[1]):
        piv = next((i for i in range(r, M.shape[0]) if M[i, c]), None)
        if piv is None: continue
        M[[r, piv]] = M[[piv, r]]; M[r] = (M[r] * (1 if M[r, c] == 1 else 2)) % 3
        nz = np.nonzero(M[:, c])[0]; nz = nz[nz != r]; M[nz] = (M[nz] - np.outer(M[nz, c], M[r])) % 3; r += 1
        if r == M.shape[0]: break
    return r
out = sys.argv[1]; res = []
for case in sys.argv[2:]:
    N, dmax, m, seed, kind = case.split(':'); N, dmax, m, seed = int(N), int(dmax), int(m), int(seed)
    rnd = random.Random(seed); k = 1 if kind == 'selectors' else 2
    cl = []
    for _ in range(2):
        fs = []
        while len(fs) < k:
            f = [rnd.randrange(1, p) for _ in range(N)]
            if len(set(f)) > 1: fs.append(f)
        cl.append((fs, [rnd.randrange(p) for _ in range(k)]))
    pts = [c for c in itertools.product((0, 1), repeat=N) if sum(c) % p == m % p]
    forb = lambda c, t: all(sum(a * x for a, x in zip(f, c)) % p == v for f, v in zip(*cl[t]))
    t0 = time.time(); rows = []
    for S in [()] + [(j,) for j in range(min(N, 3))]:
        rest = [j for j in range(N) if j not in S]
        P_ = [c for c in pts if all(c[j] for j in S)]
        U = [c for c in P_ if not forb(c, 0)]; W = [c for c in P_ if not forb(c, 1)]
        UW = [c for c in P_ if not forb(c, 0) or not forb(c, 1)]; UnW = [c for c in U if not forb(c, 1)]
        for d in range(dmax + 1 - len(S)):
            mons = [T for e in range(d + 1) for T in itertools.combinations(rest, e)]
            r = lambda X: rank3(np.array([[int(all(c[j] for j in T)) for c in X] for T in mons], dtype=np.int64)) if X else 0
            rU, rW, rUW, rUnW = r(U), r(W), r(UW), r(UnW)
            rows.append(dict(S=list(S), d=d, rU=rU, rW=rW, rUnionW=rUW, rUcapW=rUnW, defect=rUW - rU - rW + rUnW))
    bad = [x for x in rows if x['defect']]
    row = dict(case=case, sizes=[len(pts)], checks=len(rows), failing=len(bad), examples=bad[:4], seconds=round(time.time() - t0, 1))
    res.append(row); print(json.dumps(row), flush=True)
    json.dump(res, open(out, 'w'), indent=1)
