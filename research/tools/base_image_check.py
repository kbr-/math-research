"""Image of dense affine forms on the weak unary base (route review of the dense-cover line).

Question: beyond capacity, refutations inside a dense cover can only come from the weak base's image under the
family's forms being a proper, structured subset of the value space. For random dense forms, is the image of the
weak base on 7 rows and 6 columns (0/1 matrices with at most one 1 per column, occupancy = 7 mod 3; 36057 points)
all of F_3^r, and how far are the value frequencies from uniform? r = 6, 8, 9 forms (3^9 = 19683 < 36057),
three seeds each. Reports the image size and the largest deviation of a single form's or a pair of forms' value
frequencies from uniform (anti-concentration and pairwise independence, the quantities the review's leads need).
Pure numpy; about a second.
"""
import itertools

import numpy as np

m, n = 7, 6
choices = np.array(list(itertools.product(range(m + 1), repeat=n)), dtype=np.int64)
choices = choices[(choices < m).sum(axis=1) % 3 == m % 3]
X = np.zeros((len(choices), m * n), dtype=np.int64)
for j in range(n):
    rows = choices[:, j]
    hit = rows < m
    X[np.nonzero(hit)[0], rows[hit] * n + j] = 1
assert (X.reshape(-1, m, n).sum(axis=1) <= 1).all() and (X.sum(axis=1) % 3 == m % 3).all()
N = len(X)
print(f'base points {N}')
for r in (6, 8, 9):
    for seed in (1, 2, 3):
        rng = np.random.default_rng(seed)
        Y = (X @ rng.integers(0, 3, size=(m * n, r)) + rng.integers(0, 3, size=r)) % 3
        codes = Y @ (3 ** np.arange(r))
        image = len(np.unique(codes))
        single = max(abs(np.bincount(Y[:, i], minlength=3) / N - 1 / 3).max() for i in range(r))
        pair = max(abs(np.bincount(3 * Y[:, i] + Y[:, j], minlength=9) / N - 1 / 9).max()
                   for i in range(r) for j in range(i + 1, r))
        print(f'r={r} seed={seed}: image {image} of {3 ** r}; max single-form deviation {single:.4f}, '
              f'max pair deviation {pair:.4f}')
