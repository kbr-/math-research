"""Is the r=21 excess (n8_K3_defect21.json) pointwise?  If one combination z = sum a_b l_b is non-free through degree 3,
removing l_b keeps the excess exactly when a_b = 0, so z is supported on the core (forms whose removal kills the excess).
Enumerate every combination with full support on the core (one per scalar class), rank them by row profile (number of
Q-robust rows, then total row column count c_i = n - max value multiplicity), and test single-element freeness through
degree 3 for the lowest-ranked --top candidates.  Usage: --top"""
import itertools, json, os, sys
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
top = int(sys.argv[sys.argv.index('--top') + 1]) if '--top' in sys.argv else 40
sys.argv = [sys.argv[0], '--n', '8', '--K', '3', '--rs', '', '--family', 'random']
exec(open(os.path.join(HERE, 'board_affine.py')).read().split("res = []\nif opt.phis:")[0])
d = json.load(open(os.path.join(HERE, 'n8_K3_defect21.json')))
F = np.array([x for x in json.load(open(os.path.join(HERE, 'n8_K3_random.json')))['runs'] if x['r'] == 21 and x['excess'][3] > 0][0]['forms'])
core = [s['removed'] for s in d['subsystems'] if s['excess'][3] == 0]; print('core', core, len(core), flush=True)
Fc = F[core]                                   # (m, P1, n)
m = len(core); signs = np.array(list(itertools.product((1, 2), repeat=m - 1)), dtype=np.int64)
co = np.hstack([np.ones((len(signs), 1), dtype=np.int64), signs])   # first coefficient 1 fixes the scalar
Z = np.einsum('cb,bij->cij', co, Fc) % 3                            # (2^(m-1), P1, n)
cnt = np.stack([(Z == v).sum(axis=2) for v in range(3)], axis=-1)    # value multiplicities per row
crow = n - cnt.max(axis=-1)                                          # row column count c_i
nrob = (crow >= opt.Q + 1).sum(axis=1); tot = crow.sum(axis=1)
order = np.lexsort((tot, nrob)); print('robust-row histogram', np.bincount(nrob).tolist(), flush=True)
W1, T1 = W_trunc(1, 3); out = dict(core=core, robust_row_hist=np.bincount(nrob).tolist(), T=T1, tested=[])
for k in order[:top]:
    H = hilbert([Z[k]]); out['tested'].append(dict(coeffs=co[k].tolist(), nrob=int(nrob[k]), ctot=int(tot[k]), crow=crow[k].tolist(), H=H, free=H == T1))
    print(out['tested'][-1]['nrob'], out['tested'][-1]['ctot'], crow[k].tolist(), H, H == T1, flush=True)
json.dump(out, open(os.path.join(HERE, 'n8_K3_defect21_pointwise.json'), 'w'), indent=1, default=int)
