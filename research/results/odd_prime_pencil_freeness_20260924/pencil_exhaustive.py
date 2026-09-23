"""Exhaustive test of conj:worst-direction-freeness for pencils (d = 2) in the column model R = F_3[t]/(t_j^2, sum t_j).

A pencil of column forms is determined, up to the symmetries that preserve the model's Hilbert functions (hole permutations,
change of basis of the pencil, adding constants since sum t = 0), by the multiset of value points (phi_1(j), phi_2(j)) in
F_3^2 up to the affine group AGL(2,3) (432 elements).  For every class with a genuinely 2-dimensional span (1, phi_1, phi_2
independent), computes c_min over the 4 rational directions and the model HF through degree t, and compares freeness
(HF = [q^s] HS_R/(1+q+q^2)^2 for s <= t) with the criterion c_min >= 2t-1, recording whether the prediction is positive.
Usage: python3 pencil_exhaustive.py --ns 9,10,11,12 --t 3 --out OUT.json"""
import itertools, json, os, sys, time
import numpy as np
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'odd_prime_alignment_mechanism_20260922')); import gf3
a = dict(zip(sys.argv[1::2], sys.argv[2::2])); T = int(a['--t']); ns = [int(x) for x in a['--ns'].split(',')]
PTS = [(x, y) for x in range(3) for y in range(3)]; PI = {p: i for i, p in enumerate(PTS)}
GROUP = []
for M in itertools.product(range(3), repeat=4):
    if (M[0] * M[3] - M[1] * M[2]) % 3 == 0: continue
    for b in itertools.product(range(3), repeat=2):
        GROUP.append([PI[((M[0] * x + M[1] * y + b[0]) % 3, (M[2] * x + M[3] * y + b[1]) % 3)] for (x, y) in PTS])
GROUP = np.array(GROUP); assert len(GROUP) == 432
def compositions(n, k):
    for c in itertools.combinations(range(n + k - 1), k - 1):
        prev = -1; out = []
        for x in c + (n + k - 1,): out.append(x - prev - 1); prev = x
        yield tuple(out)
def classes(n):
    seen = set(); reps = []
    for v in compositions(n, 9):
        if v in seen: continue
        arr = np.array(v); imgs = {tuple(arr[np.argsort(g)]) for g in GROUP}   # image of counts under the point permutation g
        seen |= imgs; reps.append(v)
    return reps
def hf(n, lins):
    H = [1]; L = np.array(lins, dtype=np.int64) % 3
    for k in range(1, T + 1):
        Bk = list(itertools.combinations(range(n), k)); idx = {b: i for i, b in enumerate(Bk)}
        low = list(itertools.combinations(range(n), k - 1)); rows = np.zeros((len(low) * len(L), len(Bk)), dtype=np.uint8)
        for si, S in enumerate(low):
            Ss = set(S); cols = [(j, idx[tuple(sorted(S + (j,)))]) for j in range(n) if j not in Ss]
            jj = np.array([c[0] for c in cols]); cc = np.array([c[1] for c in cols])
            rows[si * len(L):(si + 1) * len(L)][:, cc] = L[:, jj]
        H.append(len(Bk) - int(gf3.rank(rows)))
    return H
def divq(base, m):
    inv = [{0: 1, 1: -1, 2: 0}[i % 3] for i in range(T + 1)]; c = [1] + [0] * T
    for _ in range(m): c = [sum(c[i] * inv[s - i] for i in range(s + 1)) for s in range(T + 1)]
    return [sum(base[i] * c[s - i] for i in range(s + 1)) for s in range(T + 1)]
DIRS = [(1, 0), (0, 1), (1, 1), (1, 2)]
out = {}; t0 = time.time()
for n in ns:
    HR = hf(n, [[1] * n]); W = divq(HR, 2); positive = all(w > 0 for w in W)
    stats = dict(classes=0, degenerate=0, agree=0, disagree=0, exceptions=[])
    for v in classes(n):
        holes = [p for p, m in zip(PTS, v) for _ in range(m)]
        phi1 = [p[0] for p in holes]; phi2 = [p[1] for p in holes]
        if np.linalg.matrix_rank(np.array([[1] * n, phi1, phi2]) % 3) < 3 or \
           len({(1, x, y) for x, y in holes}) < 3: pass
        # genuine 2-dim span modulo constants: some direction nonconstant for both basis choices
        vals = [[(u[0] * x + u[1] * y) % 3 for x, y in holes] for u in DIRS]
        if any(len(set(vv)) == 1 for vv in vals): stats['degenerate'] += 1; continue
        stats['classes'] += 1
        cmin = min(n - max(vv.count(z) for z in range(3)) for vv in vals)
        H = hf(n, [[1] * n, phi1, phi2]); free = H == W; pred = cmin >= 2 * T - 1
        if free == pred: stats['agree'] += 1
        else:
            stats['disagree'] += 1; stats['exceptions'].append(dict(counts=v, c_min=cmin, H=H, free_pred=W))
    stats['positive_prediction'] = positive; stats['free_prediction'] = W
    out[n] = stats
    print(n, 't', T, {k: stats[k] for k in ('classes', 'degenerate', 'agree', 'disagree', 'positive_prediction')}, 'W', W, f'({time.time()-t0:.0f}s)', flush=True)
    for ex in stats['exceptions'][:3]: print('   exception', ex, flush=True)
json.dump(out, open(a['--out'], 'w'), indent=1)
