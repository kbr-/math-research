"""For the same random equation sequences as random_conditioning.py, find the least M at which the
span of the first M linear parts, modulo the row equations, contains a nonzero combination
supported on at most s rows (s = 2D by default).

Modulo rows, a linear part is the tuple of row functions f_i: holes -> F_3 up to constants;
coordinates f_i(j) - f_i(n-1), j < n-1.  A span V (of independent vectors) meets the subspace of
combinations supported on a row set T iff projecting V onto the coordinates of rows outside T
drops its rank.  Every row set of size s is tried.

Usage: width_drop.py --n N --D D --seeds S --out PATH
"""
import argparse, itertools, json, os, sys
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, '..', 'odd_prime_alignment_mechanism_20260922'))
import gf3
from random_conditioning import random_eq


def row_coords(p, n):
    rows, holes = n + 1, n
    f = np.zeros((rows, holes), dtype=np.int64)
    for m, c in p.items():
        if len(m) == 1:
            u = m[0]; f[u // holes, u % holes] = c
    return ((f[:, :holes - 1] - f[:, holes - 1:holes]) % 3).astype(np.uint8)   # rows x (n-1)


def min_support_drop(vecs, n, s):
    """least M such that span(vecs[:M]) meets some row-set-of-size-s subspace; None if never."""
    rows = n + 1
    for M in range(1, len(vecs) + 1):
        V = np.array([v.reshape(-1) for v in vecs[:M]], dtype=np.uint8)
        r = gf3.rank(V)
        if r < M:
            return M, 'dependent'                          # a combination with zero linear part
        for T in itertools.combinations(range(rows), s):
            keep = [i for i in range(rows) if i not in T]
            W = np.array([v[keep].reshape(-1) for v in vecs[:M]], dtype=np.uint8)
            if gf3.rank(W) < M:
                return M, list(T)
    return None, None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--n', type=int, required=True)
    ap.add_argument('--D', type=int, required=True)
    ap.add_argument('--seeds', type=int, default=5)
    ap.add_argument('--out', required=True)
    a = ap.parse_args()
    n, D = a.n, a.D
    v = n * (n + 1)
    dim = (n + 1) * (n - 1)
    out = {'n': n, 'D': D, 'support_rows': 2 * D, 'seeds': []}
    for s in range(a.seeds):
        seed = 1000 * n + 10 * D + s
        rng = np.random.default_rng(seed)
        eqs = [random_eq(rng, v) for _ in range(dim + 2)]
        vecs = [row_coords(p, n) for p in eqs]
        M, T = min_support_drop(vecs, n, 2 * D)
        out['seeds'].append({'seed': seed, 'first_M_with_2D_row_combination': M, 'rows': T})
        print(f'n={n} D={D} seed {s}: first M with a combination on <= {2*D} rows: {M} {T}', flush=True)
    with open(a.out, 'w') as f:
        json.dump(out, f, indent=1)


if __name__ == '__main__':
    main()
