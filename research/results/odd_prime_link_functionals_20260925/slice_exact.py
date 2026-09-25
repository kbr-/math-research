"""Exact single-clause degree-5 kernel on one outside-row slice, by general product-array functionals.

Question: is the part of ker(g -> tau g) on the slice (row pairs (rho, r), rho in rows(U), r outside rows(U)) larger
than Taylor + blocking products?  Functionals: product arrays Omega = tensor over a 5-row set (r and four rows of U)
of (e_c - e_d), all ten labels distinct; these lie in K_5.  D_tau Omega(g) = sum_A 2 Omega(A u g).  If they span K_5 on
those row sets, rank = rank of mu_C on the slice, and the kernel dimension is exact.  Reported: kernel dimension,
Taylor, Taylor + blocking, and a basis of the kernel modulo Taylor + blocking (as label patterns) for inspection.
Usage: python3 slice_exact.py OUT.json N SAMPLES [|S| |T|]"""
import itertools, json, os, sys
import numpy as np
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'odd_prime_permutation_forms_20260923'))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'odd_prime_alignment_mechanism_20260922'))
import gf3, gf3_prefix

def rank3(rows, ncols):
    M = np.array(rows, dtype=np.int64) % 3
    Pk, W = gf3.pack(M.astype(np.uint8))
    return gf3_prefix.prefix_ranks(Pk, W, ncols, [len(rows)])[0]

N, SAMPLES = int(sys.argv[2]), int(sys.argv[3]); L = N - 1
nS, nT = (int(sys.argv[4]), int(sys.argv[5])) if len(sys.argv) > 5 else (4, 3)
U = nS + nT
lab = {i: 4 + i for i in range(U)}; S = list(range(nS)); T = list(range(nS, U))
assert 4 + U - 1 <= L - 1
pats = {tuple(sorted((a, b, c))) for a, b in itertools.combinations(S, 2) for c in T}
pairs = [(c, d) for c in range(L) for d in range(L) if c != d]; pidx = {p: i for i, p in enumerate(pairs)}; P = len(pairs)
ncol = U * P
col = lambda rho, c, c2: rho * P + pidx[(c, c2)]
rng = np.random.default_rng(N)
R = U  # index of the outside row r
vecs = []
rowsets = [rs for rs in itertools.combinations(range(U), 4)]
for _ in range(SAMPLES):
    rs = list(rowsets[rng.integers(len(rowsets))])
    labs = {}
    used = set()
    for row in rs:                                   # U rows: often include the U label
        pool = [c for c in range(N) if c not in used]
        if lab[row] not in used and rng.random() < 0.7:
            c = lab[row]
        else:
            c = int(rng.choice(pool))
        used.add(c)
        pool = [x for x in range(N) if x not in used]
        d = int(rng.choice(pool)); used.add(d)
        labs[row] = (c, d)
    pool = [x for x in range(N) if x not in used]
    cr, dr = (int(x) for x in rng.choice(pool, size=2, replace=False)); labs[R] = (cr, dr)
    f = lambda row, c: 1 if c == labs[row][0] else (-1 if c == labs[row][1] else 0)
    v = np.zeros(ncol, dtype=np.int64)
    for rho in rs:
        A = tuple(sorted(x for x in rs if x != rho))
        if A not in pats:
            continue
        wA = 1
        for x in A:
            wA *= f(x, lab[x])
        if wA == 0:
            continue
        for c in labs[rho]:
            for c2 in labs[R]:
                if c < L and c2 < L and c not in {lab[x] for x in A} and c2 not in {lab[x] for x in A}:
                    v[col(rho, c, c2)] += 2 * wA * f(rho, c) * f(R, c2)
    if v.any():
        vecs.append(v)
rk = rank3(vecs, ncol)
rel = []
for rho in range(U):
    v = np.zeros(ncol, dtype=np.int64); v[rho * P:(rho + 1) * P] = 1; rel.append(v)
tay = []
for c in range(L):
    v = np.zeros(ncol, dtype=np.int64)
    for a in S:
        if c != lab[a]:
            v[col(a, lab[a], c)] += 1
    tay.append(v)
def blocks(cells):
    for A in pats:
        if all(not any(rw == x or lb == lab[x] for x in A) for rw, lb in cells):
            return False
    return True
blk = []
for rho in range(U):
    for (c, c2) in pairs:
        if blocks([(rho, c), (99, c2)]):
            v = np.zeros(ncol, dtype=np.int64); v[col(rho, c, c2)] = 1; blk.append(v)
tr = rank3(rel + tay, ncol) - U; tb = rank3(rel + tay + blk, ncol) - U
out = dict(N=N, S=nS, T=nT, samples=len(vecs), dimG2=U * (P - 1), rank=rk, kernel=U * (P - 1) - rk, taylor=tr, taylor_plus_blocking=tb)
print(json.dumps(out), flush=True)
json.dump(out, open(sys.argv[1], 'w'), indent=1)

# ---- kernel modulo Taylor + blocking: explicit representatives ----
def rref3(M):
    M = M.copy() % 3; piv = []; r = 0
    for c in range(M.shape[1]):
        nz = np.nonzero(M[r:, c])[0]
        if len(nz) == 0: continue
        p = r + nz[0]; M[[r, p]] = M[[p, r]]
        if M[r, c] == 2: M[r] = (2 * M[r]) % 3
        others = np.nonzero(M[:, c])[0]; others = others[others != r]
        M[others] = (M[others] - np.outer(M[others, c], M[r])) % 3
        piv.append(c); r += 1
        if r == M.shape[0]: break
    return M[:r], piv
F = np.array(vecs, dtype=np.int64) % 3
comp = (rng.integers(0, 3, size=(ncol + 200, F.shape[0])) @ F) % 3     # compress the row space
Rm, piv = rref3(comp)
free = [c for c in range(ncol) if c not in set(piv)]
ker = []
for fc in free:
    v = np.zeros(ncol, dtype=np.int64); v[fc] = 1
    for i, pc in enumerate(piv):
        v[pc] = (-Rm[i, fc]) % 3
    ker.append(v)
base = rel + tay + blk
rb = rank3(base, ncol)
extra = []
for v in ker:
    if rank3(base + extra + [v], ncol) > rb + len(extra):
        extra.append(v)
def describe(v):
    terms = []
    for i in np.nonzero(v % 3)[0]:
        rho, k = divmod(int(i), P); c, c2 = pairs[k]
        terms.append((int(v[i] % 3), rho, c, c2))
    return terms
print('kernel dim (coords, incl. relations):', len(ker), 'extra beyond Taylor+blocking:', len(extra))
for v in extra:
    t = describe(v); print(len(t), t[:24])
