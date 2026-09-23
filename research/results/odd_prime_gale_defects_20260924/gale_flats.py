"""Gale flat statistics of column-model configurations, defective vs free (model_scaling_n results).

For hole functions phi_1..phi_d on n holes, W = span(1, phi_1..phi_d) in F_3^n (dim e), V = F_3^n/W (dim r = n-e) and m_j the
image of e_j.  Reports, for each configuration and degree, the model excess and: the number of zero Gale vectors, the largest
number of Gale vectors in a rank-1 flat (repeated points up to scalar), rank-2 flats and rank-3 flats (points counted with
multiplicity), computed exactly by brute force over the flats spanned by points (small n).  The candidate criterion under
test: a defect in degree t comes from an overfull low-rank Gale flat.  Usage: python3 gale_flats.py IN.json... --out OUT.json"""
import itertools, json, sys
import numpy as np
def rank3(M):
    M = M.copy() % 3; r = 0; rows, cols = M.shape
    for c in range(cols):
        p = next((i for i in range(r, rows) if M[i, c] % 3), None)
        if p is None: continue
        M[[r, p]] = M[[p, r]]; M[r] = (M[r] * (1 if M[r, c] == 1 else 2)) % 3
        for i in range(rows):
            if i != r and M[i, c]: M[i] = (M[i] - M[i, c] * M[r]) % 3
        r += 1
    return r
def gale(phis):
    n = len(phis[0]); Wm = np.array([[1] * n] + phis) % 3
    # basis of W^perp-complement: V = F^n / W; represent m_j by coordinates in a complement: take kernel of W (W^perp) as dual,
    # m_j coordinates = j-th column of a basis matrix of W^perp (Gale transform convention)
    # compute W^perp = {x : Wm x = 0}
    A = Wm.copy(); rows, cols = A.shape; piv = []; r = 0
    for c in range(cols):
        p = next((i for i in range(r, rows) if A[i, c] % 3), None)
        if p is None: continue
        A[[r, p]] = A[[p, r]]; A[r] = (A[r] * (1 if A[r, c] == 1 else 2)) % 3
        for i in range(rows):
            if i != r and A[i, c]: A[i] = (A[i] - A[i, c] * A[r]) % 3
        piv.append(c); r += 1
    free = [c for c in range(cols) if c not in piv]; K = []
    for f in free:
        x = np.zeros(cols, dtype=np.int64); x[f] = 1
        for i, c in enumerate(piv): x[c] = (-A[i, f]) % 3
        K.append(x)
    return np.array(K).T % 3            # n x r: row j = Gale vector m_j
def flat_stats(G):
    n, r = G.shape; nz = [j for j in range(n) if G[j].any()]; out = {'zero': n - len(nz)}
    for k in (1, 2, 3):
        best = 0
        for S in itertools.combinations(nz, k):
            if rank3(G[list(S)]) < k: continue
            B = G[list(S)]
            cnt = sum(1 for j in nz if rank3(np.vstack([B, G[j]])) == k)
            best = max(best, cnt)
        out[f'max_points_rank{k}'] = best
    return out
args = sys.argv[1:]; outp = args[args.index('--out') + 1]; ins = args[:args.index('--out')]; res = []
for f in ins:
    for row in json.load(open(f)):
        G = gale(row['phis']); st = flat_stats(G)
        res.append(dict(n=row['n'], trial=row['trial'], excess=row['excess'], free_pred=row['free'], **st))
        print(row['n'], row['trial'], 'excess', row['excess'], st, flush=True)
json.dump(res, open(outp, 'w'), indent=1)
