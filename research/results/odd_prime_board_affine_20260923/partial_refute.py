"""Degree-D PC refutation test (exact closure, as in occupancy_refute.py) for the partial-occupancy pairs of
n8_K3_partial_pairs.json: PHP plus l_1 = c_1, l_2 = c_2.  The affine maps of F_3^2 fixing the missing point p, realized by
hole permutations, send the system with right-hand side c to the one with M(c - |I|p) + |I|p (I the used pigeons), so the
right-hand sides fall into two classes: |I|p and the other eight.  Closures stop early once 1 is in the span (close_early).  Usage: --rhs 's4-0:2,1;s2-0:1,2' --D --out
(a first run over all right-hand sides, stopped after one closure for time, is n8_D3_partial_refute_run1.log)"""
import json, os, sys, time
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); a = dict(zip(sys.argv[1::2], sys.argv[2::2])); want = [(x.split(':')[0], tuple(int(v) for v in x.split(':')[1].split(','))) for x in a['--rhs'].split(';')]
sys.argv = [sys.argv[0], '--n', '8', '--D', a['--D'], '--rs', '']
src = open(os.path.join(HERE, 'occupancy_refute.py')).read()
exec(src.split("res = dict(n=n, D=D, php_alone_refuted")[0])
from early_closure import close_early, closure_of_early as closure_of
runs = {x['trial']: x for x in json.load(open(os.path.join(HERE, 'n8_K3_partial_pairs.json')))['runs']}; out = []
for tr, (c1, c2) in want:
    F = [np.array(f) for f in runs[tr]['forms']]
    P, W, _ = closure_of(space, base + [form_eq(F[0], c1), form_eq(F[1], c2)]); ref = bool(refuted(space, P, W))
    out.append(dict(trial=tr, zero_rows=runs[tr]['rows'], c=[c1, c2], refuted=ref)); print(tr, c1, c2, ref, f'({time.time()-t0:.0f}s)', flush=True)
    json.dump(dict(n=8, D=int(a['--D']), runs=out), open(a['--out'], 'w'), indent=1)   # after every closure
