"""Degree split of the degree-D closure for weak unary PHP^{n+1}_n over F_3 plus the first M selector
constraints of seed 9000+10n (same sequence as selector_threshold.py): number of echelon rows whose pivot is a
degree-D column (= rank of the projection onto the degree-D part) and the number with pivot of degree < D
(= dim of the closure's degree-<D part).  No degree fall means low = low_0 + M and top = top_0 + (gamma_1-1) M.
Usage: --n N --D D --Ms 0,20,... --out PATH"""
import argparse, json, os, sys
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', 'odd_prime_one_count_20260922')); sys.path.insert(0, HERE)
from random_conditioning_fast import QSpace, closure_of, refuted, base_rows
from selector_threshold_lib import selector
ap = argparse.ArgumentParser(); ap.add_argument('--n', type=int); ap.add_argument('--D', type=int, default=3)
ap.add_argument('--Ms'); ap.add_argument('--out'); a = ap.parse_args()
sp = QSpace(a.n, a.D); v = a.n * (a.n + 1); rng = np.random.default_rng(9000 + 10 * a.n)
Ms = [int(x) for x in a.Ms.split(',')]; cons = [selector(rng, v) for _ in range(max(Ms))]
res = {'n': a.n, 'D': a.D, 'cols_topdeg': int((sp.deg == a.D).sum()), 'probes': []}
for M in Ms:
    P, W, piv = closure_of(sp, base_rows(a.n) + cons[:M]); piv = np.asarray(piv)
    top = int((sp.deg[piv] == a.D).sum()); low = int((sp.deg[piv] < a.D).sum())
    o = {'M': M, 'rank': int(P.shape[0]), 'top': top, 'low': low, 'refuted': bool(refuted(sp, P, W))}
    res['probes'].append(o); print(o, flush=True)
json.dump(res, open(a.out, 'w'), indent=1)
