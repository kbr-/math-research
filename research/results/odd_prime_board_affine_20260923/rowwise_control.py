"""Control for the partial occupancy pair: forms supported on the same used rows I as n8_K3_partial_pairs.json trial --trial,
each used row carrying its own random hole permutation of the configuration AG(2,3) minus a point (so every nonzero
combination is 4-robust on every used row, as for the occupancy pair), but not column-type.  Reports the Hilbert function
of A/(l_1,l_2) through degree 3 and, with --rhs, the degree-3 refutation status.  Closures stop early once 1 is in the span (early_closure.py).  Usage: --trial s4-0 --seed --rhs 0,0 --out"""
import json, os, sys, time
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); a = dict(zip(sys.argv[1::2], sys.argv[2::2]))
runs = {x['trial']: x for x in json.load(open(os.path.join(HERE, 'n8_K3_partial_pairs.json')))['runs']}
run = runs[a['--trial']]; base = [np.array(f) for f in run['forms']]; rng = np.random.default_rng(int(a['--seed']))
I = [i for i in range(9) if i not in run['rows']]; F = [f.copy() for f in base]
for i in I[1:]:   # keep the first used row, permute holes independently on the others
    pi = rng.permutation(8)
    for f in F: f[i] = f[i][pi]
out = dict(trial=a['--trial'], used_rows=I, forms=[f.tolist() for f in F])
sys.argv = [sys.argv[0], '--n', '8', '--K', '3', '--rs', '', '--family', 'random']
exec(open(os.path.join(HERE, 'board_affine.py')).read().split("res = []\nif opt.phis:")[0])
W, T = W_trunc(2, 3); H = hilbert(F); out.update(H=H, T=T, excess=[h - x for h, x in zip(H, T)]); print(out['H'], out['excess'], flush=True)
if '--rhs' in a:
    c1, c2 = (int(v) for v in a['--rhs'].split(','))
    sys.argv = [sys.argv[0], '--n', '8', '--D', '3', '--rs', '']
    exec(open(os.path.join(HERE, 'occupancy_refute.py')).read().split("res = dict(n=n, D=D, php_alone_refuted")[0])
    sys.path.insert(0, HERE); from early_closure import closure_of_early as closure_of
    P, W_, _ = closure_of(space, base_rows(8) + [form_eq(F[0], c1), form_eq(F[1], c2)])
    out.update(c=[c1, c2], refuted=bool(refuted(space, P, W_))); print('refuted', out['refuted'], flush=True)
json.dump(out, open(a['--out'], 'w'), indent=1, default=int)
