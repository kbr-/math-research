"""Is rho: R_[n] -> sum_j R_[n]\\j, f -> (f|_{C_j=0})_j, injective in degree t over F_p?

Dual form, computed here: Z_t(X) = functions on t-subsets of X with zero marginals (sum over k not in S' of
f(S'+k) = 0 for every (t-1)-subset S'), the dual of the column model's degree-t part.  rho is injective in
degree t iff Z_t([n]) is spanned by the zero-extensions of Z_t([n] minus j), j = 1..n.  Prints
dim Z_t([n]) and the dimension of that span.  Exact rank over F_p by Gaussian elimination (numpy int64);
sizes are at most C(12,5) = 792 columns, seconds.
Usage: python3 rho_injectivity.py P NMAX TMAX OUT.json"""
import itertools, json, sys
import numpy as np
p, nmax, tmax, out = int(sys.argv[1]), int(sys.argv[2]), int(sys.argv[3]), sys.argv[4]

def rank_mod(M):
    M = M.copy() % p; r = 0; rows, cols = M.shape
    for c in range(cols):
        piv = next((i for i in range(r, rows) if M[i, c]), None)
        if piv is None: continue
        M[[r, piv]] = M[[piv, r]]; M[r] = (M[r] * pow(int(M[r, c]), p - 2, p)) % p
        nz = np.nonzero(M[:, c])[0]
        for i in nz:
            if i != r: M[i] = (M[i] - M[i, c] * M[r]) % p
        r += 1
        if r == rows: break
    return r

def nullspace_mod(M):
    """Basis of {v : M v = 0} over F_p, as rows."""
    M = M.copy() % p; rows, cols = M.shape; piv_cols = []; r = 0
    for c in range(cols):
        piv = next((i for i in range(r, rows) if M[i, c]), None)
        if piv is None: continue
        M[[r, piv]] = M[[piv, r]]; M[r] = (M[r] * pow(int(M[r, c]), p - 2, p)) % p
        for i in np.nonzero(M[:, c])[0]:
            if i != r: M[i] = (M[i] - M[i, c] * M[r]) % p
        piv_cols.append(c); r += 1
        if r == rows: break
    free = [c for c in range(cols) if c not in piv_cols]; basis = []
    for f in free:
        v = np.zeros(cols, dtype=np.int64); v[f] = 1
        for i, c in enumerate(piv_cols): v[c] = (-M[i, f]) % p
        basis.append(v)
    return np.array(basis, dtype=np.int64).reshape(len(basis), cols)

res = []
for n in range(3, nmax + 1):
    for t in range(1, min(tmax, n - 1) + 1):
        sets = list(itertools.combinations(range(n), t)); idx = {s: i for i, s in enumerate(sets)}
        subs = list(itertools.combinations(range(n), t - 1))
        marg = np.zeros((len(subs), len(sets)), dtype=np.int64)
        for a, S1 in enumerate(subs):
            for k in range(n):
                if k not in S1: marg[a, idx[tuple(sorted(S1 + (k,)))]] += 1
        dimZ = len(sets) - rank_mod(marg)
        gens = []
        for j in range(n):
            keep = [i for i, s in enumerate(sets) if j not in s]
            subsj = [a for a, S1 in enumerate(subs) if j not in S1]
            Nj = nullspace_mod(marg[np.ix_(subsj, keep)])
            for v in Nj:
                w = np.zeros(len(sets), dtype=np.int64); w[keep] = v; gens.append(w)
        span = rank_mod(np.array(gens)) if gens else 0
        res.append(dict(p=p, n=n, t=t, dimZ=dimZ, span=span, injective=(span == dimZ)))
        print(json.dumps(res[-1]), flush=True)
json.dump(res, open(out, 'w'), indent=1)
