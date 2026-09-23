"""Local feasibility of affine pair systems on weak unary PHP (n = 8): which right-hand sides c in F_3^2 are met by some
injective placement of the used pigeons (rows where a form is nonzero) into the holes.  A right-hand side met by none is
contradicted by injectivity on the used pigeons alone, without the pigeonhole count.  Usage: --out JSON"""
import itertools, json, os, sys
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
def feasible(F):
    I = [i for i in range(F[0].shape[0]) if any(f[i].any() for f in F)]; sums = set()
    for holes in itertools.permutations(range(F[0].shape[1]), len(I)):
        sums.add(tuple(int(sum(f[i, h] for i, h in zip(I, holes)) % 3) for f in F))
    return I, sorted(sums)
out = {}
pp = {x['trial']: x for x in json.load(open(os.path.join(HERE, 'n8_K3_partial_pairs.json')))['runs']}
for tr in ('s1-0', 's2-0', 's3-0', 's4-0'):
    I, S = feasible([np.array(f) for f in pp[tr]['forms']]); out[tr] = dict(used_rows=I, feasible=S, infeasible=[list(c) for c in itertools.product(range(3), repeat=2) if c not in S])
F = [np.array(f) for f in json.load(open(os.path.join(HERE, 'n8_D3_rowwise_control.json')))['forms']]
I, S = feasible(F); out['rowwise_control_s4-0'] = dict(used_rows=I, feasible=S, infeasible=[list(c) for c in itertools.product(range(3), repeat=2) if c not in S])
for k, v in out.items(): print(k, 'rows', len(v['used_rows']), 'infeasible', v['infeasible'])
json.dump(out, open(sys.argv[sys.argv.index('--out') + 1], 'w'), indent=1)
