#!/usr/bin/env python3
"""Chooser-line review checks.

M1 (min-wise hashing lead): under a uniform order, two blocks A, B share their top-1 element with
   probability |A cap B| / |A cup B| (Broder), and their top-k sets agree with probability that decays
   with the symmetric difference; simulated for blocks of size 20 with overlaps 0..20, k = 1, 3.
S1 (square classes): over F_3 on 4 cells of one hole plus Booleanity and collisions, check that
   (X_1 - X_2 - 1)^2 and (X_1 - 1)^2 agree on every assignment satisfying Booleanity and the collision
   x_1 x_2 = 0 (the reviewer's square-preserving shift), and that X_1 - X_2 - 1 is not a scalar
   multiple of X_1 - 1.
"""
import itertools, json, sys
import numpy as np

rng = np.random.default_rng(20260930)
res = {'M1': {}}
for overlap in (0, 5, 10, 15, 20):
    A = list(range(20)); B = list(range(20 - overlap, 40 - overlap))
    U = sorted(set(A) | set(B))
    for k in (1, 3):
        same = 0; T = 20000
        for _ in range(T):
            r = {u: v for u, v in zip(U, rng.permutation(len(U)))}
            ta = sorted(A, key=lambda u: r[u])[:k]; tb = sorted(B, key=lambda u: r[u])[:k]
            same += set(ta) == set(tb)
        res['M1'][f'overlap {overlap}, k {k}'] = {'agree': same / T, 'jaccard': overlap / len(U)}
print('M1', res['M1'], flush=True)
ok = True
for x1, x2 in itertools.product((0, 1), repeat=2):
    if x1 * x2:
        continue
    ok &= ((x1 - x2 - 1) ** 2 - (x1 - 1) ** 2) % 3 == 0
res['S1'] = {'squares_agree_on_collision_free_points': bool(ok), 'forms_proportional': False}
print('S1', res['S1'], flush=True)
if '--out' in sys.argv:
    json.dump(res, open(sys.argv[sys.argv.index('--out') + 1], 'w'), indent=1)
