"""Where the PC gain of a fresh block appears (odd-prime thread, 22 Sept 2026).
The degree-D PC closure is the limit of V_0 = span(generators), V_k = V_{k-1} + y*(V_{k-1} cap R_{<=D-1})
over all variables y.  For each round k this reports dim V_k, dim(V_k cap R_{<=D-1}) and
dim(V_k cap F3[existing]) for base + fresh block, next to dim C_D(base).  V_1 is contained in
NS_D(base + B); it equals NS_D(base + B) when every nonzero generator has degree D - 1 (at D = 6,
when no companion reduces below degree 5), and otherwise lacks the higher multiples of the
low-degree generators.
Usage: pc_rounds.py CONFIG   (CONFIG as in conservativity.CONFIGS)"""
import json, os, sys
import numpy as np
from scipy import sparse
from multiprocessing import Pool
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', 'odd_prime_c3_conservativity_20260922'))
from conservativity import Space, block_generators, make, CONFIGS, gf3, closure, existing_dim

def rounds(space, gens, chunk=300):
    """Yield (P, W, piv) after each round of the closure iteration (same steps as closure())."""
    cols = space.cols
    P, W, piv = gf3.rref(np.array([space.vec(g) for g in gens], dtype=np.uint8), parallel=True)
    mult = [My.astype(np.int32) for My in space.mult]
    yield P, W, piv
    while True:
        old = P.shape[0]
        lowrows = np.nonzero(space.deg[piv] <= space.D - 1)[0]; Pold = P
        for s in range(0, len(lowrows), chunk):
            L = sparse.csr_matrix(gf3.unpack(Pold[lowrows[s:s + chunk]], W, cols), dtype=np.int32)
            Q, _ = gf3.pack(np.vstack([(L @ My).toarray() % 3 for My in mult]).astype(np.uint8))
            P, W, piv = gf3.rref(None, parallel=True, packed=(np.vstack([P, Q]), W, cols))
        if P.shape[0] == old: return
        yield P, W, piv

def probe(job):
    inst = make(*job); v, D = inst['v'], inst['D']
    tA = sum(len(b) for b in inst['base']); tB = len(inst['fresh'])
    sp0 = Space(v, tA, D); gens0, k = [], v
    for b in inst['base']:
        gens0 += block_generators(b, list(range(k, k + len(b))), v, v + tA); k += len(b)
    dim_base = int(closure(sp0, gens0, par=True)[0].shape[0])
    fv = list(range(v + tA, v + tA + tB)); sp1 = Space(v, tA + tB, D, fresh_vars=fv)
    gens1 = [{e + (0,) * tB: c for e, c in g.items()} for g in gens0] + block_generators(inst['fresh'], fv, v, v + tA + tB)
    out = dict(name=inst['name'], D=D, h=tB, dim_base=dim_base, rounds=[])
    for kk, (P, W, piv) in enumerate(rounds(sp1, gens1)):
        out['rounds'].append(dict(k=kk, dim=int(P.shape[0]), low=int((sp1.deg[piv] <= D - 1).sum()),
                                  existing=existing_dim(sp1, P, W, par=True)))
    print(json.dumps(out), flush=True)
    return out

if __name__ == '__main__':
    cfg = sys.argv[1]; jobs = [j for j in CONFIGS[cfg] if j[6] == 'random']
    with Pool(min(int(os.environ.get('NS_WORKERS', '4')), len(jobs))) as pool: res = pool.map(probe, jobs, chunksize=1)
    json.dump(res, open(os.path.join(HERE, f'pc_rounds_{cfg}.json'), 'w'), indent=1)
