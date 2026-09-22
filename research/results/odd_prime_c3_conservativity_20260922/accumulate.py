"""Does the conservativity lag accumulate?  The only nonvacuous base found (lowgap.py) is
twobase2 seed 0 at D=6, where C_7(base) cap R_{<=6} has gap 2 below the semantic space.  Fresh
blocks: B1 = that instance's fresh block (13-dimensional rise at D=6), B2 = a random 2-input block
(seeded).  For the existing-variable part X_k of C_6(base + B1..Bk), k = 1, 2, report the least D'
in {6, 7, 8, 9} with X_k contained in C_{D'}(base).  A value 8 for k = 2 would show accumulation.
Usage: accumulate.py SEED... ; results go to c3_accumulate.json."""
import json, os, sys, time, zlib
import numpy as np
from multiprocessing import Pool
from conservativity import *

def instance(seed, v=6):
    inst = make('twobase2', v, 6, 2, 2, 0, 'random', 2)
    rng = np.random.default_rng(zlib.crc32(f'accum-second-{seed}'.encode()))
    while True:
        b2 = [rand_form(rng, v, 0.6) for _ in range(2)]
        if independent(b2, v): return inst['base'], [inst['fresh'], b2]

def existing_part(space, P, W):
    """Rows (dense, fresh-first coordinates restricted to existing columns) spanning V cap existing."""
    B = gf3.unpack(P, W, space.cols)[:, space.fresh_first]
    E, piv = echelon(B, False)
    ex = E[piv >= space.nfresh][:, space.nfresh:]
    mons = [space.mons[i] for i in space.fresh_first[space.nfresh:]]
    return ex, mons

def lag_of(polys, v, tA, gens0, D):
    for D2 in range(D, D + 4):  # D' = D, ..., D+3
        sp = Space(v, tA, D2); P, W, _ = closure(sp, gens0); B = gf3.unpack(P, W, sp.cols)
        M = np.array([sp.vec(p) for p in polys], dtype=np.uint8) if polys else np.zeros((0, sp.cols), np.uint8)
        if gf3.rank(np.vstack([B, M])) == B.shape[0]: return D2, B.shape[0]
    return None, None

def work(seed):
    D = 6; v = 6; t0 = time.time()
    base, fresh = instance(seed, v)
    tA = 4; gens0, k = [], v
    for b in base:
        gens0 += block_generators(b, [k, k + 1], v, v + tA); k += 2
    out = dict(D=D, seed=seed, base=base, fresh=fresh, per_k=[])
    for kf in (1, 2):
        tB = 2 * kf; fv = list(range(v + tA, v + tA + tB))
        sp1 = Space(v, tA + tB, D, fresh_vars=fv)
        gens1 = [{e + (0,) * tB: c for e, c in g.items()} for g in gens0]
        for j in range(kf):
            gens1 += block_generators(fresh[j], fv[2 * j:2 * j + 2], v, v + tA + tB)
        P1, W1, _ = closure(sp1, gens1)
        ex, mons = existing_part(sp1, P1, W1)
        polys = [{m[:v + tA]: int(c) for m, c in zip(mons, row) if c} for row in ex]
        lag, dimb = lag_of(polys, v, tA, gens0, D)
        out['per_k'].append(dict(k=kf, cols=sp1.cols, dim_existing=len(polys), contained_at=lag))
    out['seconds'] = round(time.time() - t0, 1)
    return out

if __name__ == '__main__':
    seeds = list(map(int, sys.argv[1:]))
    res = []
    with Pool(min(int(os.environ.get('C3_WORKERS', '8')), len(seeds))) as pool:
        for r in pool.imap_unordered(work, seeds):
            print(json.dumps({k: r[k] for k in ('D', 'seed', 'per_k', 'seconds')}), flush=True); res.append(r)
    res.sort(key=lambda r: r['seed'])
    json.dump(res, open(os.path.join(HERE, 'c3_accumulate.json'), 'w'), indent=1)
