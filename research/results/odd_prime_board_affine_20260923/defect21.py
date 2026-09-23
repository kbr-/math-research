"""Characterize the r=21 near-fill excess found in n8_K3_random.json (trial 1): (a) the Hilbert functions of all 21
subsystems with one form removed (is the defect carried by a smaller subfamily?); (b) single-element freeness through
degree 3 of 200 random nonzero F_3-combinations (A/(l_z) against HS_A/(1+t+t^2)); a combination failing it would make the
defect pointwise.  Reuses board_affine.py's functions (n=8, K=3)."""
import json, os, sys
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
sys.argv = [sys.argv[0], '--n', '8', '--K', '3', '--rs', '', '--family', 'random']
src = open(os.path.join(HERE, 'board_affine.py')).read().split("res = []\nif opt.phis:")[0]
exec(src)
d = json.load(open(os.path.join(HERE, 'n8_K3_random.json')))
run = [x for x in d['runs'] if x['r'] == 21 and x['excess'][3] > 0][0]
F = [np.array(f) for f in run['forms']]; out = dict(full_H=run['H'], full_T=run['T'])
W20, T20 = W_trunc(20, 3); sub = []
for b in range(21):
    H = hilbert(F[:b] + F[b + 1:]); sub.append(dict(removed=b, H=H, excess=[h - x for h, x in zip(H, T20)]))
    print('remove', b, H, 'T', T20, flush=True)
out['subsystems'] = sub
W1, T1 = W_trunc(1, 3); rng2 = np.random.default_rng(7); single = []
for s in range(200):
    co = rng2.integers(0, 3, size=21)
    if not co.any(): continue
    G = sum(int(a) * f for a, f in zip(co, F)) % 3
    H = hilbert([G]); single.append(dict(coeffs=co.tolist(), H=H, free=H == T1))
out['single_T'] = T1; out['single_tested'] = len(single); out['single_nonfree'] = [x for x in single if not x['free']]
print('single-element: tested', len(single), 'non-free', len(out['single_nonfree']), flush=True)
json.dump(out, open(os.path.join(HERE, 'n8_K3_defect21.json'), 'w'), indent=1, default=int)
