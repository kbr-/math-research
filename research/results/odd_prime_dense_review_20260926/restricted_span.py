#!/usr/bin/env python3
"""Span of restricted selectors 1 - L^2 (multilinear reduction over F_3) for blocks after restriction to v coordinates.

Tests the falsification attempt of the dense-block route review: under the matching-and-expander restriction of
thm:cell-family-w, a block of uniformly random dense affine forms restricts to uniformly random affine forms on the
v residual coordinates it meets, and the span dimension of their selectors (lem:span-restriction) is
min(N, 1 + v + C(v,2)); a block of dense forms confined to an affine space of dimension d has span at most
(d+1)(d+2)/2 whatever v is. Exact GF(3) ranks of the coefficient vectors in the monomial basis {1, x_c, x_c x_d}.
"""
import itertools, json, sys
import numpy as np

P = 3
rng = np.random.default_rng(20260926)

def rank3(M):
    M = M.copy() % P
    r = 0
    rows, cols = M.shape
    for c in range(cols):
        piv = next((i for i in range(r, rows) if M[i, c]), None)
        if piv is None:
            continue
        M[[r, piv]] = M[[piv, r]]
        M[r] = (M[r] * pow(int(M[r, c]), P - 2, P)) % P
        for i in range(rows):
            if i != r and M[i, c]:
                M[i] = (M[i] - M[i, c] * M[r]) % P
        r += 1
    return r

def selector_vec(a, b, v):
    """Multilinear coefficients of 1 - (a.x + b)^2 over F_3 with x Boolean."""
    mons = [()] + [(c,) for c in range(v)] + list(itertools.combinations(range(v), 2))
    idx = {m: i for i, m in enumerate(mons)}
    out = np.zeros(len(mons), dtype=np.int64)
    out[idx[()]] += 1 - b * b
    for c in range(v):
        out[idx[(c,)]] -= a[c] * a[c] + 2 * b * a[c]      # x_c^2 = x_c
    for c, d in itertools.combinations(range(v), 2):
        out[idx[(c, d)]] -= 2 * a[c] * a[d]
    return out % P

def main():
    res = []
    for v in (6, 8, 10):
        dimq = 1 + v + v * (v - 1) // 2
        for N in (10, 30, 60, 90):
            A = rng.integers(0, 3, size=(N, v)); B = rng.integers(0, 3, size=N)
            r_rand = rank3(np.array([selector_vec(A[j], B[j], v) for j in range(N)]))
            d = 2
            basis = rng.integers(0, 3, size=(d, v)); C = rng.integers(0, 3, size=(N, d))
            A2 = (C @ basis) % 3
            r_low = rank3(np.array([selector_vec(A2[j], B[j], v) for j in range(N)]))
            res.append({'v': v, 'N': N, 'quadratic_dim': dimq, 'rank_random': int(r_rand),
                        'predicted_random': min(N, dimq), 'rank_rank2': int(r_low), 'bound_rank2': (d + 1) * (d + 2) // 2})
            print(res[-1], flush=True)
    if '--out' in sys.argv:
        json.dump(res, open(sys.argv[sys.argv.index('--out') + 1], 'w'), indent=1)

if __name__ == '__main__':
    main()
