"""First non-free degree of M = (u(W)/m^2)^{(x)N} over u(W) = F_3[w_1..w_d]/(w^3), W acting diagonally.

Tested statement: M is free through t over u(W) iff HF(M/mM)_k = [q^k] HS_M/(1+q+q^2)^d for all k <= t
(the openness lemma of thm:projection-freeness, cover form). HS_M = (1+dq)^N. M_k has basis (S, labels): a
k-subset S of the N columns and a label in {1..d} per column of S; w_b sends (S, lab) to the sum over j not in S
of (S + j, lab with b at j). Ranks of W (x) M_{k-1} -> M_k are exact over F_3 (vectorized elimination).
Reports the largest t with M free through t, for small (N, d), capped by matrix size.
Usage: python3 tensor_power.py OUT.json"""
import itertools, json, sys, time
import numpy as np
p = 3

def rank_mod3(M):
    M = (M % p).astype(np.int8); r = 0; rows, cols = M.shape
    for c in range(cols):
        if r == rows: break
        nz = np.nonzero(M[r:, c])[0]
        if len(nz) == 0: continue
        piv = r + nz[0]
        if piv != r: M[[r, piv]] = M[[piv, r]]
        if M[r, c] == 2: M[r] = (M[r] * 2) % p
        below = np.nonzero(M[:, c])[0]; below = below[below != r]
        if len(below): M[below] = (M[below] - np.outer(M[below, c], M[r])) % p
        r += 1
    return r

def basis(N, d, k):
    return [(S, lab) for S in itertools.combinations(range(N), k) for lab in itertools.product(range(d), repeat=k)]

def hf_quotient(N, d, k):
    if k == 0: return 1
    tgt = {b: i for i, b in enumerate(basis(N, d, k))}; src = basis(N, d, k - 1)
    rows = np.zeros((d * len(src), len(tgt)), dtype=np.int8)
    for r, (b, (S, lab)) in enumerate(itertools.product(range(d), src)):
        full = dict(zip(S, lab))
        for j in set(range(N)) - set(S):
            g = dict(full); g[j] = b; T = tuple(sorted(g))
            rows[r, tgt[(T, tuple(g[x] for x in T))]] = 1
    return len(tgt) - rank_mod3(rows)

def pred(N, d, t):
    hs = [sum(1 for _ in [0]) * 0 for _ in range(t + 1)]
    from math import comb
    hs = [comb(N, k) * d ** k for k in range(t + 1)]
    inv = [{0: 1, 1: -1, 2: 0}[k % 3] for k in range(t + 1)]
    ser = [1] + [0] * t
    for _ in range(d): ser = [sum(ser[a] * inv[k - a] for a in range(k + 1)) for k in range(t + 1)]
    return [sum(hs[a] * ser[k - a] for a in range(k + 1)) for k in range(t + 1)]

out = sys.argv[1]; res = []; CAP = 6000
for N in range(2, 9):
    for d in range(1, 5):
        t0 = time.time(); free_through = -1; hf = []
        for k in range(0, N + 1):
            from math import comb
            if comb(N, k) * d ** k > CAP: break
            h = hf_quotient(N, d, k); hf.append(h)
            if h != pred(N, d, k)[k]: break
            free_through = k
        rec = dict(N=N, d=d, free_through=free_through, checked_to=len(hf) - 1, hf_quotient=hf,
                   pred=pred(N, d, len(hf) - 1), seconds=round(time.time() - t0, 2))
        res.append(rec); print(json.dumps(rec), flush=True)
json.dump(res, open(out, 'w'), indent=1)
