"""Are the 3-torsion directions of weak PHP's NS lattice PC-derivable over F_3? (odd-prime thread, 26 Sept 2026)

Tested statement (sharper route to conj:three-integral-php-certificates): with L_d the Z-lattice of multilinear
degree-<=d multiples of the weak-base axioms (rows sum_j x_ij - 1, collisions x_ij x_i'j) and Sat(L_d) its
3-saturation, is Sat(L_d) mod 3 contained in C_d, the degree-d PC closure over F_3 of the same axioms?
If so, e_1 not in C_d (Razborov's bound for d < n/2 + 1) gives e_1 not in Sat(L_d) + 3 Z_(3)^N.
Method: one exact lifting step of the F_3 left kernel of the generator matrix G (as in hensel_saturation.py,
which reached the rational rank in one step at these sizes), then rank tests over F_3 of C_d alone and of C_d
plus the lifted rows. C_d by the recorded closure method (conservativity.py), with the multiplication maps stacked.
Usage: torsion_pc.py --cases 5:3,4:3 --out FILE"""
import argparse, json, os, sys, time
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
for sub in ('odd_prime_hensel_saturation_20260926', 'odd_prime_closed_routes_review_20260926',
            'odd_prime_c3_conservativity_20260922', 'odd_prime_alignment_mechanism_20260922'):
    sys.path.insert(0, os.path.join(HERE, '..', sub))
import gf3
from hensel_saturation import left_kernel_mod3
from php_lattice_torsion import lattice_rows, to_sparse
import itertools
from scipy import sparse


def indicator(c, nv):
    e = [0] * nv
    for k in c:
        e[k] = 1
    return tuple(e)


class Space:
    """Multilinear F_3 polynomials of degree <= D in nv Boolean variables, the Boolean case of
    conservativity.Space (same exponent-tuple keys and decreasing-degree column order), built from
    combinations instead of enumerating the whole cube."""
    def __init__(self, nv, nt, D):
        assert nt == 0
        self.nv, self.n, self.D = nv, nv, D
        mons = [indicator(c, nv) for j in range(D, -1, -1) for c in itertools.combinations(range(nv), j)]
        self.mons = mons; self.idx = {e: i for i, e in enumerate(mons)}; self.cols = len(mons)
        self.deg = np.array([sum(e) for e in mons])
        self.mult = [self._mult(y) for y in range(nv)]

    def _mult(self, y):
        rows = [i for i, e in enumerate(self.mons) if sum(e) <= self.D - 1]
        cols = [self.idx[self.mons[i][:y] + (1,) + self.mons[i][y + 1:]] for i in rows]
        return sparse.csr_matrix((np.ones(len(rows), dtype=np.int64), (rows, cols)), shape=(self.cols, self.cols))

    def vec(self, p):
        v = np.zeros(self.cols, dtype=np.uint8)
        for e, c in p.items():
            v[self.idx[e]] = c
        return v


def closure(space, gens, chunk=150):
    """Degree-D PC closure over F_3 (as conservativity.closure): V <- V + y*(V cap R_{<=D-1}), with all
    variables' multiplication maps stacked into one sparse matrix so each chunk needs one product."""
    cols, nvar = space.cols, len(space.mult)
    mall = sparse.hstack([My.astype(np.int32) for My in space.mult]).tocsr()
    P, W, piv = gf3.rref(np.array([space.vec(g) for g in gens], dtype=np.uint8), parallel=True)
    while True:
        old = P.shape[0]; low = np.nonzero(space.deg[piv] <= space.D - 1)[0]; Pold = P
        for s in range(0, len(low), chunk):
            L = sparse.csr_matrix(gf3.unpack(Pold[low[s:s + chunk]], W, cols), dtype=np.int32)
            prod = ((L @ mall).toarray() % 3).astype(np.uint8).reshape(-1, nvar, cols).reshape(-1, cols)
            Q, _ = gf3.pack(prod)
            P, W, piv = gf3.rref(None, parallel=True, packed=(np.vstack([P, Q]), W, cols))
        if P.shape[0] == old:
            return P, W, piv


def to_exp(m, nv):
    e = [0] * nv
    for k in m:
        e[k] = 1
    return tuple(e)


def generator_matrix(n, d):
    rows, cols = lattice_rows(n, d)
    idx = {m: i for i, m in enumerate(cols)}
    G = np.zeros((len(rows), len(cols)), dtype=np.float64)
    for i, r in enumerate(to_sparse(rows, idx)):
        for j, c in r:
            G[i, j] += c
    return rows, cols, G


def rank_packed(P, W, cols, extra):
    Q, _ = gf3.pack(extra)
    return gf3.rref(None, parallel=True, packed=(np.vstack([P, Q]), W, cols))[2].shape[0]


def run(n, d):
    nv = (n + 1) * n
    rows, cols, G = generator_matrix(n, d)
    Y = left_kernel_mod3(G)
    U = np.mod(Y @ G / 3, 3).astype(np.uint8)                # lifted rows (Sat directions) mod 3
    space = Space(nv, 0, d)
    perm = np.array([space.idx[to_exp(m, nv)] for m in cols])  # lattice column -> space column
    gens = [{to_exp(m, nv): c % 3 for m, c in r.items() if c % 3} for r in rows]
    P, W, piv = closure(space, [g for g in gens if g])
    dimC = P.shape[0]
    Uc = np.zeros((U.shape[0], space.cols), dtype=np.uint8); Uc[:, perm] = U
    Gc = np.zeros((G.shape[0], space.cols), dtype=np.uint8); Gc[:, perm] = np.mod(G, 3).astype(np.uint8)
    one = np.zeros((1, space.cols), dtype=np.uint8); one[0, space.idx[tuple([0] * nv)]] = 1
    return dict(n=n, pigeons=n + 1, d=d, cols=space.cols, dim_PC_closure=dimC,
                rank_closure_plus_L=rank_packed(P, W, space.cols, Gc),
                rank_closure_plus_lifted=rank_packed(P, W, space.cols, Uc),
                one_in_closure=(rank_packed(P, W, space.cols, one) == dimC),
                lifted_rows=int(U.shape[0]), rank_lifted_mod3=int(gf3.rank(U, parallel=True)) if U.size else 0)


def main():
    ap = argparse.ArgumentParser(); ap.add_argument('--cases', required=True); ap.add_argument('--out', required=True)
    a = ap.parse_args(); out = []
    for case in a.cases.split(','):
        n, d = map(int, case.split(':')); t0 = time.time()
        res = run(n, d); res['seconds'] = round(time.time() - t0, 1)
        out.append(res); print(json.dumps(res), flush=True)
        with open(a.out, 'w') as fh:
            json.dump(out, fh, indent=1)


if __name__ == '__main__':
    main()
