"""Hilbert function of T_r/(m_1^2..m_n^2), T_r = F_3[s_1..s_r]/(s_i^3) (the group algebra of (Z/3)^r), for the Gale vectors m_j of
column-model configurations, against n uniform random vectors in F_3^r (5 draws) and the column-model free prediction.

Tested statements: (1) the Gale reduction: HF(T_r/(m_j^2)) equals the column model's HF (by prop:column-model-gale and
m^3 = 0 in characteristic 3); (2) whether the model's degree-4/5 defects are special to the configuration (random vectors
reach the free prediction) or forced (random vectors fall short too).  Exact GF(3) ranks (compiled gf3).
Usage: python3 tr_squares.py IN.json... --K 5 --out OUT.json"""
import itertools, json, os, sys
import numpy as np
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'odd_prime_alignment_mechanism_20260922')); import gf3
exec(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'gale_flats.py')).read().split('def flat_stats')[0].split('import itertools, json, sys')[1])
def monos(r, t): return [e for e in itertools.product(range(3), repeat=r) if sum(e) == t] if r <= 8 else list(_monos(r, t))
def _monos(r, t, start=0, cur=None):
    cur = cur or [0] * r
    if t == 0: yield tuple(cur); return
    for i in range(start, r):
        if cur[i] < 2:
            cur[i] += 1; yield from _monos(r, t - 1, i, cur); cur[i] -= 1
def hf(vecs, r, K):
    sq = []
    for v in vecs:
        q = {}
        for i in range(r):
            for j in range(i, r):
                c = (v[i] * v[j] * (1 if i == j else 2)) % 3
                if c:
                    e = [0] * r; e[i] += 1; e[j] += 1; q[tuple(e)] = (q.get(tuple(e), 0) + c) % 3
        sq.append(q)
    H = []
    for t in range(K + 1):
        Mt = sorted(set(monos(r, t))); idx = {m: k for k, m in enumerate(Mt)}
        if t < 2: H.append(len(Mt)); continue
        low = sorted(set(monos(r, t - 2))); rows = []
        for q in sq:
            for m in low:
                row = np.zeros(len(Mt), dtype=np.uint8)
                for e, c in q.items():
                    f = tuple(a + b for a, b in zip(m, e))
                    if max(f) <= 2: row[idx[f]] = (row[idx[f]] + c) % 3
                rows.append(row)
        H.append(len(Mt) - (int(gf3.rank(np.array(rows))) if rows else 0))
    return H
args = sys.argv[1:]; K = int(args[args.index('--K') + 1]); outp = args[args.index('--out') + 1]
ins = [x for x in args[:min(args.index('--K'), args.index('--out'))]]
rng = np.random.default_rng(7); res = []
for f in ins:
    for row in json.load(open(f)):
        n = row['n']; G = gale(row['phis']); r = G.shape[1]; Kr = min(K, len(row['H']) - 1)
        Hc = hf([list(x) for x in G], r, Kr)
        Hg = [hf([list(rng.integers(0, 3, size=r)) for _ in range(n)], r, Kr) for _ in range(5)]
        out = dict(n=n, trial=row['trial'], r=r, model_H=row['H'][:Kr + 1], free=row['free'][:Kr + 1], gale_H=Hc, generic_H=Hg,
                   gale_matches_model=(Hc == row['H'][:Kr + 1]))
        res.append(out)
        print(n, row['trial'], 'model', out['model_H'], 'gale', Hc, 'match', out['gale_matches_model'], 'free', out['free'], 'generic', sorted(map(tuple, Hg))[:2], flush=True)
json.dump(res, open(outp, 'w'), indent=1)
