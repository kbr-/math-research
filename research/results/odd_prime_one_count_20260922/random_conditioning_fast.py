"""Faster exact version of random_conditioning.py, with the same equations per seed.

Differences, each exact:
- Work in the quotient by the collision monomials X_ij X_i'j: every multilinear monomial containing
  two cells of one hole lies in the degree-D closure (a collision generator times variables), so
  columns are the collision-free monomials and multiplication into a collision gives zero.
- Incremental search: closures of nested prefixes are nested, so the closure for M+1 equations is
  computed from the echelon basis for M.  The scan starts at a lower bracket (default: the dimension
  law's value minus 3); if that prefix is already refuted, it restarts lower.
- Elimination uses the OpenMP library (run with --threads through the launcher).

Usage: random_conditioning_fast.py --n N --D D --seeds S [--start M] --out PATH
"""
import argparse, itertools, json, os, sys, time
import numpy as np
from scipy import sparse
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, '..', 'odd_prime_alignment_mechanism_20260922'))
import gf3
from random_conditioning import random_eq


class QSpace:
    def __init__(self, n, D):
        self.n_holes, self.D = n, D
        v = n * (n + 1); self.v = v
        hole = lambda u: u % n
        mons = []
        for k in range(D, -1, -1):
            for c in itertools.combinations(range(v), k):
                if len({hole(u) for u in c}) == k:
                    mons.append(c)
        self.mons = mons; self.idx = {m: i for i, m in enumerate(mons)}
        self.cols = len(mons); self.deg = np.array([len(m) for m in mons])
        self.mult = []
        for y in range(v):
            rows, cols = [], []
            for i, m in enumerate(mons):
                if len(m) <= D - 1:
                    if y in m:
                        rows.append(i); cols.append(i)
                    elif all(hole(u) != hole(y) for u in m):
                        rows.append(i); cols.append(self.idx[tuple(sorted(m + (y,)))])
            self.mult.append(sparse.csr_matrix((np.ones(len(rows), dtype=np.int32), (rows, cols)),
                                               shape=(self.cols, self.cols)))

    def vec(self, p):
        out = np.zeros(self.cols, dtype=np.uint8)
        for m, c in p.items():
            if m in self.idx:                              # collision monomials are zero
                out[self.idx[m]] = (int(out[self.idx[m]]) + c) % 3
        return out


def rref_stack(P, W, cols, rows_u8):
    Q, _ = gf3.pack(rows_u8)
    stack = Q if P is None else np.vstack([P, Q])
    return gf3.rref(None, parallel=True, packed=(stack, W, cols))


def close(space, P, W, piv, chunk=400):
    cols = space.cols
    while True:
        old = P.shape[0]
        low = np.nonzero(space.deg[piv] <= space.D - 1)[0]
        Pold = P
        for s in range(0, len(low), chunk):
            L = sparse.csr_matrix(gf3.unpack(Pold[low[s:s + chunk]], W, cols), dtype=np.int32)
            prod = np.vstack([(L @ My).toarray() % 3 for My in space.mult]).astype(np.uint8)
            P, W, piv = rref_stack(P, W, cols, prod)
        if P.shape[0] == old:
            return P, W, piv


def refuted(space, P, W):
    Q, _ = gf3.pack(space.vec({(): 1})[None, :])
    return gf3.rref(None, parallel=True, packed=(np.vstack([P, Q]), W, space.cols))[2].shape[0] == P.shape[0]


def closure_of(space, gens):
    M = np.array([space.vec(g) for g in gens], dtype=np.uint8)
    P, W, piv = gf3.rref(M, parallel=True)
    return close(space, P, W, piv)


def base_rows(n):
    holes = n
    gens = []
    for i in range(n + 1):
        p = {(i * holes + j,): 1 for j in range(holes)}; p[()] = 2
        gens.append(p)
    return gens


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--n', type=int, required=True)
    ap.add_argument('--D', type=int, required=True)
    ap.add_argument('--seeds', type=int, default=3)
    ap.add_argument('--start', type=int, default=None)
    ap.add_argument('--out', required=True)
    a = ap.parse_args()
    n, D = a.n, a.D
    t0 = time.time()
    space = QSpace(n, D)
    v = space.v; dim = (n + 1) * (n - 1)
    law = (n + 1 - 2 * D) * (n - 1) + 1
    start = max(0, law - 3) if a.start is None else a.start
    base = base_rows(n)
    P, W, piv = closure_of(space, base)
    base_ref = refuted(space, P, W)
    res = {'n': n, 'D': D, 'quotient_columns': space.cols, 'law_value': law, 'php_alone_refuted': base_ref,
           'seeds': []}
    print(f'n={n} D={D} quotient cols={space.cols} PHP alone refuted: {base_ref} ({time.time()-t0:.1f}s)', flush=True)
    if not base_ref:
        for s in range(a.seeds):
            seed = 1000 * n + 10 * D + s
            rng = np.random.default_rng(seed)
            eqs = [random_eq(rng, v) for _ in range(dim + 2)]
            m0 = start
            while True:
                P, W, piv = closure_of(space, base + eqs[:m0])
                if not refuted(space, P, W) or m0 == 0:
                    break
                m0 = max(0, m0 - 4)
            M = m0
            while not refuted(space, P, W):
                M += 1
                P, W, piv = rref_stack(P, W, space.cols, space.vec(eqs[M - 1])[None, :])
                P, W, piv = close(space, P, W, piv)
            res['seeds'].append({'seed': seed, 'threshold_M': M, 'scan_start': m0})
            print(f'  seed {s}: least refuted M = {M} (law {law}; {time.time()-t0:.1f}s)', flush=True)
    res['seconds'] = round(time.time() - t0, 1)
    with open(a.out, 'w') as f:
        json.dump(res, f, indent=1)


if __name__ == '__main__':
    main()
