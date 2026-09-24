"""Test of the sharp form-space selector locality: over F_3, for selectors (hyperplanes {L_b = v_b}) in F_3^s whose
linear parts are t-wise independent, I_e(n U_b) = sum_b I_e(U_b) for every e with 2e + 1 <= t.
(The pairing obstruction shows 2e + 1 <= t cannot be weakened to 2e <= t.)
Families: greedy random t-wise independent linear parts (each new vector keeps every <= t subset independent),
M as large as the greedy reaches (capped), random values.  Reports the defect for e = 1 .. emax.
Usage: python3 sharp_locality.py OUT.json s:t:Mcap:trials:emax:seed [...]"""
import itertools, json, random, sys, time
import numpy as np
exec(open(__file__.replace('odd_prime_t_wise_proof_20260924/sharp_locality.py',
                           'odd_prime_t_wise_locality_20260924/form_locality.py')).read().split('def indep_t')[0])
def twise_ok(vecs, t):
    new = vecs[-1]
    for size in range(0, min(t, len(vecs)) ):
        for S in itertools.combinations(range(len(vecs) - 1), size):
            if rank(np.array([vecs[i] for i in S] + [new], dtype=np.int64)) < size + 1: return False
    return True
out = sys.argv[1]; res = []
for case in sys.argv[2:]:
    s, t, Mcap, trials, emax, seed = map(int, case.split(':')); rnd = random.Random(seed)
    pts = np.array(list(itertools.product(range(p), repeat=s)), dtype=np.int64)
    mons_all = sorted(itertools.product(range(p), repeat=s), key=sum); t0 = time.time()
    for tr in range(trials):
        vecs = []; fails = 0
        while len(vecs) < Mcap and fails < 400:
            v = [rnd.randrange(p) for _ in range(s)]
            if not any(v): continue
            vecs.append(v)
            if not twise_ok(vecs, t): vecs.pop(); fails += 1
        vals = [rnd.randrange(p) for _ in vecs]; M = len(vecs)
        L = (pts @ np.array(vecs, dtype=np.int64).T) % p
        forb = (L == np.array(vals)[None, :])
        Zmask = ~forb.any(axis=1); defects = []
        for e in range(1, emax + 1):
            mons = [m for m in mons_all if sum(m) <= e]
            E = np.ones((len(mons), len(pts)), dtype=np.int64)
            for i, m in enumerate(mons):
                for j in range(s):
                    if m[j]: E[i] = E[i] * (pts[:, j] ** m[j]) % p
            IZ = null_left(E[:, Zmask]) if Zmask.any() else np.eye(len(mons), dtype=np.int64)
            parts = [null_left(E[:, ~forb[:, b]]) for b in range(M)]; parts = [q for q in parts if len(q)]
            sm = rank(np.vstack(parts)) if parts else 0
            defects.append(len(IZ) - sm)
        row = dict(case=case, trial=tr, s=s, t=t, M=M, allowed=int(Zmask.sum()), vecs=vecs, vals=vals, defects=defects)
        res.append(row); print(json.dumps({x: row[x] for x in ('case', 'trial', 'M', 'allowed', 'defects')}), flush=True)
        json.dump(res, open(out, 'w'), indent=1)
    print('case done', case, round(time.time() - t0, 1), flush=True)
