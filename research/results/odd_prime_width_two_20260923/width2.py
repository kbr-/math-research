"""Local-fall test at width 2 (the first product width of the logarithmic-prefix reduction's clauses).

Clauses: (L1)^2 (L2)^2 = 0, i.e. L1 = 0 or L2 = 0, for affine forms, on weak unary PHP^{n+1}_n, PC closure at degree D.
Tested statement (conj:local-falls, low part): for a confined family (clauses on pairs of distinct directions of the span
W of d random affine forms, each clause vanishing at a planted point z, so satisfiable on the span) planted before a
random clause sequence, the degree-<D part of the closure equals the random sequence's own measured low part plus the
family's own low change, at every M before refutation; refutation comes near the random run's crossing shifted by the
family.  Also recorded: the random sequence's split per M (the baseline) and the top part.
Asserted: every family clause vanishes at z; the two forms of each clause have independent directions.
Usage: --n 5 --D 5 --configs d:m,... --Mmax K --seed S --out PATH"""
import argparse, itertools, json, os, sys, time
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.join(HERE, '..', 'odd_prime_local_falls_20260923'))
from local_falls import Closure, QSpace, base_rows, random_eq, add_forms
def mul(P, Q):
    out = {}
    for m1, a1 in P.items():
        for m2, a2 in Q.items():
            mon = tuple(sorted(set(m1 + m2))); out[mon] = (out.get(mon, 0) + a1 * a2) % 3
    return {m: a for m, a in out.items() if a}
def clause(L1, L2): return mul(mul(L1, L1), mul(L2, L2))
def family(rng, v, d, m):
    A = [random_eq(rng, v) for _ in range(d)]; z = rng.integers(0, 3, size=d)
    dirs = [c for c in itertools.product(range(3), repeat=d) if any(c) and c[next(i for i in range(d) if c[i])] == 1]
    out, seen = [], set()
    while len(out) < m:
        i, j = rng.choice(len(dirs), size=2, replace=False)
        if (i, j) in seen: continue
        seen.add((i, j)); c1, c2 = dirs[i], dirs[j]
        v1, v2 = int(np.dot(c1, z) % 3), int(np.dot(c2, z) % 3)
        f1 = v1 if rng.random() < 0.5 else int(rng.integers(0, 3)); f2 = int(rng.integers(0, 3)) if f1 == v1 else v2
        assert f1 == v1 or f2 == v2                                   # the clause holds at z
        L1 = add_forms(*[(ct, A[t]) for t, ct in enumerate(c1) if ct], (1, {(): (-f1) % 3}))
        L2 = add_forms(*[(ct, A[t]) for t, ct in enumerate(c2) if ct], (1, {(): (-f2) % 3}))
        out.append(clause(L1, L2))
    return out
ap = argparse.ArgumentParser(); ap.add_argument('--n', type=int, default=5); ap.add_argument('--D', type=int, default=5)
ap.add_argument('--configs', default=''); ap.add_argument('--Mmax', type=int, default=200); ap.add_argument('--seed', type=int, default=1)
ap.add_argument('--threads', type=int, default=12); ap.add_argument('--out', required=True)
a = ap.parse_args(); t0 = time.time(); sp = QSpace(a.n, a.D); v = sp.v; top = int((sp.deg == a.D).sum())
rng = np.random.default_rng(7000 + a.seed); rand = [clause(random_eq(rng, v), random_eq(rng, v)) for _ in range(a.Mmax)]
C = Closure(sp, a.threads); C.add(base_rows(a.n)); base = C.split()
print(f'n={a.n} D={a.D}: columns {sp.cols}, top {top}; base {base} ({time.time()-t0:.0f}s)', flush=True)
res = dict(n=a.n, D=a.D, seed=a.seed, columns=sp.cols, top_columns=top, base=base, random=[], families=[])
for M in range(1, a.Mmax + 1):
    C.add(rand[M - 1:M]); s = C.split(); res['random'].append(dict(M=M, **s))
    if M % 10 == 0 or s['refuted']: print(f'  random M={M}: {s} ({time.time()-t0:.0f}s)', flush=True)
    if s['refuted']: break
json.dump(res, open(a.out, 'w'), indent=1)
rlow = {r['M']: r['low'] for r in res['random']}; rlow[0] = base['low']
for cfg in [c for c in a.configs.split(',') if c]:
    d, m = map(int, cfg.split(':')); fam = family(np.random.default_rng(1000 * a.seed + 17 * d + m), v, d, m)
    Cm = Closure(sp, a.threads); Cm.add(base_rows(a.n) + fam); s = Cm.split()
    own = dict(low=s['low'] - base['low'], top=s['top'] - base['top'], refuted=s['refuted'])
    Cf = Closure(sp, a.threads); Cf.add(base_rows(a.n) + fam); rows = [dict(M=0, **Cf.split())]
    for M in range(1, len(res['random']) + 1):
        if rows[-1]['refuted']: break
        Cf.add(rand[M - 1:M]); rows.append(dict(M=M, **Cf.split()))
    for r in rows:
        r['pred_low'] = rlow.get(r['M'], None) + own['low'] if r['M'] in rlow else None
        r['excess_low'] = r['low'] - r['pred_low'] if r['pred_low'] is not None else None
    ok = [r for r in rows if not r['refuted']]
    res['families'].append(dict(d=d, m=m, own=own, rows=rows, max_excess_low=max((r['excess_low'] for r in ok), default=None),
                                refuted_M=next((r['M'] for r in rows if r['refuted']), None)))
    json.dump(res, open(a.out, 'w'), indent=1)
    f = res['families'][-1]
    print(f'd={d} m={m}: own {own}; max low excess before refutation {f["max_excess_low"]}; refuted at M={f["refuted_M"]} ({time.time()-t0:.0f}s)', flush=True)
