"""Worst-direction criterion for column spans in the column model R = F_3[t]/(t_j^2, sum t_j).

Tested statement: for a d-dimensional column span with minimum column count c_min over its nonzero directions, and n such
that the free prediction [q^s] HS_R/(1+q+q^2)^d is positive for s <= t, the span is free through degree t iff c_min >= 2t-1
(the single-form threshold: one column form with count c is free exactly through degree ceil(c/2)).  Draws random hole
functions with a prescribed c_min (rejection), computes the model HF through degree t (compiled gf3 ranks).
Usage: python3 worst_direction.py --d 3 --t 4 --ns 15,16,17,18 --cmins 5,6,7,8 --trials 3 --seed 1 --out OUT.json"""
import itertools, json, os, sys
import numpy as np
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'odd_prime_alignment_mechanism_20260922')); import gf3
a = dict(zip(sys.argv[1::2], sys.argv[2::2])); d = int(a['--d']); T = int(a['--t']); tr = int(a['--trials'])
ns = [int(x) for x in a['--ns'].split(',')]; cmins = [int(x) for x in a['--cmins'].split(',')]; rng = np.random.default_rng(int(a['--seed']))
dirs = [np.array(c) for c in itertools.product(range(3), repeat=d) if any(c) and c[next(i for i, x in enumerate(c) if x)] == 1]
def cmin_of(P): return min(P.shape[1] - np.bincount((u @ P) % 3, minlength=3).max() for u in dirs)
def hf(n, lins):
    H = [1]; Lm = np.array(lins, dtype=np.int64) % 3
    for k in range(1, T + 1):
        Bk = list(itertools.combinations(range(n), k)); idx = {b: i for i, b in enumerate(Bk)}
        low = list(itertools.combinations(range(n), k - 1)); rows = np.zeros((len(low) * len(Lm), len(Bk)), dtype=np.uint8)
        for si, S in enumerate(low):
            Ss = set(S); cols = [(j, idx[tuple(sorted(S + (j,)))]) for j in range(n) if j not in Ss]
            jj = np.array([c[0] for c in cols]); cc = np.array([c[1] for c in cols])
            rows[si * len(Lm):(si + 1) * len(Lm)][:, cc] = Lm[:, jj]
        H.append(len(Bk) - int(gf3.rank(rows)))
    return H
def divq(base, m):
    inv = [{0: 1, 1: -1, 2: 0}[i % 3] for i in range(T + 1)]; c = [1] + [0] * T
    for _ in range(m): c = [sum(c[i] * inv[s - i] for i in range(s + 1)) for s in range(T + 1)]
    return [sum(base[i] * c[s - i] for i in range(s + 1)) for s in range(T + 1)]
out = []; agree = disagree = 0
for n in ns:
    HR = hf(n, [[1] * n])
    for cm in cmins:
        for t_ in range(tr):
            P = None
            for _ in range(400000):
                Q = rng.integers(0, 3, size=(d, n))
                if cmin_of(Q) == cm: P = Q; break
            if P is None: continue
            H = hf(n, [[1] * n] + P.tolist()); W = divq(HR, d)
            positive = all(w > 0 for w in W); free = (H == W); predicted = cm >= 2 * T - 1
            ok = (free == predicted) if positive else None
            agree += ok is True; disagree += ok is False
            out.append(dict(n=n, d=d, t=T, c_min=cm, phis=P.tolist(), H=H, free_pred=W, positive=positive, free=free, predicted_free=predicted, agrees=ok))
            print(n, 'c_min', cm, 'H', H, 'pred', W, 'free', free, 'criterion', predicted, 'positive' if positive else 'nonpositive', flush=True)
print('agree', agree, 'disagree', disagree, flush=True)
json.dump(out, open(a['--out'], 'w'), indent=1)
