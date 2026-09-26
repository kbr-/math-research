#!/usr/bin/env python3
"""Immunity of one randomized-prefix block in form-value space (Alekhnovich-Razborov lead).

Statement tested: treat a block's h forms as independent F_3 variables y. The block's
randomized-prefix clauses g_i Q^C (g_i = 1 - y_i^2, Q^C = prod_j (1 - (sum_i c_ji g_i)^2))
vanish exactly on the allowed set A_C = {y : pattern(y) = 0 or C pattern(y) != 0}, where
pattern_i = [y_i = 0]. Its immunity is the least degree of a nonzero function on F_3^h
(individual degrees <= 2) vanishing on A_C. The clause gives immunity <= 4t + 2, and a
counting bound (a nonzero function of degree d on F_3^h is nonzero on at least 3^(h-d/2)
points... roughly) gives about 2t. The run reports where the immunity lies, for uniform C
and, as a control, for C with a zero column (the hole-family degeneracy).
"""
import argparse, itertools, json
import numpy as np

def rank_mod3(M):
    M = M.copy() % 3
    r = 0
    rows, cols = M.shape
    for c in range(cols):
        piv = np.nonzero(M[r:, c])[0]
        if piv.size == 0:
            continue
        p = r + piv[0]
        M[[r, p]] = M[[p, r]]
        if M[r, c] == 2:
            M[r] = (2 * M[r]) % 3
        nz = np.nonzero(M[:, c])[0]
        nz = nz[nz != r]
        if nz.size:
            M[nz] = (M[nz] - np.outer(M[nz, c], M[r])) % 3
        r += 1
        if r == rows:
            break
    return r

def immunity(h, C):
    pts = np.array(list(itertools.product(range(3), repeat=h)), dtype=np.int64)
    pat = (pts == 0).astype(np.int64)
    s = (pat @ C.T) % 3
    allowed = (pat.sum(1) == 0) | (s != 0).any(1)
    A = pts[allowed]
    exps = sorted(itertools.product(range(3), repeat=h), key=sum)
    exps = np.array(exps, dtype=np.int64)
    degs = exps.sum(1)
    # evaluate every monomial on A: prod_k y_k^{e_k}, with 0^0 = 1
    powers = np.stack([np.ones_like(A), A, (A * A) % 3], axis=0)   # [e, point, k]
    vals = np.ones((len(exps), len(A)), dtype=np.int64)
    for k in range(h):
        vals = (vals * powers[exps[:, k], :, k]) % 3
    for d in range(0, 2 * h + 1):
        block = vals[degs <= d]
        if rank_mod3(block) < block.shape[0]:
            return d, int((~allowed).sum())
    return None, int((~allowed).sum())

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--out', required=True)
    ap.add_argument('--samples', type=int, default=8)
    args = ap.parse_args()
    rng = np.random.default_rng(20260926)
    rows = []
    for h in (3, 4, 5, 6):
        for t in (1, 2):
            if t >= h:
                continue
            for kind in ('uniform', 'zero column'):
                for _ in range(args.samples if kind == 'uniform' else 2):
                    C = rng.integers(0, 3, size=(t, h))
                    if kind == 'zero column':
                        C[:, 0] = 0
                    d, err = immunity(h, C)
                    rows.append(dict(h=h, t=t, kind=kind, C=C.tolist(), immunity=d,
                                     error_points=err, clause_degree=4 * t + 2))
                    print(h, t, kind, d, err, flush=True)
    json.dump(rows, open(args.out, 'w'), indent=1)

if __name__ == '__main__':
    main()
