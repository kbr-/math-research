"""Does the tensor dependency lift on a weak unary base?

Statement tested (prop:first-fall-criterion): a dependency among clause tops lifts iff the same combination of
clause functions vanishes on the base. Base: the weak unary base on m = 7 rows and n = 6 columns (0/1 matrices with
at most one 1 per column, total occupancy = m mod 3). Family: the tensor family with c = 2, m = 3 of
thm:tensor-relations, realized by six random dense affine forms y_1..y_6 of the 42 board variables: member w in
PG(2,3) has forms f1 = w . (y_1, y_2, y_3) + a1 and f2 = w . (y_4, y_5, y_6) + a2, prefix P = s f1 + t f2 (s != 0) and
clause (1 - f2^2) P^2, the indicator of {f2 = 0, P != 0}. The tops sum to zero; the clause sum F is evaluated at every
base point. Also reported: whether the six forms map the base onto F_3^6. Pure numpy; runs in about a second.
"""
import argparse
import itertools

import numpy as np

ap = argparse.ArgumentParser()
ap.add_argument('--seeds', type=int, default=3)
args = ap.parse_args()

m, n = 7, 6
# base points: choose for each column a row or none (index m), then keep occupancy = m mod 3
choices = np.array(list(itertools.product(range(m + 1), repeat=n)), dtype=np.int64)
occ = (choices < m).sum(axis=1)
choices = choices[occ % 3 == m % 3]
X = np.zeros((len(choices), m * n), dtype=np.int64)
for j in range(n):
    rows = choices[:, j]
    hit = rows < m
    X[np.nonzero(hit)[0], rows[hit] * n + j] = 1
assert (X.reshape(-1, m, n).sum(axis=1) <= 1).all() and (X.sum(axis=1) % 3 == m % 3).all()

pts = [w for w in itertools.product(range(3), repeat=3) if any(w) and w[next(i for i in range(3) if w[i])] == 1]
assert len(pts) == 13
for seed in range(1, args.seeds + 1):
    rng = np.random.default_rng(seed)
    A = rng.integers(0, 3, size=(m * n, 6))
    b = rng.integers(0, 3, size=6)
    Y = (X @ A + b) % 3
    image = len({tuple(r) for r in Y})
    F = np.zeros(len(X), dtype=np.int64)
    for w in pts:
        a1, a2 = rng.integers(0, 3, size=2)
        s, t = rng.integers(1, 3), rng.integers(0, 3)
        f1 = (Y[:, :3] @ np.array(w) + a1) % 3
        f2 = (Y[:, 3:] @ np.array(w) + a2) % 3
        P = (s * f1 + t * f2) % 3
        F += (f2 == 0) & (P != 0)
    F %= 3
    print(f'seed {seed}: base points {len(X)}, image of the six forms {image} of 729, '
          f'clause sum nonzero at {int((F != 0).sum())} base points')
