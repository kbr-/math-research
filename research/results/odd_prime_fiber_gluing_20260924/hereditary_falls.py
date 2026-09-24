"""Do the specializations of an augmented column member's occupancy system fall (condition (i) of fiber gluing)?

Tested statement over F_p: for a column member with allowed set Z in the occupancy slice L = {c in {0,1}^N :
sum c = m mod p}, augmented to its full vanishing ideal I(Z) (all elements of degree <= D as generators), and for
every hole set S, the specialized system J_S (generators f|_{C_S=1}, on the holes outside S, slice sum = m - |S|)
has no fall in degrees e < D - |S|. When the single row is saturated through degree e + 1 (asserted for every (holes, residue,
degree) used, by row_saturated), the degree-e part of J_S modulo the slice is R_e = {f|_{C_S=1} : f in I(Z), deg f <= e} as
functions on L_S, and the fall in degree e is dim(R_{e+1} cap P_e) - dim R_e, P_e = functions of degree <= e on
L_S. Also reported: whether R_e equals I(Z_S)_{<=e} (restriction surjectivity, which implies no fall).
Members: 'merge' (C_1 C_2 = 0; control, predicted to fall at S = {1}), 'selector' (forbid l = v), 'clause2'
(forbid l_1 = v_1 and l_2 = v_2), 'sparse' (forbid a random set of occupancy patterns of density about 1/p^2).
Usage: python3 hereditary_falls.py OUT.json N:D:p:m:seed:smax [...]"""
import itertools, json, random, sys, time
import numpy as np

def rank(M, p):
    M = M.copy() % p; r = 0; rows, cols = M.shape
    for c in range(cols):
        piv = next((i for i in range(r, rows) if M[i, c]), None)
        if piv is None: continue
        M[[r, piv]] = M[[piv, r]]; M[r] = (M[r] * pow(int(M[r, c]), p - 2, p)) % p
        nz = np.nonzero(M[:, c])[0]; nz = nz[nz != r]
        M[nz] = (M[nz] - np.outer(M[nz, c], M[r])) % p
        r += 1
        if r == rows: break
    return r

def kernel(M, p):  # basis of {x : x M = 0} (left kernel), rows of the result
    rows, cols = M.shape
    A = np.concatenate([M % p, np.eye(rows, dtype=np.int64)], axis=1); r = 0
    for c in range(cols):
        piv = next((i for i in range(r, rows) if A[i, c]), None)
        if piv is None: continue
        A[[r, piv]] = A[[piv, r]]; A[r] = (A[r] * pow(int(A[r, c]), p - 2, p)) % p
        nz = np.nonzero(A[:, c])[0]; nz = nz[nz != r]
        A[nz] = (A[nz] - np.outer(A[nz, c], A[r])) % p
        r += 1
    return A[r:, cols:]

def row_saturated(n, mres, d, p):
    """Are the polynomials of degree <= d on n holes vanishing on the slice sum c = mres (mod p) exactly the
    multiples row * P_{d-1}, row = sum C_j - mres, reduced by C_j^2 = C_j?  This is what identifies the degree-e
    part of J_S (on the cube) with R_e (functions on the slice) for d = e, e + 1."""
    ms = [T for t in range(d + 1) for T in itertools.combinations(range(n), t)]; idx = {T: i for i, T in enumerate(ms)}
    pts = [c for c in itertools.product((0, 1), repeat=n) if sum(c) % p == mres % p]
    ev = np.array([[int(all(c[j] for j in T)) for c in pts] for T in ms], dtype=np.int64)
    vanishing = len(ms) - rank(ev.T.copy(), p)
    rows = []
    for T in ms:
        if len(T) > d - 1: continue
        v = np.zeros(len(ms), dtype=np.int64); v[idx[T]] = (len(T) - mres) % p
        for j in range(n):
            if j not in T: v[idx[tuple(sorted(T + (j,)))]] += 1
        rows.append(v % p)
    return vanishing == (rank(np.array(rows), p) if rows else 0)

