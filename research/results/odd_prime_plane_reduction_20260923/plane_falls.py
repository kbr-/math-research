"""Local-fall test for a member with no coherent reduction: four selectors forbidding A=0, A+C=0, B=1, B+C=0 for
random affine forms A, B, C (the smallest arrangement found by describable.c whose allowed set, 5 points of F_3^3,
is not a grid up-set for any basis).  Same design as local_falls.py: each member's own change in the degree-D
closure split, then k planted members followed by the recorded random selector sequence, against the additive
prediction.  Usage: --n N --D D --members k1,... --Ms ... --seed S --out PATH"""
import argparse, json, os, sys, time
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.join(HERE, '..', 'odd_prime_local_falls_20260923'))
from local_falls import Closure, QSpace, base_rows, random_eq, add_forms, sel, selector
def member(rng, v):
    A, B, C = random_eq(rng, v), random_eq(rng, v), random_eq(rng, v)
    return [sel(A), sel(add_forms((1, A), (1, C))), sel(add_forms((1, B), (1, {(): 2}))), sel(add_forms((1, B), (1, C)))]
ap = argparse.ArgumentParser(); ap.add_argument('--n', type=int, default=6); ap.add_argument('--D', type=int, default=3)
ap.add_argument('--members', default='0,1,2,3,4,6,8'); ap.add_argument('--Ms', default='0,5,10,15'); ap.add_argument('--seed', type=int, default=1)
ap.add_argument('--threads', type=int, default=12); ap.add_argument('--out'); a = ap.parse_args()
t0 = time.time(); sp = QSpace(a.n, a.D); v = sp.v
Ms = [int(x) for x in a.Ms.split(',')]; ks = [int(x) for x in a.members.split(',')]
rng = np.random.default_rng(9000 + 10 * a.n); rand = [selector(rng, v) for _ in range(max(Ms))]
prng = np.random.default_rng(100 + a.seed); mems = [member(prng, v) for _ in range(max(ks))]
C = Closure(sp, a.threads); C.add(base_rows(a.n)); base = C.split()
own = []
for m in mems:
    Cm = Closure(sp, a.threads); Cm.add(base_rows(a.n) + m); s = Cm.split()
    own.append(dict(low=s['low'] - base['low'], top=s['top'] - base['top'], refuted=s['refuted']))
print('base', base, 'own', own[:3], f'({time.time()-t0:.0f}s)', flush=True)
res = dict(n=a.n, D=a.D, seed=a.seed, base=base, own=own, runs=[])
for k in ks:
    C = Closure(sp, a.threads); C.add(base_rows(a.n) + [c for m in mems[:k] for c in m]); done = 0
    for M in Ms:
        C.add(rand[done:M]); done = M; s = C.split()
        pl = base['low'] + M + sum(o['low'] for o in own[:k]); pt = base['top'] + 34 * M + sum(o['top'] for o in own[:k])
        res['runs'].append(dict(k=k, M=M, **s, pred_low=pl, pred_top=pt, excess_low=s['low'] - pl))
        if a.out: json.dump(res, open(a.out, 'w'), indent=1)
        if s['refuted']: break
for k in ks:
    rows = [x for x in res['runs'] if x['k'] == k]
    print('k', k, [(x['M'], x['excess_low'], x['top'] - x['pred_top'], 'R' if x['refuted'] else '') for x in rows if x['M'] % 5 == 0 or x['refuted']], flush=True)
