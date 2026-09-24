"""First failing degree of degreewise locality for families with a dependency space of dimension 2, over F_3.
Families: M clauses of width k on F_3^s with combined linear parts of rank M*k - 2 and every tmin clauses independent
(general position; tmin = M-1 for wide clauses, s for selectors), all forbidden points scanned up to translation (values of the non-coordinate forms), linear parts
random subject to these conditions.  Reports, per family, the minimum over values of the first failing degree.
Usage: python3 double_base.py OUT.json s:k:M:trials:seed:tmin [...]"""
import itertools, json, random, sys, time
import numpy as np
exec(open(__file__.replace('odd_prime_double_dependency_20260924/double_base.py',
                           'odd_prime_t_wise_locality_20260924/form_locality.py')).read().split('out = sys.argv[1]')[0])
out = sys.argv[1]; res = []
for case in sys.argv[2:]:
    s, k, M, trials, seed, tmin = map(int, case.split(':')); rnd = random.Random(seed); t0 = time.time()
    pts = np.array(list(itertools.product(range(p), repeat=s)), dtype=np.int64)
    mons_all = sorted(itertools.product(range(p), repeat=s), key=sum); degs = np.array([sum(m) for m in mons_all])
    Efull = np.ones((len(mons_all), len(pts)), dtype=np.int64)
    for i, m in enumerate(mons_all):
        for j in range(s):
            if m[j]: Efull[i] = Efull[i] * (pts[:, j] ** m[j]) % p
    done = 0
    while done < trials:
        lins = [[rnd.randrange(p) for _ in range(s)] for _ in range(M * k)]
        if rank(np.array(lins)) != M * k - 2 or indep_t(lins, k) < tmin: continue
        done += 1; firsts = []
        # values: the first s independent forms can be translated to 0; scan values of the remaining forms
        L = (pts @ np.array(lins, dtype=np.int64).T) % p
        for extra in itertools.product(range(p), repeat=2):
            vals = [0] * (M * k)
            vals[-2:] = list(extra)
            forb = np.stack([(L[:, b * k:(b + 1) * k] == np.array(vals[b * k:(b + 1) * k])[None, :]).all(axis=1) for b in range(M)], axis=1)
            Z = ~forb.any(axis=1); first = None
            for e in range(0, 2 * s + 1):
                E = Efull[degs <= e]
                IZ = null_left(E[:, Z]) if Z.any() else np.eye(len(E), dtype=np.int64)
                parts = [null_left(E[:, ~forb[:, b]]) for b in range(M)]; parts = [q for q in parts if len(q)]
                if len(IZ) - (rank(np.vstack(parts)) if parts else 0): first = e; break
            firsts.append(first)
        row = dict(case=case, lins=lins, firsts=firsts, min_first=min(f for f in firsts if f is not None) if any(f is not None for f in firsts) else None,
                   seconds=round(time.time() - t0, 1))
        res.append(row); print(json.dumps({x: row[x] for x in ('case', 'firsts', 'min_first', 'seconds')}), flush=True)
        json.dump(res, open(out, 'w'), indent=1)
