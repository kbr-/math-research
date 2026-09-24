"""Degreewise locality for budget-type clauses in form space over F_3: each clause forbids 'all its forms nonzero'
(allowed: some form = 0).  Normal form of one dependency: clause b <= t has forms (y_b, private w_b), clause t+1 has
forms (y_1 + ... + y_t - c, private w_{t+1}); k_b - 1 private forms each.
Tested statement: locality I_e(n U_b) = sum_b I_e(U_b) holds at every degree when c = 0 (consistent cluster), and
first fails at 2 sum_b (k_b - 1) when c != 0 (inconsistent; failure proved by prop:member-inconsistency).
Usage: python3 budget_type.py OUT.json t:k_1,...,k_{t+1}:c [...]"""
import itertools, json, sys, time
import numpy as np
exec(open(__file__.replace('odd_prime_cluster_freeness_20260924/budget_type.py',
                           'odd_prime_t_wise_locality_20260924/form_locality.py')).read().split('def indep_t')[0])
out = sys.argv[1]; res = []
for case in sys.argv[2:]:
    t, ks, c = case.split(':'); t = int(t); ks = [int(x) for x in ks.split(',')]; c = int(c); t0 = time.time()
    wpos = []; pos = t
    for kb in ks: wpos.append(list(range(pos, pos + kb - 1))); pos += kb - 1
    s = pos; pts = np.array(list(itertools.product(range(p), repeat=s)), dtype=np.int64)
    forb = []
    for b in range(t + 1):
        ynz = (pts[:, b] != 0) if b < t else ((pts[:, :t].sum(axis=1) - c) % p != 0)
        wnz = np.all(pts[:, wpos[b]] != 0, axis=1) if wpos[b] else np.ones(len(pts), bool)
        forb.append(ynz & wnz)
    forb = np.stack(forb, axis=1); Z = ~forb.any(axis=1)
    mons_all = sorted(itertools.product(range(p), repeat=s), key=sum); defects = []
    for e in range(0, 2 * s + 1):
        ms = [m for m in mons_all if sum(m) <= e]
        E = np.ones((len(ms), len(pts)), dtype=np.int64)
        for i, m in enumerate(ms):
            for j in range(s):
                if m[j]: E[i] = E[i] * (pts[:, j] ** m[j]) % p
        IZ = null_left(E[:, Z]) if Z.any() else np.eye(len(ms), dtype=np.int64)
        parts = [null_left(E[:, ~forb[:, b]]) for b in range(t + 1)]; parts = [q for q in parts if len(q)]
        defects.append(len(IZ) - (rank(np.vstack(parts)) if parts else 0))
    row = dict(case=case, s=s, allowed=int(Z.sum()), predicted_inconsistent=2 * sum(kb - 1 for kb in ks), defects=defects,
               seconds=round(time.time() - t0, 1))
    res.append(row); print(json.dumps(row), flush=True); json.dump(res, open(out, 'w'), indent=1)
