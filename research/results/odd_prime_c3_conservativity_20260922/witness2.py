"""Witness checks for general base shapes (vectorized soundness; same checks as witness.py).
Usage: witness2.py TAG[@LABEL] V D HA HB NBASE SEED...  (instances as conservativity.make builds
them from TAG; an optional @LABEL only names the output); results in c3_witness_TAG[_LABEL]_D{D}.json.  Checks: new elements of the existing part of C_D(base+B)
that are independent of C_D(base) in the base ring's own coordinates; soundness by evaluation on
every solution of the base; least D' in {D+1, D+2} with the element in C_{D'}(base)."""
import itertools, json, os, sys
import numpy as np
from conservativity import make, Space, closure, gf3, block_generators
from witness import fmt, HERE
POW = np.array([[1, 0, 0], [1, 1, 1], [1, 2, 1]], dtype=np.uint8)

def elements(inst, par=True):
    """As witness.elements, but with the parallel elimination and a packed, chunked fresh-first
    echelon form, so that only the existing-variable rows are ever unpacked."""
    v, D = inst['v'], inst['D']; tA = sum(len(b) for b in inst['base']); tB = len(inst['fresh'])
    sp0 = Space(v, tA, D); gens0, k = [], v
    for b in inst['base']:
        gens0 += block_generators(b, list(range(k, k + len(b))), v, v + tA); k += len(b)
    P0, W0, _ = closure(sp0, gens0, par=par); B0 = gf3.unpack(P0, W0, sp0.cols)
    fv = list(range(v + tA, v + tA + tB)); sp1 = Space(v, tA + tB, D, fresh_vars=fv)
    gens1 = [{e + (0,) * tB: c for e, c in g.items()} for g in gens0]
    gens1 += block_generators(inst['fresh'], fv, v, v + tA + tB)
    P1, W1, _ = closure(sp1, gens1, par=par)
    parts = []                                             # permute chunk by chunk, echelon once
    for s0 in range(0, P1.shape[0], 2000):
        Q, W2 = gf3.pack(gf3.unpack(P1[s0:s0 + 2000], W1, sp1.cols)[:, sp1.fresh_first])
        parts.append(Q)
    acc, W2, pv = gf3.rref(None, parallel=par, packed=(np.vstack(parts), W2, sp1.cols))
    del parts
    ex = gf3.unpack(acc[pv >= sp1.nfresh], W2, sp1.cols)[:, sp1.nfresh:]
    exmons = [sp1.mons[i] for i in sp1.fresh_first[sp1.nfresh:]]
    polys = [{m[:v + tA]: int(c) for m, c in zip(exmons, row) if c} for row in ex]
    new, cur = [], B0
    for p in polys:
        w = sp0.vec(p)
        if gf3.rank(np.vstack([cur, w]), parallel=par) > cur.shape[0]: new.append(p); cur = np.vstack([cur, w])
    return dict(sp0=sp0, gens0=gens0, new=new, v=v, tA=tA)

def solution_values(sp, gens, chunk=4000):
    """Rows: monomial values of sp at every solution point of gens (x Boolean, r in F3)."""
    E = np.array(sp.mons, dtype=np.int64)
    G = np.array([sp.vec(g) for g in gens], dtype=np.int32).T
    grid = itertools.product(*([range(2)] * sp.nv + [range(3)] * sp.nt))
    out = []
    while True:
        pts = np.array(list(itertools.islice(grid, chunk)), dtype=np.int64)
        if pts.shape[0] == 0: break
        V = np.ones((pts.shape[0], sp.cols), dtype=np.uint8)
        for j in range(sp.n): V = (V * POW[pts[:, j:j + 1], E[None, :, j]]) % 3
        out.append(V[((V.astype(np.int32) @ G) % 3 == 0).all(axis=1)])  # uint8 rows
    return np.vstack(out)

if __name__ == '__main__':
    tag, v, D0, hA, hB, nb = sys.argv[1], *map(int, sys.argv[2:7])
    out = []
    for seed in map(int, sys.argv[7:]):
        inst = make(tag.split('@')[0], v, D0, hA, hB, seed, 'random', nb)
        R = elements(inst)
        sp0 = R['sp0']; S = solution_values(sp0, R['gens0'])
        higher = []
        for D2 in (D0 + 1, D0 + 2):
            sp2 = Space(R['v'], R['tA'], D2); P2, W2, _ = closure(sp2, R['gens0'], par=True)
            higher.append((D2, sp2, gf3.unpack(P2, W2, sp2.cols)))
        rec = dict(name=inst['name'], base=inst['base'], fresh=inst['fresh'], n_base_solutions=int(S.shape[0]), new=[])
        for p in R['new']:
            w = sp0.vec(p).astype(np.int32)
            sound = all(((S[c:c + 2000].astype(np.int32) @ w) % 3 == 0).all() for c in range(0, S.shape[0], 2000))
            lag = None
            for D2, sp2, B2 in higher:
                if gf3.rank(np.vstack([B2, sp2.vec(p)]), parallel=True) == B2.shape[0]: lag = D2; break
            rec['new'].append(dict(poly=fmt(p, R['v']), degree=max(sum(e) for e in p), terms=len(p), sound=sound,
                                   in_base_closure_at=lag))
        print(json.dumps({'name': rec['name'], 'n_new': len(rec['new']),
                          'summary': [(n['degree'], n['terms'], n['sound'], n['in_base_closure_at']) for n in rec['new']]}), flush=True)
        out.append(rec)
    json.dump(out, open(os.path.join(HERE, f"c3_witness_{tag.replace('@', '_')}_D{D0}.json"), 'w'), indent=1)
