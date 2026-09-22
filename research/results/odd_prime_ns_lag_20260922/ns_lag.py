"""Nullstellensatz-level fresh-block losses against rank (odd-prime thread, 22 Sept 2026).
NS_D(G) in the reduced ring R = F3[x, r]/(x^2 - x, r^3 - r) is the span of reduce(m*g) over generators
g and reduced monomials m with deg m + deg g <= D.  (Reduction is by Boolean and field axioms at
degree <= D, so this is degree-D NS with those axioms, each generator charged at the degree of its
reduced form; some companions reduce below degree 5.)

count:  for each base, room(D') = semantic_D - dim(NS_{D'}(base) cap R_{<=D}) for D' = D..D+4;
        a loss of L degrees is detectable only where room(D+L-1) > 0.
losses: for fresh blocks with h inputs, the new existing-variable elements of NS_D(base+B) beyond
        NS_D(base), and the least D' <= D+4 with all of them in NS_{D'}(base).  With --axiomP the
        block product P is added as an axiom (a control that must produce unsound elements).
Rows are generated as dense layers and packed at once; each base echelon keeps only its part of
degree <= D, in the base space's columns, so memory stays near one packed echelon per worker.
Usage: ns_lag.py count CONFIG | ns_lag.py losses CONFIG H... [--axiomP]   (CONFIG as in
conservativity.CONFIGS; NS_WORKERS sets the pool size, default 4)"""
import json, os, sys
import numpy as np
from scipy import sparse
from multiprocessing import Pool
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', 'odd_prime_c3_conservativity_20260922'))
from conservativity import Space, block_generators, block_product, make, CONFIGS, gf3, deg

def shift_maps(space):
    """For each variable y, the map m -> reduce(y m) on columns of degree <= D-1, split into two
    groups in which every target occurs at most once (a target has at most two preimages)."""
    out = []
    for My in space.mult:
        C = My.tocoo(); src, tgt = C.row, C.col
        order = np.argsort(tgt, kind='stable'); src, tgt = src[order], tgt[order]
        first = np.ones(len(tgt), bool); first[1:] = tgt[1:] != tgt[:-1]
        assert not (~first[1:] & ~first[:-1]).any()                   # at most two preimages
        out.append((src[first], tgt[first], src[~first], tgt[~first]))
    return out

def ns_packed(space, gens, D, perm=None):
    """Bit-packed rows spanning NS_D(gens) in space (space.D >= D): reduce(m g) for every reduced
    monomial m with deg m + deg g <= D.  Monomials are built layer by layer; the child m + e_y is
    produced only from the parent with y the least variable of the child, so each monomial occurs
    once.  Layers are dense uint8 and are packed as soon as they are produced.  Columns are
    permuted by `perm` before packing if given."""
    maps = shift_maps(space); parts = []
    def emit(A):
        A = A if perm is None else A[:, perm]
        parts.append(gf3.pack(np.ascontiguousarray(A))[0])
    high = space.deg > D - 1
    for g in gens:
        if not g: continue                                    # a generator that reduces to zero
        dg = max(deg(e) for e in g)
        if dg > D: continue
        mons = [tuple([0] * space.n)]; A = space.vec(g)[None, :]
        emit(A)
        for k in range(1, D - dg + 1):
            assert not A[:, high].any()                       # parents have degree <= D-1
            newm, blocks = [], []
            for y in range(space.n):
                cap = 1 if y < space.nv else 2
                sel = [i for i, m in enumerate(mons) if m[y] < cap and not any(m[:y])]
                if not sel: continue
                s1, t1, s2, t2 = maps[y]; Ay = A[sel]
                C = np.zeros((len(sel), space.cols), np.uint8)
                C[:, t1] = Ay[:, s1]; C[:, t2] += Ay[:, s2]; C %= 3
                blocks.append(C)
                for i in sel:
                    m = list(mons[i]); m[y] += 1; newm.append(tuple(m))
            if not blocks: break
            mons, A = newm, np.vstack(blocks)
            emit(A)
    W = (space.cols + 63) // 64
    return (np.vstack(parts) if parts else np.zeros((0, 2 * W), np.uint64)), W

