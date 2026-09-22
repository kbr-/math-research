"""Single-block conservativity over unsaturated random-equation bases (route review 22 Sept 2026).
Base F: random equations over v Boolean variables (seeds as in proxy_count2.random_system).
Fresh block B: h affine forms in x with independent linear parts; inputs 1 - L^2, companions only.
Existing variables: x.  For each instance report dim C_D(F) cap F3[x], the semantic dimension
(degree-<=D polynomials vanishing on the solutions of F), the gap, and the rise
dim C_D(F + B) cap F3[x] - dim C_D(F) cap F3[x].  For rises, extract the new elements, check their
soundness on the solutions of F and find the least D' <= D+2 with the element in C_{D'}(F).
Usage: single_block.py CONFIG   (configs below; results in single_block_CONFIG.json)."""
import itertools, json, os, sys, time, zlib
import numpy as np
from multiprocessing import Pool
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', 'odd_prime_c3_conservativity_20260922'))
sys.path.insert(0, os.path.join(HERE, '..', 'odd_prime_window_review_c3_20260922'))
from conservativity import (Space, closure, block_generators, block_product, rand_form, independent,
                            echelon, contains_one, existing_dim)
from proxy_count2 import random_system
import gf3
POW = np.array([[1, 0, 0], [1, 1, 1], [1, 2, 1]], dtype=np.uint8)

def values(sp, pts):
    E = np.array(sp.mons, dtype=np.int64)
    V = np.ones((pts.shape[0], sp.cols), dtype=np.uint8)
    for j in range(sp.n): V = (V * POW[pts[:, j:j + 1], E[None, :, j]]) % 3
    return V

def solutions_matrix(sp, gens):
    pts = np.array(list(itertools.product(range(2), repeat=sp.n)), dtype=np.int64)
    V = values(sp, pts)
    G = np.array([sp.vec(g) for g in gens], dtype=np.int32).T
    return V[((V.astype(np.int32) @ G) % 3 == 0).all(axis=1)]

def lift(p, t): return {e + (0,) * t: c for e, c in p.items()}

def run(job):
    name, v, neq, d, seed, h, D, ctl = job
    t0 = time.time()
    F = random_system(v, neq, d, seed)
    rng = np.random.default_rng(zlib.crc32(f'single-{v}-{neq}-{d}-{seed}-{h}'.encode()))
    while True:
        forms = [rand_form(rng, v, 0.6) for _ in range(h)]
        if independent(forms, v): break
    sp0 = Space(v, 0, D); P0, W0, piv0 = closure(sp0, F)
    S = solutions_matrix(sp0, F)
    semantic = sp0.cols - (gf3.rank(S) if S.shape[0] else 0)
    fv = list(range(v, v + h)); sp1 = Space(v, h, D, fresh_vars=fv)
    gens1 = [lift(g, h) for g in F] + block_generators(forms, fv, v, v + h)
    if ctl == 'fake':
        e = [0] * (v + h); e[0] = e[1] = e[2] = 1; gens1.append({tuple(e): 1})
    if ctl == 'axiomP':
        gens1.append(block_product(forms, fv, v, v + h))
    P1, W1, _ = closure(sp1, gens1)
    dim_base = int(P0.shape[0])
    rise = existing_dim(sp1, P1, W1) - dim_base              # packed count; dense only for witnesses
    polys = []
    if rise > 0 and ctl is None:
        B1 = gf3.unpack(P1, W1, sp1.cols)[:, sp1.fresh_first]
        E1, piv1 = echelon(B1, False); del B1
        ex = E1[piv1 >= sp1.nfresh][:, sp1.nfresh:]
        exmons = [sp1.mons[i] for i in sp1.fresh_first[sp1.nfresh:]]
        polys = [{m[:v]: int(c) for m, c in zip(exmons, row) if c} for row in ex]
    out = dict(name=name, v=v, neq=neq, deg=d, seed=seed, h=h, D=D, control=ctl, cols_full=sp1.cols,
               dim_base=dim_base, semantic=int(semantic), gap=int(semantic) - dim_base, rise=rise,
               n_solutions=int(S.shape[0]), forms=forms, witnesses=[])
    if rise > 0 and ctl is None:
        B0 = gf3.unpack(P0, W0, sp0.cols); cur = B0
        new = []
        for p in polys:
            w = sp0.vec(p)
            if gf3.rank(np.vstack([cur, w])) > cur.shape[0]: new.append(p); cur = np.vstack([cur, w])
        for p in new:
            w = sp0.vec(p).astype(np.int32)
            sound = bool(((S.astype(np.int32) @ w) % 3 == 0).all())
            lag = None
            for D2 in (D + 1, D + 2):
                sp2 = Space(v, 0, D2); P2, W2, _ = closure(sp2, F); B2 = gf3.unpack(P2, W2, sp2.cols)
                if gf3.rank(np.vstack([B2, sp2.vec(p)])) == B2.shape[0]: lag = D2; break
            out['witnesses'].append(dict(degree=max(sum(e) for e in p), terms=len(p), sound=sound,
                                         in_base_closure_at=lag))
    out['seconds'] = round(time.time() - t0, 1)
    return out

CONFIGS = {
    'd6': [('d6', v, 1, d, s, h, 6, None) for v in (10, 12) for d in (2, 3) for s in range(4) for h in (2, 3)],
    'd7': [('d7', 12, 1, 3, s, h, 7, None) for s in range(4) for h in (2, 3)] +
          [('d7', 12, 1, 2, s, h, 7, None) for s in range(4) for h in (2, 3)],
    'd6h': [('d6h', 10, 1, d, s, h, 6, None) for d in (2, 3) for s in range(3) for h in (4, 5, 6)],
    'controls': [('ctl', 10, 1, 3, 0, 2, 6, c) for c in ('fake', 'axiomP')] +
                [('ctl', 10, 2, 2, s, h, 6, None) for s in range(2) for h in (2, 3)],
}

if __name__ == '__main__':
    cfg = sys.argv[1]; jobs = CONFIGS[cfg]
    workers = int(sys.argv[2]) if len(sys.argv) > 2 else 14
    res = []
    with Pool(min(workers, len(jobs))) as pool:
        for r in pool.imap_unordered(run, jobs):
            print(json.dumps({k: r[k] for k in ('name', 'v', 'deg', 'seed', 'h', 'D', 'control', 'cols_full',
                                                'gap', 'rise', 'seconds')}), flush=True)
            res.append(r)
    res.sort(key=lambda r: (r['v'], r['deg'], r['seed'], r['h'], r['D'], str(r['control'])))
    json.dump(res, open(os.path.join(HERE, f'single_block_{cfg}.json'), 'w'), indent=1)
