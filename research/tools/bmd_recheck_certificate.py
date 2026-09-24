"""Independent recheck of a compiled factor certificate with the Python placement dynamic program.

The compiled kernel (bmd_factor_kernel.cpp) builds rows from generating functions; this script
enumerates the conditions separately (bmd_symmetric_q.conditions) and evaluates each by the
per-partition placement DP.  It also checks the constant term and the degree bound.  With --sample N
it checks N random conditions (seeded) plus every condition of weight w <= 2; otherwise all.
Usage: bmd_recheck_certificate.py KERNELJSON [--sample N --seed S] --out PATH
"""
import argparse, json, math, os, random, sys, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from bmd_symmetric_q import conditions, placement_parity

ap = argparse.ArgumentParser()
ap.add_argument('cert'); ap.add_argument('--sample', type=int); ap.add_argument('--seed', type=int, default=1)
ap.add_argument('--out', required=True)
a = ap.parse_args()
d = json.load(open(a.cert))
K, D = d['K'], d['D']
Q = [tuple(l) for l in d['Q']]
rows = conditions(K)
if a.sample:
    rng = random.Random(a.seed)
    chosen = [r for r in rows if r[0] <= 2] + rng.sample([r for r in rows if r[0] > 2], a.sample)
else:
    chosen = rows
t0 = time.time()
bad = [r for r in chosen if sum(placement_parity(l, r[1], r[2]) for l in Q) & 1]
rec = {'K': K, 'D': D, 'terms': len(Q), 'has_constant': () in Q, 'max_size': max(sum(l) for l in Q),
       'rows_total': len(rows), 'rows_checked': len(chosen), 'violations': len(bad),
       'sample_seed': a.seed if a.sample else None, 'seconds': round(time.time() - t0, 1)}
rec['ok'] = rec['has_constant'] and rec['max_size'] <= D and not bad
print(json.dumps(rec), flush=True)
json.dump(rec, open(a.out, 'w'), indent=1)
