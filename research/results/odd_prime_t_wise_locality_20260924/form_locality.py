"""Degreewise locality of supported functions in form space.

Tested statement (form-space core of conj:t-wise-locality): over F_3, for clauses b with affine forms L_b (k forms each)
on F_3^s, forbidden sets B_b = {L_b = v_b}, allowed sets U_b = complement, and every e,
I_e(n_b U_b) = sum_b I_e(U_b), where I_e(X) = polynomials of degree <= e (exponents <= 2) vanishing on X.
The t-wise independence of the family (every <= t clauses have independent combined linear parts) is computed and
reported, not assumed.  Output per family: s, k, linear parts, values, t, and the defect dim I_e(n U_b) - dim sum.
Usage: python3 form_locality.py OUT.json s:k:M:trials:seed [...]"""
import itertools, json, random, sys, time
import numpy as np
p = 3
def rref(M):
    M = M.copy() % p; r = 0; piv = []
    for c in range(M.shape[1]):
        k = next((i for i in range(r, M.shape[0]) if M[i, c]), None)
        if k is None: continue
        M[[r, k]] = M[[k, r]]; M[r] = (M[r] * (1 if M[r, c] == 1 else 2)) % p
        nz = np.nonzero(M[:, c])[0]; nz = nz[nz != r]; M[nz] = (M[nz] - np.outer(M[nz, c], M[r])) % p
        piv.append(c); r += 1
        if r == M.shape[0]: break
    return M[:r], piv
def rank(M): return 0 if M.size == 0 else len(rref(M)[1])
def null_left(E):
    R, piv = rref(E.T.copy()); n = E.shape[0]; free = [c for c in range(n) if c not in piv]; B = []
    for f in free:
        a = np.zeros(n, dtype=np.int64); a[f] = 1
        for i, c in enumerate(piv): a[c] = (-R[i, f]) % p
        B.append(a)
    return np.array(B, dtype=np.int64).reshape(len(B), n)
def indep_t(lins, k):
    """largest t such that every <= t clauses have independent combined linear parts"""
    M = len(lins) // k; t = 0
    for size in range(1, M + 1):
        for S in itertools.combinations(range(M), size):
            rows = np.array([lins[b * k + j] for b in S for j in range(k)], dtype=np.int64)
            if rank(rows) < len(rows): return t
        t = size
    return t
out = sys.argv[1]; res = []
for case in sys.argv[2:]:
    s, k, M, trials, seed = map(int, case.split(':')); rnd = random.Random(seed)
    pts = list(itertools.product(range(p), repeat=s))
    mons_all = sorted(itertools.product(range(p), repeat=s), key=sum)
    t0 = time.time()
    for tr in range(trials):
        lins = [[rnd.randrange(p) for _ in range(s)] for _ in range(M * k)]
        if any(not any(l) for l in lins): continue
        vals = [rnd.randrange(p) for _ in range(M * k)]
        forb = lambda y, b: all(sum(a * x for a, x in zip(lins[b * k + j], y)) % p == vals[b * k + j] for j in range(k))
        Z = [y for y in pts if not any(forb(y, b) for b in range(M))]
        t = indep_t(lins, k); defects = []
        for e in range(1, (p - 1) * s + 1):
            mons = [m for m in mons_all if sum(m) <= e]
            ev = lambda X: np.array([[int(np.prod([pow(y[i], m[i], p) for i in range(s)]) % p) for y in X] for m in mons], dtype=np.int64)
            IZ = null_left(ev(Z)) if Z else np.eye(len(mons), dtype=np.int64)
            parts = [null_left(ev([y for y in pts if not forb(y, b)])) for b in range(M)]
            parts = [q for q in parts if len(q)]
            sm = rank(np.vstack(parts)) if parts else 0
            defects.append(len(IZ) - sm)
        row = dict(case=case, trial=tr, s=s, k=k, M=M, t=t, allowed=len(Z), lins=lins, vals=vals, defects=defects)
        res.append(row); print(json.dumps({x: row[x] for x in ('case', 'trial', 't', 'allowed', 'defects')}), flush=True)
    json.dump(res, open(out, 'w'), indent=1)
    print('case done', case, round(time.time() - t0, 1), flush=True)
