#!/usr/bin/env python3
"""Cube layer hiding check over F_3.

Tested statement: for k = 3 and d = 2k - 2 = 4, the space of multilinear polynomials of degree
at most d on {0,1}^M over F_3 that vanish at every point whose weight is not a positive multiple
of k is zero exactly when M >= 3k - 1 = 8. For M <= 3k - 2 the pairing construction
prod_{i<=k}(u_{2i-1} - u_{2i}) prod_{j>2k}(1 - u_j) has degree M - k <= d, so the space is nonzero.
Positive control: at d = 2k - 1 = 5 the space is nonzero for every M >= 2k, by
prod_{i<=k}(u_{2i-1} - u_{2i}) * 1_{k | r}.

For each case the script prints the dimension of the kernel of the evaluation map from
polynomials of degree <= d to the forbidden points (exact Gaussian elimination mod 3).
"""
import argparse
import itertools
import json

import numpy as np

P = 3


def rank_mod_p(a):
    a = a.copy() % P
    rows, cols = a.shape
    r = 0
    for c in range(cols):
        piv = None
        for i in range(r, rows):
            if a[i, c]:
                piv = i
                break
        if piv is None:
            continue
        a[[r, piv]] = a[[piv, r]]
        inv = 1 if a[r, c] == 1 else 2
        a[r] = (a[r] * inv) % P
        nz = np.nonzero(a[:, c])[0]
        for i in nz:
            if i != r:
                a[i] = (a[i] - a[i, c] * a[r]) % P
        r += 1
        if r == rows:
            break
    return r


def kernel_dim(k, m, d):
    monos = [s for j in range(d + 1) for s in itertools.combinations(range(m), j)]
    points = [x for x in itertools.product((0, 1), repeat=m)
              if not (sum(x) > 0 and sum(x) % k == 0)]
    a = np.zeros((len(points), len(monos)), dtype=np.int64)
    for i, x in enumerate(points):
        ones = {b for b in range(m) if x[b]}
        for j, s in enumerate(monos):
            if ones.issuperset(s):
                a[i, j] = 1
    return len(monos) - rank_mod_p(a), len(monos), len(points)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--out', required=True)
    args = ap.parse_args()
    k = 3
    cases = [(k, m, 2 * k - 2) for m in (6, 7, 8, 9)] + [(k, m, 2 * k - 1) for m in (6, 8)]
    results = []
    for k_, m, d in cases:
        assert m >= 2 * k_
        kd, nmon, npts = kernel_dim(k_, m, d)
        results.append({'k': k_, 'M': m, 'd': d, 'kernel_dim': kd,
                        'monomials': nmon, 'forbidden_points': npts})
        print(json.dumps(results[-1]), flush=True)
    with open(args.out, 'w') as fh:
        json.dump({'field': 'F_3', 'statement': __doc__.strip().splitlines()[2],
                   'results': results}, fh, indent=1)


if __name__ == '__main__':
    main()
