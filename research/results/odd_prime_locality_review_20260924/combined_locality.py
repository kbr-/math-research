"""Falsification attempt for locality under independence and sparsity together, in form space over F_3.
Families: M clauses of k = 2 affine forms on F_3^6, with every t clauses' combined linear parts independent
(t = 3, so any 3 clauses' 6 forms form a basis), random forbidden values; the forbidden union has density <= 1/2.
M = 3 is the fully independent control (locality holds by the product argument); M = 4, 5 are dependent families.
Tested statement: I_e(n U_b) = sum_b I_e(U_b) for every e <= 12.
Usage: python3 combined_locality.py OUT.json M:trials:seed [...]"""
import itertools, json, random, sys, time
import numpy as np
exec(open(__file__.replace('odd_prime_locality_review_20260924/combined_locality.py',
                           'odd_prime_t_wise_locality_20260924/form_locality.py')).read().split('out = sys.argv[1]')[0])
s, k, t = 6, 2, 3
out = sys.argv[1]; res = []
pts = np.array(list(itertools.product(range(p), repeat=s)), dtype=np.int64)
mons_all = sorted(itertools.product(range(p), repeat=s), key=sum)
Efull = np.ones((len(mons_all), len(pts)), dtype=np.int64)
for i, m in enumerate(mons_all):
    for j in range(s):
        if m[j]: Efull[i] = Efull[i] * (pts[:, j] ** m[j]) % p
degs = np.array([sum(m) for m in mons_all])
for case in sys.argv[2:]:
    M, trials, seed = map(int, case.split(':')); rnd = random.Random(seed); t0 = time.time(); done = 0
    while done < trials:
        lins = [[rnd.randrange(p) for _ in range(s)] for _ in range(M * k)]
        if indep_t(lins, k) < min(t, M): continue
        vals = [rnd.randrange(p) for _ in range(M * k)]
        L = (pts @ np.array(lins, dtype=np.int64).T) % p
        forb = np.stack([(L[:, b * k:(b + 1) * k] == np.array(vals[b * k:(b + 1) * k])[None, :]).all(axis=1) for b in range(M)], axis=1)
        Z = ~forb.any(axis=1)
        assert Z.mean() >= 0.5
        done += 1; defects = []
        for e in range(0, 13):
            E = Efull[degs <= e]
            IZ = null_left(E[:, Z]); parts = [null_left(E[:, ~forb[:, b]]) for b in range(M)]
            parts = [q for q in parts if len(q)]; sm = rank(np.vstack(parts)) if parts else 0
            defects.append(len(IZ) - sm)
        row = dict(case=case, M=M, t=indep_t(lins, k), density_forbidden=round(1 - float(Z.mean()), 3), lins=lins, vals=vals, defects=defects,
                   seconds=round(time.time() - t0, 1))
        res.append(row); print(json.dumps({x: row[x] for x in ('case', 't', 'density_forbidden', 'defects', 'seconds')}), flush=True)
        json.dump(res, open(out, 'w'), indent=1)
