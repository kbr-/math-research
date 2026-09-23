"""Local-fall test for confined families (the adversary's strongest recorded move: many selectors in one subspace).

Tested statement (conj:local-falls, additive form): for a satisfiable selector family whose forms all lie in the span
W of d random affine forms A_1..A_d, planted before the recorded random selector sequence on weak unary PHP at n = 6,
degree D = 3, the degree split of the PC closure equals base + the family's own change (computed alone) + the random
selectors' recorded increments (+1 low, +34 top each), with refutation at the first M where the predicted top part
exceeds the degree-3 column count.  Family: m distinct directions c of F_3^d (up to sign), form L_c = sum_t c_t A_t,
forbidding one value f_c != c.z for a planted point z in F_3^d (so z satisfies every selector: satisfiable member).
Asserted: directions distinct up to sign; the planted point avoids every forbidden value.
Usage: --n 6 --D 3 --configs d:m,... --Ms ... --seed S --out PATH"""
import argparse, itertools, json, os, sys, time
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.join(HERE, '..', 'odd_prime_local_falls_20260923'))
from local_falls import Closure, QSpace, base_rows, random_eq, add_forms, sel, selector
def family(rng, v, d, m):
    A = [random_eq(rng, v) for _ in range(d)]; z = rng.integers(0, 3, size=d)
    dirs = [c for c in itertools.product(range(3), repeat=d) if any(c) and c[next(i for i in range(d) if c[i])] == 1]
    pick = [dirs[i] for i in rng.choice(len(dirs), size=m, replace=False)]
    out = []
    for c in pick:
        val = int(np.dot(c, z) % 3); f = int(rng.choice([x for x in range(3) if x != val])); assert f != val
        L = add_forms(*[(ct, A[t]) for t, ct in enumerate(c) if ct], (1, {(): (-f) % 3}))
        out.append(sel(L))                                   # 1 - (L_c - f)^2 = 0 forbids L_c = f
    return out
ap = argparse.ArgumentParser(); ap.add_argument('--n', type=int, default=6); ap.add_argument('--D', type=int, default=3)
ap.add_argument('--configs', default='4:4,4:8,4:16'); ap.add_argument('--Ms', default='0,10,20,30,40,50,60')
ap.add_argument('--seed', type=int, default=1); ap.add_argument('--threads', type=int, default=12); ap.add_argument('--out', required=True)
a = ap.parse_args(); t0 = time.time(); sp = QSpace(a.n, a.D); v = sp.v; cols = int((sp.deg == a.D).sum())     # degree-D columns
Ms = [int(x) for x in a.Ms.split(',')]
rng = np.random.default_rng(9000 + 10 * a.n); rand = [selector(rng, v) for _ in range(max(Ms))]
C0 = Closure(sp, a.threads); C0.add(base_rows(a.n)); base = C0.split()
print('base', base, 'top columns', cols, flush=True)
res = dict(n=a.n, D=a.D, seed=a.seed, base=base, runs=[])
for cfg in a.configs.split(','):
    d, m = map(int, cfg.split(':')); frng = np.random.default_rng(1000 * a.seed + 17 * d + m); fam = family(frng, v, d, m)
    Cm = Closure(sp, a.threads); Cm.add(base_rows(a.n) + fam); s = Cm.split()
    own = dict(low=s['low'] - base['low'], top=s['top'] - base['top'], refuted=s['refuted'])
    C = Closure(sp, a.threads); C.add(base_rows(a.n) + fam); done = 0; rows = []
    for M in Ms:
        C.add(rand[done:M]); done = M; s = C.split()
        pl, pt = base['low'] + own['low'] + M, base['top'] + own['top'] + 34 * M
        rows.append(dict(M=M, **s, pred_low=pl, pred_top=pt, excess_low=s['low'] - pl, excess_top=s['top'] - pt, pred_refuted=pt > cols))
        if s['refuted']: break
    first_pred = next((M for M in range(0, 10 ** 4) if base['top'] + own['top'] + 34 * M > cols), None)
    res['runs'].append(dict(d=d, m=m, own=own, predicted_refutation_M=first_pred, rows=rows))
    json.dump(res, open(a.out, 'w'), indent=1)
    print(f'd={d} m={m}: own {own}; predicted refutation at M={first_pred}; '
          f'(M, excess_low, excess_top, refuted): {[(r["M"], r["excess_low"], r["excess_top"], r["refuted"]) for r in rows if r["M"] % 10 == 0 or r["refuted"]]} '
          f'({time.time()-t0:.0f}s)', flush=True)
