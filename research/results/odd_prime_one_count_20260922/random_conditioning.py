"""Degree-D PC refutability of ordinary weak unary PHP^{n+1}_n over F_3 plus M random affine equations.

Ring F_3[x_ij]/(x^2 - x), i in rows (n+1), j in holes (n).  Base generators: row equations
sum_j x_ij - 1 and column collisions x_ij x_i'j.  Added: M affine equations sum c_ij x_ij + c0,
all coefficients uniform in F_3.  PC closure at ceiling D is computed exactly (closure() of the
ternary conservativity tester), and the script reports the least M whose system has 1 in C_D,
found by bisection on nested prefixes of one random sequence of equations per seed.

Usage: random_conditioning.py --n N --D D --seeds S --out PATH
"""
import argparse, itertools, json, os, sys, time
import numpy as np
from scipy import sparse
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', 'odd_prime_c3_conservativity_20260922'))
sys.path.insert(0, os.path.join(HERE, '..', 'odd_prime_alignment_mechanism_20260922'))
import gf3
from conservativity import closure, contains_one


class Space:
    """Multilinear monomials of degree <= D in v Boolean variables, ordered by decreasing degree."""
    def __init__(self, v, D):
        self.n, self.D = v, D
        mons = [c for k in range(D, -1, -1) for c in itertools.combinations(range(v), k)]
        self.mons = mons
        self.idx = {m: i for i, m in enumerate(mons)}
        self.cols = len(mons)
        self.deg = np.array([len(m) for m in mons])
        self.mult = []
        for y in range(v):
            rows, cols = [], []
            for i, m in enumerate(mons):
                if len(m) <= D - 1:
                    t = tuple(sorted(set(m) | {y}))
                    rows.append(i); cols.append(self.idx[t])
            self.mult.append(sparse.csr_matrix((np.ones(len(rows), dtype=np.int64), (rows, cols)),
                                               shape=(self.cols, self.cols)))

    def vec(self, p):
        out = np.zeros(self.cols, dtype=np.uint8)
        for m, c in p.items():
            out[self.idx[m]] = (int(out[self.idx[m]]) + c) % 3
        return out


def const_poly(c):
    # contains_one() calls space.vec(const(1, space.n)) from the tester; keys there are exponent
    # tuples, so it is re-implemented below for this monomial encoding.
    return {(): c % 3}


def has_one(space, P, W):
    Q, _ = gf3.pack(space.vec({(): 1})[None, :])
    r = gf3.rref(None, packed=(np.vstack([P, Q]), W, space.cols))[2].shape[0]
    return r == P.shape[0]


def base_gens(n):
    rows, holes = n + 1, n
    x = lambda i, j: i * holes + j
    gens = []
    for i in range(rows):
        p = {(x(i, j),): 1 for j in range(holes)}
        p[()] = 2                                          # -1
        gens.append(p)
    for j in range(holes):
        for i, k in itertools.combinations(range(rows), 2):
            gens.append({tuple(sorted((x(i, j), x(k, j)))): 1})
    return gens


def random_eq(rng, v):
    c = rng.integers(0, 3, size=v)
    p = {(u,): int(c[u]) for u in range(v) if c[u]}
    c0 = int(rng.integers(0, 3))
    if c0: p[()] = c0
    return p


def refutes(space, gens):
    P, W, piv = closure(space, gens)
    return has_one(space, P, W)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--n', type=int, required=True)
    ap.add_argument('--D', type=int, required=True)
    ap.add_argument('--seeds', type=int, default=5)
    ap.add_argument('--out', required=True)
    a = ap.parse_args()
    n, D = a.n, a.D
    v = n * (n + 1)
    space = Space(v, D)
    dim_forms = (n + 1) * (n - 1)
    base = base_gens(n)
    t0 = time.time()
    base_ref = refutes(space, base)
    res = {'n': n, 'D': D, 'vars': v, 'columns': space.cols, 'form_space_dim_mod_rows': dim_forms,
           'php_alone_refuted': base_ref, 'seeds': []}
    print(f'n={n} D={D} v={v} cols={space.cols} PHP alone refuted: {base_ref}', flush=True)
    if not base_ref:
        for s in range(a.seeds):
            rng = np.random.default_rng(1000 * n + 10 * D + s)
            eqs = [random_eq(rng, v) for _ in range(dim_forms + 2)]
            lo, hi = 0, dim_forms + 2                      # invariant: lo not refuted, hi refuted
            assert refutes(space, base + eqs[:hi])
            while hi - lo > 1:
                mid = (lo + hi) // 2
                if refutes(space, base + eqs[:mid]): hi = mid
                else: lo = mid
            res['seeds'].append({'seed': 1000 * n + 10 * D + s, 'threshold_M': hi})
            print(f'  seed {s}: least refuted M = {hi} (form-space dim {dim_forms})', flush=True)
    res['seconds'] = round(time.time() - t0, 1)
    with open(a.out, 'w') as f:
        json.dump(res, f, indent=1)


if __name__ == '__main__':
    main()
