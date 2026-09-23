"""Degree-four annihilators of squares in the top algebra A of weak unary PHP over F_3, computed component-wise.
A = F_3[x_ij]/(x_ij^2, x_ij x_i'j, sum_j x_ij), n holes, n+1 pigeons.  A_k splits by the pigeon multiset of its
monomials; each component's relations are R_i*m (i in the multiset, m of multiset U-{i}).  We reduce every product
to its normal form modulo each component's fully reduced relation echelon, so no global elimination is needed.
Reports gamma_2, gamma_4 and dim Ann_{A_2}(l^2) = gamma_2 - rank(E -> E l^2) for uniform l.
Usage: --n N --samples K --workers W --out PATH [--support S] (S = number of pigeons carrying l; default all)"""
import argparse, itertools, json, os, sys, time
from collections import defaultdict
from multiprocessing import Pool
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', 'odd_prime_alignment_mechanism_20260922'))
import gf3
ap = argparse.ArgumentParser(); ap.add_argument('--n', type=int, default=6); ap.add_argument('--samples', type=int, default=3)
ap.add_argument('--workers', type=int, default=12); ap.add_argument('--support', type=int, default=0)
ap.add_argument('--seed', type=int, default=0); ap.add_argument('--out'); opt = ap.parse_args()
n = opt.n; P1 = n + 1; v = P1 * n
hole = lambda u: u % n; pig = lambda u: u // n
def key(m): return tuple(sorted(pig(u) for u in m))
def component_monomials(U):
    """All collision-free monomials with pigeon multiset U: assign distinct holes to the multiset's entries."""
    out = set()
    for hs in itertools.permutations(range(n), len(U)):
        m = tuple(sorted(i * n + j for i, j in zip(U, hs)))
        if len(set(m)) == len(U): out.add(m)
    return sorted(out)
def build(U):
    cols = component_monomials(U); I = {m: c for c, m in enumerate(cols)}
    rows = []
    for i in sorted(set(U)):
        V = list(U); V.remove(i)
        for m in component_monomials(tuple(V)):
            hs = {hole(u) for u in m}; r = np.zeros(len(cols), dtype=np.uint8)
            for j in range(n):
                if j not in hs: r[I[tuple(sorted(m + (i * n + j,)))]] = 1
            rows.append(r)
    if not rows: return U, cols, np.zeros(0, dtype=np.int32), np.zeros((0, len(cols)), dtype=np.uint8)
    E, W, piv = gf3.rref(np.array(rows), full=True)
    return U, cols, piv, gf3.unpack(E, W, len(cols))
def quotient(k, workers):
    comps = sorted({tuple(sorted(c)) for c in itertools.combinations_with_replacement(range(P1), k)})
    with Pool(workers) as pool: res = pool.map(build, comps, chunksize=1)
    Q = {}; off = 0
    for U, cols, piv, E in res:
        pivset = set(piv.tolist()); nonp = np.array([c for c in range(len(cols)) if c not in pivset], dtype=np.int64)
        Q[U] = dict(I={m: c for c, m in enumerate(cols)}, cols=cols, piv=piv, nonp=nonp, E=E[:, nonp].astype(np.int64), off=off)
        off += len(nonp)
    return Q, off
def normal_form(poly, Q, dim):
    """poly: dict monomial -> coeff (collision-free, degree k).  Returns its coordinates in the quotient basis."""
    out = np.zeros(dim, dtype=np.int64); byc = defaultdict(list)
    for m, c in poly.items():
        if c % 3: byc[key(m)].append((m, c))
    for U, terms in byc.items():
        q = Q[U]; x = np.zeros(len(q['cols']), dtype=np.int64)
        for m, c in terms: x[q['I'][m]] = c
        nf = x[q['nonp']] - (x[q['piv']] @ q['E'] if len(q['piv']) else 0)
        out[q['off']:q['off'] + len(q['nonp'])] = nf % 3
    return out
def mul(p1, p2):
    out = {}
    for m1, c1 in p1.items():
        h1 = {hole(u) for u in m1}
        for m2, c2 in p2.items():
            if h1 & {hole(u) for u in m2}: continue
            mm = tuple(sorted(m1 + m2)); out[mm] = (out.get(mm, 0) + c1 * c2) % 3
    return out
def square(l):
    nz = [int(u) for u in np.nonzero(l)[0]]; out = {}
    for a, u in enumerate(nz):
        for w in nz[a + 1:]:
            if hole(u) != hole(w): out[(u, w)] = (out.get((u, w), 0) + 2 * int(l[u]) * int(l[w])) % 3
    return out
if __name__ == '__main__':
    t0 = time.time()
    Q2, g2 = quotient(2, opt.workers); Q4, g4 = quotient(4, opt.workers)
    print(f'n={n}: gamma_2={g2} gamma_4={g4} ({time.time()-t0:.0f}s)', flush=True)
    basis2 = [q['cols'][c] for q in Q2.values() for c in q['nonp']]
    rng = np.random.default_rng(opt.seed); anns = []
    for s in range(opt.samples):
        l = rng.integers(0, 3, size=v)
        if opt.support:
            keep = rng.choice(P1, size=opt.support, replace=False)
            for i in range(P1):
                if i not in keep: l[i * n:(i + 1) * n] = 0
        sq = square(l)
        rows = np.array([normal_form(mul({m: 1}, sq), Q4, g4) for m in basis2], dtype=np.uint8)
        anns.append(g2 - gf3.rank(rows, parallel=True))
        print(f'sample {s}: dim Ann_A2(l^2) = {anns[-1]} ({time.time()-t0:.0f}s)', flush=True)
    res = dict(n=n, gamma_2=g2, gamma_4=g4, support=opt.support or P1, ann=anns)
    if opt.out: json.dump(res, open(opt.out, 'w'), indent=1, default=int)
    print(res, flush=True)
