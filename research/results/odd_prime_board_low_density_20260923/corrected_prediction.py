"""From n7_M8.json: (a) the component-corrected prediction HS_A * (model_H / (1+t+t^2)^3) * (1 - t^4/(1+t+t^2)^2)^(M - planted)
through degree 5 for each planted family, against the board's H; (b) the rank modulo row forms of the planted forms, of each
constraint's pair, and of the whole family (checks that the planted span is 3-dimensional on the board).  Usage: --out JSON"""
import json, os, sys
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); outp = sys.argv[sys.argv.index('--out') + 1]
d = json.load(open(os.path.join(HERE, 'n7_M8.json'))); g = d['gamma']; K = 5; n = d['n']
def mul(a, b): return [sum(a[i] * b[k - i] for i in range(k + 1)) for k in range(K + 1)]
inv = [{0: 1, 1: -1, 2: 0}[i % 3] for i in range(K + 1)]
def invpow(e):
    o = [1] + [0] * K
    for _ in range(e): o = mul(o, inv)
    return o
inv2 = mul(inv, inv); f0 = [(1 if k == 0 else 0) - (inv2[k - 4] if k >= 4 else 0) for k in range(K + 1)]
def rank3(M):
    M = np.array(M, dtype=np.int64) % 3; r = 0
    for c in range(M.shape[1]):
        piv = next((i for i in range(r, M.shape[0]) if M[i, c]), None)
        if piv is None: continue
        M[[r, piv]] = M[[piv, r]]; M[r] = (M[r] * M[r, c]) % 3
        for i in range(M.shape[0]):
            if i != r and M[i, c]: M[i] = (M[i] - M[i, c] * M[r]) % 3
        r += 1
    return r
def mod_rows(F):   # a form modulo the row forms: subtract each row's first entry (row functions up to constants)
    F = np.array(F) % 3; return ((F - F[:, :1]) % 3)[:, 1:].reshape(-1)
out = []
for r in d['runs']:
    if r['kind'] == 'random': continue
    npl = 3 if r['kind'] == 'triple' else 2
    W = mul(mul(g[:K + 1], mul(r['model_H'], invpow(3))), [1] + [0] * K)
    for _ in range(r['M'] - npl): W = mul(W, f0)
    V = [mod_rows(f) for f in r['forms']]
    rec = dict(kind=r['kind'], trial=r['trial'], corrected_W=W, board_H=r['H'], match=W == r['H'],
               planted_rank=rank3(V[:2 * npl]), pair_ranks=[rank3(V[2 * b:2 * b + 2]) for b in range(r['M'])], family_rank=rank3(V))
    out.append(rec); print(rec['kind'], rec['trial'], W[4:], r['H'][4:], rec['match'], 'planted rank', rec['planted_rank'], 'family rank', rec['family_rank'], 'pair ranks', set(rec['pair_ranks']))
json.dump(out, open(outp, 'w'), indent=1)
