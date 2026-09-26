"""Onto weak PHP on a rectangular board (odd-prime thread, 26 September 2026).

Statement tested (conj:occupancy-pinned-php at its first nonvacuous sizes): over F_3, the system of
m pigeons and N holes with Booleanity, collisions x_ij x_i'j = 0, rows sum_j x_ij = 1 and onto
columns sum_i x_ij = 1, with m - N = 3 (counts agree mod 3), is compared with the control without
the onto columns (weak PHP of m pigeons into N holes).  The occupancy-pinned system of the entry, weak
PHP^{n+1}_n with e = 2 holes pinned empty and the rest pinned occupied, is this system with
m = n + 1, N = n - 2, after the degree-2 deletion of the empty holes.  For each board and degree D the
script reports whether the exact degree-D PC closure contains 1, for both systems, and whether one onto
equation C_0 - 1 already lies in the control's degree-D closure.  The closure follows the recorded
collision-quotient closure (random_conditioning_fast.close) with its own close(): all variable
products of a chunk come from one sparse product; elimination is the recorded gf3 module, and the
monomial space is built for an m x N board.
Usage: onto_rect.py --boards 8x5 --Ds 3,4 --out FILE"""
import argparse, itertools, json, os, sys, time
import numpy as np
from scipy import sparse
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', 'odd_prime_one_count_20260922'))
sys.path.insert(0, os.path.join(HERE, '..', 'odd_prime_alignment_mechanism_20260922'))
import gf3


def distinct_holes(c, N):
    return len(set(map(N.__rmod__, c))) == len(c)


def monomials_of_size(v, N, k):
    return [c for c in itertools.combinations(range(v), k) if distinct_holes(c, N)]


class RectSpace:
    """Collision-free multilinear monomials of degree <= D on an m x N board (cell u = i*N + j)."""
    def __init__(self, m, N, D):
        self.D = D
        v = m * N; self.v = v
        mons = []
        for k in range(D, -1, -1):
            mons.extend(monomials_of_size(v, N, k))
        self.mons = mons; self.idx = {mo: i for i, mo in enumerate(mons)}
        self.cols = len(mons); self.deg = np.array([len(mo) for mo in mons])
        # all variable multiplications side by side: row i, column y*cols + j means y * mon_i = mon_j
        blocks = [self._mult(y, N) for y in range(v)]
        self.mall = sparse.hstack(blocks, format='csr')

    def _mult(self, y, N):
        rows, cols = [], []
        for i, mo in enumerate(self.mons):
            if len(mo) > self.D - 1:
                continue
            if y in mo:
                rows.append(i); cols.append(i)
            elif all(u % N != y % N for u in mo):
                rows.append(i); cols.append(self.idx[tuple(sorted(mo + (y,)))])
        return sparse.csr_matrix((np.ones(len(rows), dtype=np.int32), (rows, cols)), shape=(self.cols, self.cols))

    def vec(self, p):
        out = np.zeros(self.cols, dtype=np.uint8)
        for mo, c in p.items():
            if mo in self.idx:
                out[self.idx[mo]] = (int(out[self.idx[mo]]) + c) % 3
        return out


def rref_stack(P, W, cols, rows_u8):
    Q, _ = gf3.pack(rows_u8)
    return gf3.rref(None, parallel=True, packed=(np.vstack([P, Q]), W, cols))


def products(space, P, W, rows):
    """All products y * r for the given echelon rows r and every variable y, as uint8 rows."""
    L = sparse.csr_matrix(gf3.unpack(P[rows], W, space.cols), dtype=np.int32)
    prod = (L @ space.mall).toarray() % 3
    return prod.reshape(len(rows) * space.v, space.cols).astype(np.uint8)


def close(space, P, W, piv, chunk=150):
    """Degree-D PC closure: add y * r for every echelon row r of degree <= D-1 until stable (the
    recorded random_conditioning_fast.close, with the variable loop replaced by one sparse product)."""
    while True:
        old = P.shape[0]; low = np.nonzero(space.deg[piv] <= space.D - 1)[0]; Pold = P
        for s in range(0, len(low), chunk):
            P, W, piv = rref_stack(P, W, space.cols, products(space, Pold, W, low[s:s + chunk]))
        if P.shape[0] == old:
            return P, W, piv


def refuted(space, P, W):
    Q, _ = gf3.pack(space.vec({(): 1})[None, :])
    return gf3.rref(None, parallel=True, packed=(np.vstack([P, Q]), W, space.cols))[2].shape[0] == P.shape[0]


def linear(cells, rhs):
    p = {(u,): 1 for u in cells}
    p[()] = (-rhs) % 3
    return p


def is_refuted(space, gens):
    P, W, piv = gf3.rref(np.array([space.vec(g) for g in gens], dtype=np.uint8), parallel=True)
    P, W, piv = close(space, P, W, piv)
    return bool(refuted(space, P, W))


def row_eqs(m, N):
    return [linear(range(i * N, (i + 1) * N), 1) for i in range(m)]


def onto_eqs(m, N):
    return [linear(range(j, m * N, N), 1) for j in range(N)]


def in_closure(space, P, W, poly):
    Q, _ = gf3.pack(space.vec(poly)[None, :])
    return gf3.rref(None, parallel=True, packed=(np.vstack([P, Q]), W, space.cols))[2].shape[0] == P.shape[0]


def run_case(m, N, D):
    space = RectSpace(m, N, D)
    rows, onto = row_eqs(m, N), onto_eqs(m, N)
    P, W, piv = close(space, *gf3.rref(np.array([space.vec(g) for g in rows], dtype=np.uint8), parallel=True))
    return dict(m=m, N=N, D=D, columns=space.cols, control_refuted=bool(refuted(space, P, W)),
                onto_eq_in_control_closure=in_closure(space, P, W, onto[0]),
                onto_refuted=is_refuted(space, rows + onto))


ap = argparse.ArgumentParser(); ap.add_argument('--boards', default='8x5'); ap.add_argument('--Ds', default='3')
ap.add_argument('--out', required=True); opt = ap.parse_args()
res = []; t0 = time.time()
cases = [(tuple(map(int, b.split('x'))), D) for b in opt.boards.split(',') for D in map(int, opt.Ds.split(','))]
for (m, N), D in cases:
    res.append(run_case(m, N, D)); print(json.dumps(res[-1]), f'({time.time()-t0:.0f}s)', flush=True)
    json.dump(res, open(opt.out, 'w'), indent=1)