def to_base(space, P, W, rows, cols_src, cols_dst, n_dst, chunk=2000):
    """Unpack the given echelon rows in chunks, keep columns cols_src and place them at cols_dst
    of an n_dst-column space; return packed rows."""
    parts = []
    for s in range(0, len(rows), chunk):
        U = gf3.unpack(P[rows[s:s + chunk]], W, space.cols)
        Y = np.zeros((U.shape[0], n_dst), np.uint8); Y[:, cols_dst] = U[:, cols_src]
        parts.append(gf3.pack(Y)[0])
    W0 = (n_dst + 63) // 64
    return np.vstack(parts) if parts else np.zeros((0, 2 * W0), np.uint64)

def low_part(sp, gens, D2, sp0):
    """NS_{D2}(gens) cap R_{<=D}, D = sp0.D, as packed rows in sp0's columns.  Columns of sp are
    ordered by decreasing degree, so echelon rows with pivot of degree <= D span the intersection."""
    Pk, W = ns_packed(sp, gens, D2)
    P, W, piv = gf3.rref(None, parallel=True, packed=(Pk, W, sp.cols)); del Pk
    rows = np.nonzero(sp.deg[piv] <= sp0.D)[0]
    low = np.nonzero(sp.deg <= sp0.D)[0]
    dst = np.array([sp0.idx[sp.mons[i]] for i in low])
    return to_base(sp, P, W, rows, low, dst, sp0.cols)

def base_gens(inst):
    v = inst['v']; tA = sum(len(b) for b in inst['base']); gens, k = [], v
    for b in inst['base']:
        gens += block_generators(b, list(range(k, k + len(b))), v, v + tA); k += len(b)
    return gens, tA

def count(job):
    inst = make(*job); v, D = inst['v'], inst['D']
    gens, tA = base_gens(inst); sp0 = Space(v, tA, D)
    out = dict(name=inst['name'], D=D, dims={})
    for D2 in range(D, D + 5):
        out['dims'][D2] = int(low_part(Space(v, tA, D2), gens, D2, sp0).shape[0])   # dim NS_{D2} cap R_{<=D}
    return out

def solution_values(sp, gens, chunk=4000):
    """Rows: the monomial values (sp's columns) at every point of {0,1}^nv x F3^nt where all gens vanish."""
    import itertools
    POW = np.array([[1, 0, 0], [1, 1, 1], [1, 2, 1]], dtype=np.uint8)
    E = np.array(sp.mons, dtype=np.int64)
    G = np.array([sp.vec(g) for g in gens if g], dtype=np.int32).T
    grid = itertools.product(*([range(2)] * sp.nv + [range(3)] * sp.nt)); out = []
    while True:
        pts = np.array(list(itertools.islice(grid, chunk)), dtype=np.int64)
        if pts.shape[0] == 0: break
        V = np.ones((pts.shape[0], sp.cols), dtype=np.uint8)
        for j in range(sp.n): V = (V * POW[pts[:, j:j + 1], E[None, :, j]]) % 3
        out.append(V[((V.astype(np.int32) @ G) % 3 == 0).all(axis=1)])
    return np.vstack(out)

def rank_packed(Pk, W, cols):
    return int(gf3.rref(None, parallel=True, packed=(np.ascontiguousarray(Pk), W, cols))[2].shape[0])

