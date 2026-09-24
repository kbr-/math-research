"""Dense form-space locality: over F_3, random clauses (k affine forms each, forbidden set {L_b = v_b}) on F_3^s,
kept only when the allowed set Z has density >= 1/2; no independence imposed (the family's t is recorded).
Tested statement: I_e(n U_b) = sum_b I_e(U_b) for every e <= 2s (does density alone give degreewise locality?).
Usage: python3 dense_locality.py OUT.json s:k:M:trials:seed [...]"""
import itertools, json, random, sys, time
import numpy as np
exec(open(__file__.replace('odd_prime_t_wise_proof_20260924/dense_locality.py',
                           'odd_prime_t_wise_locality_20260924/form_locality.py')).read().split('out = sys.argv[1]')[0])
out = sys.argv[1]; res = []
for case in sys.argv[2:]:
    s, k, M, trials, seed = map(int, case.split(':')); rnd = random.Random(seed)
    pts = np.array(list(itertools.product(range(p), repeat=s)), dtype=np.int64)
    mons_all = sorted(itertools.product(range(p), repeat=s), key=sum)
    Efull = np.ones((len(mons_all), len(pts)), dtype=np.int64)
    for i, m in enumerate(mons_all):
        for j in range(s):
            if m[j]: Efull[i] = Efull[i] * (pts[:, j] ** m[j]) % p
    degs = np.array([sum(m) for m in mons_all]); t0 = time.time(); done = 0
    while done < trials:
        lins = [[rnd.randrange(p) for _ in range(s)] for _ in range(M * k)]
        if any(not any(l) for l in lins): continue
        vals = [rnd.randrange(p) for _ in range(M * k)]
        L = (pts @ np.array(lins, dtype=np.int64).T) % p
        forb = np.stack([(L[:, b * k:(b + 1) * k] == np.array(vals[b * k:(b + 1) * k])[None, :]).all(axis=1) for b in range(M)], axis=1)
        Z = ~forb.any(axis=1)
        if Z.sum() * 2 < len(pts): continue
        done += 1; defects = []
        for e in range(0, 2 * s + 1):
            E = Efull[degs <= e]
            IZ = null_left(E[:, Z]); parts = [null_left(E[:, ~forb[:, b]]) for b in range(M)]
            parts = [q for q in parts if len(q)]; sm = rank(np.vstack(parts)) if parts else 0
            defects.append(len(IZ) - sm)
        row = dict(case=case, s=s, k=k, M=M, t=indep_t(lins, k), density=round(float(Z.mean()), 3), lins=lins, vals=vals, defects=defects)
        res.append(row); print(json.dumps({x: row[x] for x in ('case', 't', 'density', 'defects')}), flush=True)
        json.dump(res, open(out, 'w'), indent=1)
    print('case done', case, round(time.time() - t0, 1), flush=True)
