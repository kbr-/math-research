"""Column-model freeness of robust column spans as n grows (the model reproduced the board excesses 3, 7, 1 at n = 8, 9, 10).

Tested statement: for a d-dimensional column span all of whose nonzero forms have column count c >= cmin, the model
R = F_3[t]/(t_j^2, sum t_j) is free over the span's forms through degree K exactly when the prediction [q^t] HS_R/(1+q+q^2)^d
stays positive for t <= K; the excess is reported per degree for random robust spans at each n.  Degree-t work is exact GF(3)
rank on C(n,t) squarefree monomials (compiled gf3), small for n <= 16, K <= 4.
Usage: python3 model_scaling_n.py --d 3 --ns 8,9,...,16 --K 4 --cmin 5 --trials 2 --seed 1 --out OUT.json"""
import itertools, json, os, sys
import numpy as np
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'odd_prime_alignment_mechanism_20260922')); import gf3
a = dict(zip(sys.argv[1::2], sys.argv[2::2])); d = int(a['--d']); K = int(a['--K']); cmin = int(a['--cmin']); tr = int(a['--trials'])
ns = [int(x) for x in a['--ns'].split(',')]; rng = np.random.default_rng(int(a['--seed']))
def hf(n, lins):
    H = [1]; L = np.array(lins, dtype=np.int64) % 3
    for k in range(1, K + 1):
        Bk = list(itertools.combinations(range(n), k)); idx = {b: i for i, b in enumerate(Bk)}
        low = list(itertools.combinations(range(n), k - 1)); rows = np.zeros((len(low) * len(L), len(Bk)), dtype=np.uint8)
        for si, S in enumerate(low):
            Ss = set(S); cols = [(j, idx[tuple(sorted(S + (j,)))]) for j in range(n) if j not in Ss]
            jj = np.array([c[0] for c in cols]); cc = np.array([c[1] for c in cols])
            rows[si * len(L):(si + 1) * len(L)][:, cc] = L[:, jj]
        H.append(len(Bk) - int(gf3.rank(rows)))
    return H
def divq(base, m):
    inv = [{0: 1, 1: -1, 2: 0}[i % 3] for i in range(K + 1)]; c = [1] + [0] * K
    for _ in range(m): c = [sum(c[i] * inv[s - i] for i in range(s + 1)) for s in range(K + 1)]
    return [sum(base[i] * c[s - i] for i in range(s + 1)) for s in range(K + 1)]
dirs = [np.array(c) for c in itertools.product(range(3), repeat=d) if any(c) and c[next(i for i, x in enumerate(c) if x)] == 1]
out = []
for n in ns:
    for t in range(tr):
        for _ in range(200000):
            P = rng.integers(0, 3, size=(d, n))
            if min(n - np.bincount((u @ P) % 3, minlength=3).max() for u in dirs) >= cmin: break
        else: continue
        HR = hf(n, [[1] * n]); H = hf(n, [[1] * n] + P.tolist()); W = divq(HR, d)
        row = dict(n=n, trial=t, phis=P.tolist(), HR=HR, H=H, free=W, excess=[h - w for h, w in zip(H, W)])
        out.append(row); print(n, t, 'free', W, 'H', H, 'excess', row['excess'], flush=True)
json.dump(out, open(a['--out'], 'w'), indent=1)
