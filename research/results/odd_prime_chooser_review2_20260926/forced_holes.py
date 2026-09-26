#!/usr/bin/env python3
"""Forced holes in the singleton-plus-hole family under a uniform order (prop:cell-block-implications).

Model: n holes, m = n+1 pigeons, a uniform order on the n*m cells.  Hole s keeps its top-k cells T_s.
A cell (i,s) is exceptional for t' when it ranks above the k-th cell of t'.  Hole t' is forced
(derivably occupied by one pigeon's row) when some pigeon i has all its kept cells (i in T_s)
non-exceptional for t', i.e. min over its kept cells of the rank is worse than theta_t' (the rank of
t''s k-th cell).  Pigeons with no kept cell are deleted outright, which refutes, so we record them too.
Reports, for n = 200, 800 and k = 2..16, the fraction of forced holes and the number of pigeons
without kept cells, averaged over 5 orders.
"""
import json, sys
import numpy as np

rng = np.random.default_rng(20261001)
out = {}
for n in (200, 800):
    m = n + 1
    for k in (2, 4, 6, 8, 10, 12, 16):
        fr, iso = [], []
        for _ in range(5):
            rank = rng.permutation(n * m).reshape(m, n)          # rank[i, s], smaller is better
            order = np.argsort(rank, axis=0)                     # pigeons sorted per hole
            kept = np.zeros((m, n), dtype=bool)
            kept[order[:k, :], np.arange(n)] = True
            theta = rank[order[k - 1, :], np.arange(n)]          # rank of each hole's k-th cell
            best = np.where(kept, rank, n * m + 1).min(axis=1)   # each pigeon's best kept rank
            has = best <= n * m
            Rstar = best[has].max() if has.any() else -1
            fr.append(float(np.mean(theta < Rstar)))
            iso.append(int((~has).sum()))
        out[f'n={n}, k={k}'] = {'forced_fraction': float(np.mean(fr)), 'pigeons_without_kept_cells': float(np.mean(iso)),
                                'ln_n': float(np.log(n))}
        print(n, k, out[f'n={n}, k={k}'], flush=True)
if '--out' in sys.argv:
    json.dump(out, open(sys.argv[sys.argv.index('--out') + 1], 'w'), indent=1)
