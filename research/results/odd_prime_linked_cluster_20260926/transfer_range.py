#!/usr/bin/env python3
"""Transfer range n_0 of the instances of hilbert_series.py (same forms, regenerated from its seed).

n_0 - 1 is the largest e for which T * Gamma_{<=e} is free over T = F_3[w]/(w^3)^{(r)}, T acting on the
graded functions Gamma of the 12-cube by the tops of s and the instance's forms (hypothesis (T) of
cor:free-hole-uniformity, tested exactly by transfer_vs_uniformity.hypothesis).  Freeness with n_0 >= 1
needs (p-1) r <= N, since T * 1 must contain the socle element in degree (p-1) r; a generator in degree e
likewise needs e + (p-1) r <= N, so only e <= N - 2r is tested.
"""
import json, sys
import numpy as np
here = __file__.rsplit('/', 1)[0]
sys.path.insert(0, here + '/../odd_prime_free_hole_20260925')
sys.path.insert(0, here + '/../odd_prime_closure_route_review_20260925')
from transfer_vs_uniformity import hypothesis as hypothesis_reference, mult, t_hilbert
from vanishing_tops import rank3, rref3
from math import comb


def hypothesis(vecs, holes, e):
    """transfer_vs_uniformity.hypothesis with each degree's span reduced to a basis (that version stacks
    unreduced rows, whose number grows by a factor r+1 per degree); validated against it below."""
    n = len(holes); r = len(vecs); t = t_hilbert(r)
    g = {0: 1}; U = np.eye(1, dtype=np.int64)
    for d in range(1, e + 2 * r + 1):
        pred = sum(g[k] * (t[d - k] if d - k < len(t) else 0) for k in g)
        if d > n:
            if pred:
                return False
            continue
        W = np.vstack([U @ mult(v, holes, d - 1) % 3 for v in vecs]) % 3 if len(U) else np.zeros((0, comb(n, d)), dtype=np.int64)
        W = rref3(W)[0] if len(W) else W
        w = len(W)
        if w != pred:
            return False
        if d <= e:
            g[d] = comb(n, d) - w; U = np.eye(comb(n, d), dtype=np.int64)
        else:
            U = W
    return True

for Nv in (7, 8, 9):                      # validation against the reference implementation
    rv = np.random.default_rng(Nv)
    for rr in (2, 3):
        vv = [np.ones(Nv, dtype=np.int64)] + list(rv.integers(0, 3, size=(rr, Nv)))
        for ee in range(3):
            assert hypothesis(vv, list(range(Nv)), ee) == hypothesis_reference(vv, list(range(Nv)), ee)
print('validated against the reference on N = 7, 8, 9', flush=True)

N = 12
rng = np.random.default_rng(20260928)
phi = rng.integers(1, 3, size=(4, N)); phi[0:2, 6:] = 0; phi[2:4, :6] = 0
cases = {'disjoint supports': phi}
cases['dense independent'] = rng.integers(1, 3, size=(4, N))
cases['shared forms (two-block pair)'] = rng.integers(1, 3, size=(2, N))
out = {}
for name, ph in cases.items():
    vecs = [np.ones(N, dtype=np.int64)] + list(ph)
    for sub, vv in (('s and all forms', vecs),):
        e, cap = -1, N - 2 * (len(vv))           # socle bound: a generator in degree e needs e + 2r <= N
        while e + 1 <= cap:
            ok = hypothesis(vv, list(range(N)), e + 1)
            print(name, sub, 'e =', e + 1, 'free' if ok else 'not free', flush=True)
            if not ok:
                break
            e += 1
        out[f'{name}: {sub}'] = {'forms_with_s': len(vv), 'n0': e + 1}
        print(name, sub, len(vv), 'n0 =', e + 1, flush=True)
if '--out' in sys.argv:
    json.dump(out, open(sys.argv[sys.argv.index('--out') + 1], 'w'), indent=1)