def losses(args):
    job, hs, axiomP = args
    inst0 = make(*job); v, D = inst0['v'], inst0['D']
    gens, tA = base_gens(inst0); sp0 = Space(v, tA, D); W0 = (sp0.cols + 63) // 64
    low = {D2: low_part(Space(v, tA, D2), gens, D2, sp0) for D2 in range(D, D + 5)}
    S = solution_values(sp0, gens)
    out = dict(name=inst0['name'], D=D, axiomP=axiomP, dim_base=int(low[D].shape[0]),
               nsolutions=int(S.shape[0]), per_h=[])
    for h in hs:
        inst = make(job[0], v, D, job[3], h, job[5], 'random', job[7])
        if inst['base'] != inst0['base']:
            out['per_h'].append(dict(h=h, skipped='base changed when drawing the fresh block')); continue
        fv = list(range(v + tA, v + tA + h)); sp1 = Space(v, tA + h, D, fresh_vars=fv)
        g1 = [{e + (0,) * h: c for e, c in g.items()} for g in gens] + block_generators(inst['fresh'], fv, v, v + tA + h)
        if axiomP: g1.append(block_product(inst['fresh'], fv, v, v + tA + h))   # control: P as an axiom
        Pk, W1 = ns_packed(sp1, g1, D, perm=sp1.fresh_first)
        P1, W1, piv1 = gf3.rref(None, parallel=True, packed=(Pk, W1, sp1.cols)); del Pk
        rows = np.nonzero(piv1 >= sp1.nfresh)[0]                   # rows free of fresh monomials
        src = np.arange(sp1.nfresh, sp1.cols)                       # fresh-first coordinates
        dst = np.array([sp0.idx[sp1.mons[i][:v + tA]] for i in sp1.fresh_first[sp1.nfresh:]])
        X = to_base(sp1, P1, W1, rows, src, dst, sp0.cols); del P1
        # Every base solution extends to a solution of base + B (r = e_j if some L_j vanishes there,
        # else r = 0), so every element of X must vanish on the base solutions.  This checks X only:
        # it tests neither the rows of low[D'] nor that X is complete.
        sound = True
        for s in range(0, X.shape[0], 500):
            Xs = gf3.unpack(X[s:s + 500], W0, sp0.cols).astype(np.int32)
            for t in range(0, S.shape[0], 4000):
                sound &= bool(((S[t:t + 4000].astype(np.int32) @ Xs.T) % 3 == 0).all())
        outside = {D2: rank_packed(np.vstack([L, X]), W0, sp0.cols) - L.shape[0] for D2, L in low.items()}
        lag = next((D2 - D for D2 in sorted(outside) if outside[D2] == 0), None)
        out['per_h'].append(dict(h=h, cols=sp1.cols, dim_existing=int(X.shape[0]), sound=sound, outside=outside, loss=lag))
        print(json.dumps({'name': out['name'], 'h': h, 'axiomP': axiomP, 'rise': outside[D], 'outside': outside,
                          'loss': lag, 'sound': sound}), flush=True)
    return out

if __name__ == '__main__':
    mode, cfg = sys.argv[1], sys.argv[2]
    jobs = [j for j in CONFIGS[cfg] if j[6] == 'random']
    if mode == 'count':
        sat = {(r['name'], r['D']): r for r in json.load(open(os.path.join(HERE, '..', 'odd_prime_c3_conservativity_20260922', 'c3_saturation.json')))}
        with Pool(min(4, len(jobs))) as pool: res = pool.map(count, jobs)
        for r in res:
            sem = sat[(r['name'], r['D'])]['semantic']; r['semantic'] = sem
            r['room'] = {D2: sem - d for D2, d in r['dims'].items()}
            print(json.dumps({k: r[k] for k in ('name', 'D', 'semantic', 'room')}), flush=True)
        json.dump(res, open(os.path.join(HERE, f'ns_count_{cfg}.json'), 'w'), indent=1)
    if mode == 'losses':
        axiomP = '--axiomP' in sys.argv; hs = [int(h) for h in sys.argv[3:] if h != '--axiomP']
        nw = int(os.environ.get('NS_WORKERS', '4'))
        with Pool(min(nw, len(jobs))) as pool: res = pool.map(losses, [(j, hs, axiomP) for j in jobs], chunksize=1)
        json.dump(res, open(os.path.join(HERE, f'ns_losses_{cfg}{"_axiomP" if axiomP else ""}.json'), 'w'), indent=1)
