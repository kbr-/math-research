"""Consistency check of the wide single-dependency threshold over F_3.
Family in normal form: coordinates u_1..u_t, and for each clause b = 1..t+1 its own extra coordinates w_b (k_b - 1 of
them).  Clause b <= t forbids {u_b = 0, w_b = 0}; clause t+1 forbids {u_1+...+u_t = c, w_{t+1} = 0}.
Predicted: degreewise locality holds for e < ceil(t/2) + 2*sum_b (k_b - 1), and fails there for c = t + w0.
Usage: python3 wide_single.py OUT.json t:k_1,...,k_{t+1}:c [...]"""
import itertools, json, sys, time
import numpy as np
exec(open(__file__.replace('odd_prime_wide_dependency_20260924/wide_single.py',
                           'odd_prime_t_wise_locality_20260924/form_locality.py')).read().split('def indep_t')[0])
out = sys.argv[1]; res = []
for case in sys.argv[2:]:
    t, ks, c = case.split(':'); t = int(t); ks = [int(x) for x in ks.split(',')]; c = int(c); t0 = time.time()
    wpos = []; pos = t
    for kb in ks: wpos.append(list(range(pos, pos + kb - 1))); pos += kb - 1
    s = pos; pts = np.array(list(itertools.product(range(p), repeat=s)), dtype=np.int64)
    forb = []
    for b in range(t + 1):
        ucond = (pts[:, b] == 0) if b < t else (pts[:, :t].sum(axis=1) % p == c)
        wcond = np.all(pts[:, wpos[b]] == 0, axis=1) if wpos[b] else np.ones(len(pts), bool)
        forb.append(ucond & wcond)
    forb = np.stack(forb, axis=1); Z = ~forb.any(axis=1)
    mons_all = sorted(itertools.product(range(p), repeat=s), key=sum); degs = np.array([sum(m) for m in mons_all])
    pred = -(-t // 2) + 2 * sum(kb - 1 for kb in ks); defects = []
    for e in range(0, pred + 1):
        ms = [m for m in mons_all if sum(m) <= e]
        E = np.ones((len(ms), len(pts)), dtype=np.int64)
        for i, m in enumerate(ms):
            for j in range(s):
                if m[j]: E[i] = E[i] * (pts[:, j] ** m[j]) % p
        IZ = null_left(E[:, Z]); parts = [null_left(E[:, ~forb[:, b]]) for b in range(t + 1)]
        parts = [q for q in parts if len(q)]; sm = rank(np.vstack(parts)) if parts else 0
        defects.append(len(IZ) - sm)
    row = dict(case=case, s=s, predicted_threshold=pred, defects=defects, seconds=round(time.time() - t0, 1))
    res.append(row); print(json.dumps(row), flush=True); json.dump(res, open(out, 'w'), indent=1)
