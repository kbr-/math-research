"""Local-fall test, all in one process with shared prefixes: the base closure and the random selector series are
computed once; every member type, seed and k starts from a copy of the base closure (closure3.py / gf3_closure.c).
Members: pencil (four selectors on L1, L2, L1+L2+c3, L1-L2+c4) and plane (forbid A=0, A+C=0, B=1, B+C=0).
Usage: --n N --D D --types pencil,plane --seeds 1,2 --ks 0,1,2,4,8 --Ms ... --out PATH"""
import argparse, json, os, sys, time
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
from closure3 import Space, Closure, base_rows
from local_falls import random_eq, add_forms, sel, selector, pencil
def plane(rng, v):
    A, B, C = random_eq(rng, v), random_eq(rng, v), random_eq(rng, v)
    return [sel(A), sel(add_forms((1, A), (1, C))), sel(add_forms((1, B), (1, {(): 2}))), sel(add_forms((1, B), (1, C)))]
ap = argparse.ArgumentParser(); ap.add_argument('--n', type=int, default=7); ap.add_argument('--D', type=int, default=3)
ap.add_argument('--types', default='pencil,plane'); ap.add_argument('--seeds', default='1,2'); ap.add_argument('--ks', default='1,2,4,8')
ap.add_argument('--Ms', default='0,50,100'); ap.add_argument('--threads', type=int, default=12); ap.add_argument('--out'); a = ap.parse_args()
t0 = time.time(); sp = Space(a.n, a.D); v = sp.v; cap = int((sp.deg == a.D).sum())
Ms = [int(x) for x in a.Ms.split(',')]; ks = [int(x) for x in a.ks.split(',')]
rng = np.random.default_rng(9000 + 10 * a.n); rand = [selector(rng, v) for _ in range(max(Ms))]
base = Closure(sp, a.threads).add(base_rows(a.n)); bs = base.split()
R = base.copy(); rs = {}; done = 0
for M in Ms:                                               # random series once
    R.add(rand[done:M]); done = M; rs[M] = R.split()
    if rs[M]['refuted']: break
print(f'n={a.n}: space and base {time.time()-t0:.1f}s; random refuted at', next((M for M in rs if rs[M]['refuted']), None), flush=True)
res = dict(n=a.n, D=a.D, Ms=Ms, top_columns=cap, base=bs, random=rs, series=[])
for typ in a.types.split(','):
    gen = plane if typ == 'plane' else pencil
    for s in map(int, a.seeds.split(',')):
        prng = np.random.default_rng(100 * (typ == 'plane') + s); mems = [gen(prng, v) for _ in range(max(ks))]
        own = []
        for m in mems:
            x = base.copy().add(m).split(); own.append(dict(low=x['low'] - bs['low'], top=x['top'] - bs['top']))
        for k in ks:
            C = base.copy().add([c for m in mems[:k] for c in m]); done = 0; rows = []
            for M in Ms:
                C.add(rand[done:M]); done = M; x = C.split(); row = dict(M=M, **x)
                if M in rs and not rs[M]['refuted']:
                    row['excess_low'] = x['low'] - rs[M]['low'] - sum(o['low'] for o in own[:k])
                rows.append(row)
                if x['refuted']: break
            ser = dict(type=typ, seed=s, k=k, own=own[:k], rows=rows); res['series'].append(ser)
            print(typ, s, 'k', k, 'refuted at', next((r['M'] for r in rows if r['refuted']), None),
                  'max low excess', max((r.get('excess_low', 0) for r in rows if not r['refuted']), default=None), f'{time.time()-t0:.0f}s', flush=True)
            if a.out: json.dump(res, open(a.out, 'w'), indent=1)
