#!/usr/bin/env python3
"""Exact check of the hole-splitting identities (lem:hole-splitting), N = 10, p = 3, seconds.

For a column member Z (patterns in the slice sum = m mod 3) and a hole j, with Y a hole set not
containing j, Z^0 = {c in Z : c_j = 0} and Z^1 = {c in Z : c_j = 1} (patterns on the other holes):
  Q_Y := projection of a_{Y,e}(Z) onto the monomials without C_j  ==  a_{Y,e}(Z^0) cap a_{Y,e}(Z^1)
  K_Y := {h : C_j h in a_{Y,e}(Z)}                              ==  a_{Y,e-1}(Z^0) + a_{Y,e-1}(Z^1)
where a_{Y,e}(X) is the space of degree-e tops of polynomials of degree <= e vanishing on X_Y.
Reports mismatches per member (0 expected).
"""
import itertools, json, sys
import numpy as np
sys.path.insert(0, __file__.rsplit('/', 1)[0])
from vanishing_tops import rref3, nullspace3, rank3

N, m = 10, 11
rng = np.random.default_rng(20260925)
phi = rng.integers(0, 3, size=(4, N))
form = lambda c, b: int(np.dot(phi[b], c) % 3)
clause = lambda c, i, S, k: form(c, i) == k[i] and all(form(c, j) != k[j] for j in S)
members = {
    'low-weight control': lambda c: sum(c) <= 2,
    'one clause, k=1': lambda c: not clause(c, 0, [1], {0: 0, 1: 0}),
    "two-block pair, k=1, i=i'": lambda c: not clause(c, 0, [1], {0: 0, 1: 0}) and not clause(c, 0, [1], {0: 1, 1: 1}),
}


def tops(pts, holes, e):
    """Basis of degree-e vanishing tops on the point set pts (columns = holes), as rows over monomials."""
    mons = [mu for k in range(e + 1) for mu in itertools.combinations(holes, k)]
    col = {h: i for i, h in enumerate(holes)}
    if len(pts) == 0:
        ker = np.eye(len(mons), dtype=np.int64)
    else:
        E = np.array([[int(all(p[col[h]] for h in mu)) for mu in mons] for p in pts], dtype=np.int64)
        ker = nullspace3(E)
    ti = [i for i, mu in enumerate(mons) if len(mu) == e]
    T = ker[:, ti] if len(ker) else np.zeros((0, len(ti)), dtype=np.int64)
    return [mons[i] for i in ti], (rref3(T)[0] if len(T) else T)


def embed(mus, T, target):
    idx = {mu: i for i, mu in enumerate(target)}
    out = np.zeros((len(T), len(target)), dtype=np.int64)
    for r, row in enumerate(T):
        for mu, cf in zip(mus, row):
            if cf:
                out[r, idx[mu]] = cf
    return out


def same(A, B):
    ra, rb = rank3(A), rank3(B)
    return ra == rb == rank3(np.vstack([A, B])) if (len(A) or len(B)) else True


def intersect_dim(A, B):
    return rank3(A) + rank3(B) - rank3(np.vstack([A, B])) if len(A) and len(B) else 0


res = {}
j = 0
for name, allowed in members.items():
    pts = np.array([c for c in itertools.product((0, 1), repeat=N) if sum(c) % 3 == m % 3 and allowed(c)])
    bad = {'Q': 0, 'K': 0, 'checked': 0}
    for e in (1, 2):
        for ysz in (0, 1, 2):
            for Y in itertools.combinations(range(1, N), ysz):
                sel = pts[np.all(pts[:, list(Y)] == 1, axis=1)] if Y else pts
                rest = [h for h in range(N) if h not in Y]                 # includes j
                rest0 = [h for h in rest if h != j]
                musZ, TZ = tops(sel[:, rest], rest, e)
                Z0 = sel[sel[:, j] == 0][:, rest0]
                Z1 = sel[sel[:, j] == 1][:, rest0]
                mus0, T0 = tops(Z0, rest0, e)
                mus1, T1 = tops(Z1, rest0, e)
                target_e = [mu for mu in itertools.combinations(rest0, e)]
                # Q: projection of a_{Y,e}(Z) to monomials without j
                proj = np.zeros((len(TZ), len(target_e)), dtype=np.int64)
                idx = {mu: i for i, mu in enumerate(target_e)}
                for r, row in enumerate(TZ):
                    for mu, cf in zip(musZ, row):
                        if cf and j not in mu:
                            proj[r, idx[mu]] = cf
                A0, A1 = embed(mus0, T0, target_e), embed(mus1, T1, target_e)
                inter = intersect_dim(A0, A1)
                okQ = rank3(proj) == inter and (rank3(np.vstack([proj, A0])) == rank3(A0)) and \
                      (rank3(np.vstack([proj, A1])) == rank3(A1))
                # K: {h : C_j h in a_{Y,e}(Z)} = kernel part of TZ supported on monomials containing j
                target_e1 = [mu for mu in itertools.combinations(rest0, e - 1)]
                idxj = {mu: i for i, mu in enumerate(musZ)}
                nonj = [i for i, mu in enumerate(musZ) if j not in mu]
                withj = [i for i, mu in enumerate(musZ) if j in mu]
                comb = nullspace3(TZ[:, nonj].T) if len(TZ) else np.zeros((0, 0), dtype=np.int64)  # combos killing non-j part
                Krows = (comb @ TZ[:, withj]) % 3 if len(comb) else np.zeros((0, len(withj)), dtype=np.int64)
                Kmus = [tuple(h for h in musZ[i] if h != j) for i in withj]
                Kemb = embed(Kmus, Krows, target_e1) if len(Krows) else np.zeros((0, len(target_e1)), dtype=np.int64)
                m0, S0 = tops(Z0, rest0, e - 1)
                m1, S1 = tops(Z1, rest0, e - 1)
                Ssum = np.vstack([embed(m0, S0, target_e1), embed(m1, S1, target_e1)])
                okK = same(Kemb, Ssum) if (len(Kemb) or len(Ssum)) else True
                bad['checked'] += 1
                bad['Q'] += int(not okQ)
                bad['K'] += int(not okK)
    res[name] = bad
    print(name, bad, flush=True)
if '--out' in sys.argv:
    json.dump(res, open(sys.argv[sys.argv.index('--out') + 1], 'w'), indent=1)
