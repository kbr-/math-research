"""Deciding test of conj:large-support-taylor at degree 5 (width 1): the inside block.

Statement tested: for one clause with |S| >= 6, |T| >= 5, the kernel of g -> tau g on the inside block (G_2 on row pairs
within rows(U)) is exactly the Taylor part (l_S y_v, v on rows of U, and l_T^2).  Here a multiplying cell on a row of U
kills two cells of U, the case the factor 2 in the size condition is for.  The kernel dimension is bracketed: sampled
product-array functionals (tensor of (e_c - e_d) on 5-row subsets of rows(U), ten distinct labels) give an upper bound
dim G_2 - rank; Taylor (+ blocking) gives a lower bound.  Equality decides.
Usage: python3 inside_exact.py OUT.json N SAMPLES nS nT"""
import itertools, json, os, sys
import numpy as np
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'odd_prime_permutation_forms_20260923'))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'odd_prime_alignment_mechanism_20260922'))
import gf3, gf3_prefix

def rank3(M, ncols):
    Pk, W = gf3.pack(np.asarray(M, dtype=np.uint8) % 3)
    return gf3_prefix.prefix_ranks(Pk, W, ncols, [M.shape[0]])[0]

N, SAMPLES, nS, nT = (int(x) for x in sys.argv[2:6]); L = N - 1; U = nS + nT
lab = {i: 4 + i for i in range(U)}; S = list(range(nS)); T = list(range(nS, U))
assert 4 + U - 1 <= L - 1
pats = {tuple(sorted((a, b, c))) for a, b in itertools.combinations(S, 2) for c in T}
pairs = [(c, d) for c in range(L) for d in range(L) if c != d]; pidx = {p: i for i, p in enumerate(pairs)}; P = len(pairs)
rp = list(itertools.combinations(range(U), 2)); rpi = {p: k for k, p in enumerate(rp)}; ncol = len(rp) * P
def colin(i, ci, j, cj):
    if i > j: i, j, ci, cj = j, i, cj, ci
    return rpi[(i, j)] * P + pidx[(ci, cj)]
rng = np.random.default_rng(N)
rowsets = [rs for rs in itertools.combinations(range(U), 5) if any(
    tuple(sorted(set(rs) - {i, j})) in pats for i, j in itertools.combinations(rs, 2))]
CH = 20000; chunks = []; buf = np.zeros((CH, ncol), dtype=np.uint8); k = 0; nb = 0
PU = float(os.environ.get('PU', '0.7'))
for _ in range(SAMPLES):
    rs = list(rowsets[rng.integers(len(rowsets))]); labs = {}; used = set()
    for row in rs:
        pool = [c for c in range(N) if c not in used]
        c = lab[row] if (lab[row] not in used and rng.random() < PU) else int(rng.choice(pool))
        used.add(c); pool = [x for x in range(N) if x not in used]
        d = int(rng.choice(pool)); used.add(d); labs[row] = (c, d)
    f = lambda row, c: 1 if c == labs[row][0] else (-1 if c == labs[row][1] else 0)
    v = np.zeros(ncol, dtype=np.int64)
    for i, j in itertools.combinations(rs, 2):
        A = tuple(sorted(set(rs) - {i, j}))
        if A not in pats: continue
        wA = 1
        for x in A: wA *= f(x, lab[x])
        if wA == 0: continue
        for ci in labs[i]:
            for cj in labs[j]:
                if ci < L and cj < L:
                    v[colin(i, ci, j, cj)] += 2 * wA * f(i, ci) * f(j, cj)
    if v.any():
        buf[nb] = v % 3; nb += 1; k += 1
        if nb == CH:
            chunks.append(gf3.pack(buf)[0]); nb = 0
if nb:
    chunks.append(gf3.pack(buf[:nb])[0])
Wd = (ncol + 63) // 64
Pk = np.concatenate(chunks, axis=0)
rk = gf3_prefix.prefix_ranks(Pk, Wd, ncol, [Pk.shape[0]])[0]
base = []
for q in range(len(rp)):
    v = np.zeros(ncol, dtype=np.uint8); v[q * P:(q + 1) * P] = 1; base.append(v)
nrel = len(base)
for vr in range(U):                       # l_S y_v, v on row vr of U
    for c in range(L):
        v = np.zeros(ncol, dtype=np.int64)
        for a in S:
            if a != vr and c != lab[a]:
                v[colin(a, lab[a], vr, c)] += 1
        if v.any(): base.append(v % 3)
v = np.zeros(ncol, dtype=np.int64)
for t1, t2 in itertools.combinations(T, 2): v[colin(t1, lab[t1], t2, lab[t2])] += 2
base.append(v % 3)
tr = rank3(np.array(base), ncol) - nrel
out = dict(N=N, S=nS, T=nT, samples=int(k), dimG2=len(rp) * (P - 1), rank=int(rk), kernel_upper=len(rp) * (P - 1) - int(rk), taylor=int(tr))
out['decided_taylor'] = out['kernel_upper'] == out['taylor']
print(json.dumps(out), flush=True)
json.dump(out, open(sys.argv[1], 'w'), indent=1)
