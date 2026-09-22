"""Feasibility count, second proxy: a few random low-degree equations over v Boolean variables
(deterministic seeds).  Reports closure dimension vs semantic dimension at D = 6, 7, 8."""
import itertools, json, os, sys, zlib
import numpy as np
from multiprocessing import Pool
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', 'odd_prime_c3_conservativity_20260922'))
from conservativity import Space, closure, contains_one, monomials
sys.path.insert(0, os.path.join(HERE, '..', 'odd_prime_alignment_mechanism_20260922'))
import gf3
POW = np.array([[1, 0, 0], [1, 1, 1], [1, 2, 1]], dtype=np.uint8)

def random_system(v, neq, d, seed):
    rng = np.random.default_rng(zlib.crc32(f'proxy-{v}-{neq}-{d}-{seed}'.encode()))
    mons = [e for e in monomials(v, 0, d)]
    return [{e: int(c) for e, c in zip(mons, rng.integers(0, 3, len(mons))) if c} for _ in range(neq)]

def work(job):
    v, neq, d, D, seed = job
    gens = random_system(v, neq, d, seed)
    sp = Space(v, 0, D); P, W, piv = closure(sp, gens)
    pts = np.array(list(itertools.product(range(2), repeat=v)), dtype=np.int64)
    E = np.array(sp.mons, dtype=np.int64)
    V = np.ones((pts.shape[0], sp.cols), dtype=np.uint8)
    for j in range(v): V = (V * POW[pts[:, j:j + 1], E[None, :, j]]) % 3
    G = np.array([sp.vec(g) for g in gens], dtype=np.int32).T
    S = V[((V.astype(np.int32) @ G) % 3 == 0).all(axis=1)]
    semantic = sp.cols - (gf3.rank(S) if S.shape[0] else 0)
    return dict(v=v, neq=neq, deg=d, D=D, seed=seed, cols=sp.cols, dim=int(P.shape[0]), semantic=int(semantic),
                n_solutions=int(S.shape[0]), one=bool(contains_one(sp, P, W)))

if __name__ == '__main__':
    jobs = [(v, neq, d, D, s) for v in (10, 12) for (neq, d) in ((1, 2), (2, 2), (1, 3)) for D in (6, 7, 8) for s in range(2)]
    with Pool(12) as pool: res = pool.map(work, jobs)
    for r in res: print(json.dumps({k: r[k] for k in ('v', 'neq', 'deg', 'D', 'seed', 'cols', 'dim', 'semantic', 'n_solutions')}))
    json.dump(res, open(os.path.join(HERE, 'proxy_count2.json'), 'w'), indent=1)