SAT = {}
out = sys.argv[1]; res = []
for case in sys.argv[2:]:
    N, D, p, m, seed, smax = map(int, case.split(':')); rnd = random.Random(seed)
    phi = []
    while len(phi) < 2:
        f = [rnd.randrange(1, p) for _ in range(N)]
        if len(set(f)) > 1: phi.append(f)
    v = [rnd.randrange(p) for _ in range(2)]
    L = [c for c in itertools.product((0, 1), repeat=N) if sum(c) % p == m % p]
    ell = lambda b, c: sum(a * x for a, x in zip(phi[b], c)) % p
    bad = set(rnd.sample(L, max(1, len(L) // p**2)))
    members = {'merge': lambda c: not (c[0] and c[1]), 'selector': lambda c: ell(0, c) != v[0],
               'clause2': lambda c: (ell(0, c), ell(1, c)) != (v[0], v[1]), 'sparse': lambda c: c not in bad}
    mons = [T for d in range(D + 1) for T in itertools.combinations(range(N), d)]
    for label, allowed in members.items():
        t0 = time.time()
        Z = [c for c in L if allowed(c)]
        assert Z, 'empty allowed set'
        # I(Z)_{<=d}: coefficient vectors (over monomials of degree <= d) of polynomials vanishing on Z
        ev = lambda pts, ms: np.array([[int(all(c[j] for j in T)) for c in pts] for T in ms], dtype=np.int64)
        IZ = {d: kernel(ev(Z, [T for T in mons if len(T) <= d]), p) for d in range(D + 1)}
        worst = []
        for s in range(1, smax + 1):
            for S in itertools.combinations(range(N), s):
                rest = [j for j in range(N) if j not in S]
                LS = [c for c in L if all(c[j] for j in S)]  # points of L with the holes of S occupied
                ZS = [c for c in Z if all(c[j] for j in S)]
                for e in range(D - s):
                    if len(rest) < 2 * e + 3: continue
                    for d in (e, e + 1):
                        key = (len(rest), (m - s) % p, d)
                        if key not in SAT: SAT[key] = row_saturated(*key, p)
                        assert SAT[key], f'single row not saturated at {key}; the reduction to R_e fails'
                    def R(d):  # restrictions of I(Z)_{<=d} to C_S = 1, as functions on LS
                        ms = [T for T in mons if len(T) <= d]
                        return (IZ[d] @ ev(LS, ms)) % p if len(IZ[d]) else np.zeros((0, len(LS)), dtype=np.int64)
                    Pe = ev(LS, [T for T in mons if len(T) <= e and not set(T) & set(S)])
                    Re, Re1 = R(e), R(e + 1)
                    rRe, rRe1, rPe = rank(Re, p), rank(Re1, p), rank(Pe, p)
                    cap = rRe1 + rPe - rank(np.concatenate([Re1, Pe]), p)
                    izs = kernel(ev(ZS, [T for T in mons if len(T) <= e and not set(T) & set(S)]), p)
                    izs_fun = (izs @ Pe) % p if len(izs) else np.zeros((0, len(LS)), dtype=np.int64)
                    worst.append(dict(S=list(S), e=e, fall=cap - rRe, dim_R=rRe,
                                      dim_I_ZS=rank(izs_fun, p)))
        falls = [w for w in worst if w['fall']]
        row = dict(case=case, member=label, row_saturation_checked=sorted(map(list, SAT)), allowed=len(Z), slice=len(L), checks=len(worst),
                   falling=len(falls), examples=falls[:3],
                   surjective=all(w['dim_R'] == w['dim_I_ZS'] for w in worst), seconds=round(time.time() - t0, 1))
        res.append(row); print(json.dumps(row), flush=True)
json.dump(res, open(out, 'w'), indent=1)
