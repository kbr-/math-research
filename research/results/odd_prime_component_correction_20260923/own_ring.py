"""For the v = 12 families (planted_circuit_v12.json, products_v12.json): list every circuit of at most five constraints
(deficient span, every proper subset of full span), and compute each circuit's own quotient in the truncated ring on its span,
through degree 2d, against its own truncated prediction (the old independent-product series in d variables).
Usage: --out JSON"""
import itertools, json, os, sys
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); LD = os.path.join(HERE, '..', 'odd_prime_low_density_20260923')
outp = sys.argv[sys.argv.index('--out') + 1]
sys.argv = [sys.argv[0], '--vs', '', '--Ms', '']
exec(open(os.path.join(LD, 'products.py')).read().split('res = []')[0])
exec(open(os.path.join(HERE, 'component.py')).read().split('out = []')[0].split("a = dict(zip")[0])
from itertools import combinations
sys.path.insert(0, HERE)
src = open(os.path.join(HERE, 'component.py')).read()
exec(src[src.index('def basis_coords'):src.index('out = []')])
def circuits(F, M, kmax=5):
    rk = lambda S: rank3([F[2 * b] for b in S] + [F[2 * b + 1] for b in S])
    return [S for k in range(2, kmax + 1) for S in combinations(range(M), k)
            if rk(S) < 2 * k and all(rk(T) == 2 * len(T) for j in range(1, k) for T in combinations(S, j))]
res = []
fams = [('planted', x) for x in json.load(open(os.path.join(HERE, 'planted_circuit_v12.json')))] + \
       [('random', x) for x in json.load(open(os.path.join(HERE, 'products_v12.json')))]
for kind, x in fams:
    F = [np.array(f) for f in x['forms']]; M = len(F) // 2; cs = circuits(F, M); rec = dict(kind=kind, tag={k: x[k] for k in x if k in ('circuit_size', 'circuit_span', 'M', 'trial')}, circuits=[])
    for S in cs:
        d, coords = basis_coords([F[2 * b] for b in S] + [F[2 * b + 1] for b in S]); K2 = 2 * d
        P = [polymul(polymul(lin(coords[i]), lin(coords[i])), polymul(lin(coords[len(S) + i]), lin(coords[len(S) + i]))) for i in range(len(S))]
        H = hilbert(d, P, K2, [mons(d, k) for k in range(K2 + 1)]); _, W = series_W(d, len(S), K2); T = truncated(W)
        fd = next((k for k in range(K2 + 1) if H[k] != T[k]), None)
        rec['circuits'].append(dict(S=list(S), span=d, first_defect_own=fd))
    res.append(rec); print(kind, rec['tag'], [(c['S'], c['span'], c['first_defect_own']) for c in rec['circuits']], flush=True)
json.dump(res, open(outp, 'w'), indent=1, default=int)
