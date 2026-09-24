"""AND of r copies of the canonical single-dependency selector family over F_3: coordinates y^(j) in F_3^t (j = 1..r);
clause b <= t forbids {y^(j)_b = 0 for all j}, clause t+1 forbids {sum_i y^(j)_i = c_j for all j}.
Every t clauses have independent forms, rank r*t, dependency space of dimension r.
Conjectured threshold: ceil(t/2) + 2*t*(r-1) (the rank formula ceil(t/2) + (p-1)(rank - t)); failure proved at that
degree for c_1 = t + w_0, c_j = 0 (j >= 2).  Reports the first failing degree for the listed value vectors.
Usage: python3 and_family.py OUT.json t:r:c_1,...,c_r [...]"""
import itertools, json, sys, time
import numpy as np
exec(open(__file__.replace('odd_prime_double_dependency_20260924/and_family.py',
                           'odd_prime_t_wise_locality_20260924/form_locality.py')).read().split('def indep_t')[0])
out = sys.argv[1]; res = []
for case in sys.argv[2:]:
    t, r, cs = case.split(':'); t = int(t); r = int(r); cs = [int(x) for x in cs.split(',')]; s = t * r; t0 = time.time()
    pts = np.array(list(itertools.product(range(p), repeat=s)), dtype=np.int64)
    Y = [pts[:, j * t:(j + 1) * t] for j in range(r)]
    forb = [np.all(np.stack([Y[j][:, b] == 0 for j in range(r)]), axis=0) for b in range(t)]
    forb.append(np.all(np.stack([Y[j].sum(axis=1) % p == cs[j] for j in range(r)]), axis=0))
    forb = np.stack(forb, axis=1); Z = ~forb.any(axis=1)
    mons_all = sorted(itertools.product(range(p), repeat=s), key=sum); pred = -(-t // 2) + 2 * t * (r - 1); first = None
    for e in range(0, pred + 1):
        ms = [m for m in mons_all if sum(m) <= e]
        E = np.ones((len(ms), len(pts)), dtype=np.int64)
        for i, m in enumerate(ms):
            for j in range(s):
                if m[j]: E[i] = E[i] * (pts[:, j] ** m[j]) % p
        IZ = null_left(E[:, Z]); parts = [null_left(E[:, ~forb[:, b]]) for b in range(t + 1)]
        parts = [q for q in parts if len(q)]
        if len(IZ) - (rank(np.vstack(parts)) if parts else 0): first = e; break
    row = dict(case=case, predicted=pred, first_failure=first, seconds=round(time.time() - t0, 1))
    res.append(row); print(json.dumps(row), flush=True); json.dump(res, open(out, 'w'), indent=1)
