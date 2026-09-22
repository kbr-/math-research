"""Nonvacuity count for the C3 tests.  For each instance of a configuration, compare dim C_D(base)
with the semantic dimension, dim{f in R_existing, deg f <= D : f vanishes on all base solutions}.
If they are equal, the base closure is saturated and conservativity at D is forced by soundness,
so that test is vacuous.  The gap (semantic - dim_base) bounds how much a fresh block could add.
Usage: saturation.py CONFIG...  Output: c3_saturation.json (merged over runs, keyed by name+D)."""
import itertools, json, os, sys
import numpy as np
from multiprocessing import Pool
from conservativity import *

POW = np.array([[1, 0, 0], [1, 1, 1], [1, 2, 1]], dtype=np.uint8)   # POW[x, a] = x^a mod 3

def work(job, chunk=1500):
    inst = make(*job); v = inst['v']; D = inst['D']
    tA = sum(len(b) for b in inst['base'])
    sp0 = Space(v, tA, D); gens0, k = [], v
    for b in inst['base']:
        gens0 += block_generators(b, list(range(k, k + len(b))), v, v + tA); k += len(b)
    P0, W0, _ = closure(sp0, gens0)
    E = np.array(sp0.mons, dtype=np.int64)
    G = np.array([sp0.vec(g) for g in gens0], dtype=np.int32).T
    grid = itertools.product(*([range(2)] * v + [range(3)] * tA))
    acc, nsol, W = None, 0, None
    while True:
        pts = np.array(list(itertools.islice(grid, chunk)), dtype=np.int64)
        if pts.shape[0] == 0: break
        V = np.ones((pts.shape[0], sp0.cols), dtype=np.uint8)
        for j in range(sp0.n):
            V = (V * POW[pts[:, j:j + 1], E[None, :, j]]) % 3
        S = V[((V.astype(np.int32) @ G) % 3 == 0).all(axis=1)]
        nsol += S.shape[0]
        if S.shape[0]:
            Q, W = gf3.pack(S)
            acc = Q if acc is None else np.vstack([acc, Q])
            acc, W, _ = gf3.rref(None, packed=(acc, W, sp0.cols))
    rank = 0 if acc is None else acc.shape[0]
    return dict(name=inst['name'], D=D, cols=sp0.cols, dim_base=int(P0.shape[0]),
                semantic=int(sp0.cols - rank), n_solutions=int(nsol))

if __name__ == '__main__':
    out_path = os.path.join(HERE, 'c3_saturation.json')
    have = {(r['name'], r['D']): r for r in json.load(open(out_path))} if os.path.exists(out_path) else {}
    jobs = [j for c in sys.argv[1:] for j in CONFIGS[c]]
    jobs = [j for j in jobs if j[5] != 'fake' and j[5] != 'axiomP']
    with Pool(int(os.environ.get('C3_WORKERS', '10'))) as pool:
        for r in pool.imap_unordered(work, jobs):
            have[(r['name'], r['D'])] = r
    res = sorted(have.values(), key=lambda r: (r['name'], r['D']))
    json.dump(res, open(out_path, 'w'), indent=1)
    print(len(res), 'instances')
