"""Local-fall test at any board size: k planted members (pencil: four selectors on L1, L2, L1+L2+c3, L1-L2+c4,
(c3,c4) != (0,0); plane: forbid A=0, A+C=0, B=1, B+C=0) followed by the recorded random selector sequence of seed
9000+10n, against the additive prediction built from measured data: the k=0 run gives the random selectors'
split at every M, and each member's own change is measured alone.  Reports the low excess and compares the least
refuted M with the first M at which the predicted top part exceeds the number of degree-D columns.
Usage: --n N --D D --member pencil|plane --ks 0,1,... --Ms ... --seed S --out PATH"""
import argparse, json, os, sys, time
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.join(HERE, '..', 'odd_prime_local_falls_20260923'))
from local_falls import Closure, QSpace, base_rows, random_eq, add_forms, sel, selector, pencil
def plane(rng, v):
    A, B, C = random_eq(rng, v), random_eq(rng, v), random_eq(rng, v)
    return [sel(A), sel(add_forms((1, A), (1, C))), sel(add_forms((1, B), (1, {(): 2}))), sel(add_forms((1, B), (1, C)))]
ap = argparse.ArgumentParser(); ap.add_argument('--n', type=int, default=7); ap.add_argument('--D', type=int, default=3)
ap.add_argument('--member', default='pencil'); ap.add_argument('--ks', default='0,1,2,4,8'); ap.add_argument('--Ms', default='0,50,100,150')
ap.add_argument('--seed', type=int, default=1); ap.add_argument('--threads', type=int, default=12); ap.add_argument('--out'); a = ap.parse_args()
t0 = time.time(); sp = QSpace(a.n, a.D); v = sp.v; cap = int((sp.deg == a.D).sum())
Ms = [int(x) for x in a.Ms.split(',')]; ks = [int(x) for x in a.ks.split(',')]
rng = np.random.default_rng(9000 + 10 * a.n); rand = [selector(rng, v) for _ in range(max(Ms))]
prng = np.random.default_rng(100 * (a.member == 'plane') + a.seed); gen = plane if a.member == 'plane' else pencil
mems = [gen(prng, v) for _ in range(max(ks))]
C = Closure(sp, a.threads); C.add(base_rows(a.n)); base = C.split()
own = []
for m in mems:
    Cm = Closure(sp, a.threads); Cm.add(base_rows(a.n) + m); s = Cm.split()
    own.append(dict(low=s['low'] - base['low'], top=s['top'] - base['top'], refuted=s['refuted']))
print(f'n={a.n} D={a.D} columns={sp.cols} top-degree={cap} base={base} own={own[:2]} ({time.time()-t0:.0f}s)', flush=True)
res = dict(n=a.n, D=a.D, member=a.member, seed=a.seed, Ms=Ms, top_columns=cap, base=base, own=own, runs=[])
randsplit = {}
for k in ks:
    C = Closure(sp, a.threads); C.add(base_rows(a.n) + [c for m in mems[:k] for c in m]); done = 0
    for M in Ms:
        C.add(rand[done:M]); done = M; s = C.split()
        if k == 0: randsplit[M] = s
        row = dict(k=k, M=M, **s)
        if M in randsplit and not randsplit[M]['refuted']:
            row['pred_low'] = randsplit[M]['low'] + sum(o['low'] for o in own[:k]); row['excess_low'] = s['low'] - row['pred_low']
            row['pred_top'] = randsplit[M]['top'] + sum(o['top'] for o in own[:k])
        res['runs'].append(row)
        if a.out: json.dump(res, open(a.out, 'w'), indent=1)
        if s['refuted']: break
for k in ks:
    rows = [x for x in res['runs'] if x['k'] == k]; ref = next((x['M'] for x in rows if x['refuted']), None)
    pc = next((x['M'] for x in rows if 'pred_top' in x and x['pred_top'] > cap), None)
    print('k', k, 'refuted at', ref, 'predicted-top crossing at', pc, 'max low excess', max((x.get('excess_low', 0) for x in rows if not x['refuted']), default=None), flush=True)
print(f'({time.time()-t0:.0f}s)')
