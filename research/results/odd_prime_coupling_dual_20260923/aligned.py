"""Aligned specialization for the row Horace pieces: form k has row-i part x_{i,a} with a = k mod N, and its part on the
other rows avoids label a (column a zero), so each label class lives on one slice.  Tested statement: full, trace,
residual and coupling ranks equal their expected values (as in horace_pieces.py) for every M up to 1.15 capacity.
Hypothesis asserted: every form nonconstant modulo constants on every row.
Usage: python3 aligned.py --ns 6,7 --seed S --out OUT.json"""
import argparse, json, os, sys, time
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', 'odd_prime_horace_pieces_20260923'))
from horace_pieces import Board, series
ap = argparse.ArgumentParser(); ap.add_argument('--ns', default='6,7'); ap.add_argument('--seed', type=int, default=1)
ap.add_argument('--out', required=True); a = ap.parse_args(); t0 = time.time(); res = []
for n in map(int, a.ns.split(',')):
    R, N = n + 1, n; b = Board(R, N); i = R - 1; rng = np.random.default_rng(a.seed)
    contains = np.array([i in S for S in b.sets[3]])
    colsT = np.nonzero(~contains[b.block_of_col])[0]; colsR = np.nonzero(contains[b.block_of_col])[0]
    g3, g3T, kR = b.Kb.shape[1], len(colsT), len(colsR); g1, g1T = R * (N - 1), (R - 1) * (N - 1)
    cap = g3 / (g1 - 1); Mmax = int(1.15 * cap) + 2; forms = []
    while len(forms) < Mmax:
        lab = len(forms) % N; f = rng.integers(0, 3, size=(R, N)); f[:, lab] = 0; f[i, :] = 0; f[i, lab] = 1
        if all(len(set(f[x])) > 1 for x in range(R)): forms.append(f)
    full = series([b.D2K(f, np.arange(g3)) for f in forms], g3)
    fz = [f.copy() for f in forms]
    for f in fz: f[i, :] = 0
    trace = series([b.D2K(f, colsT) for f in fz], g3T); resid = series([b.D2K(f, colsR) for f in fz], kR); rows = []
    for M in range(1, Mmax + 1):
        rF, rT, rR = full[M - 1], trace[M - 1], resid[M - 1]
        rows.append(dict(M=M, full=rF, full_exp=min(g3, M * (g1 - 1)), trace=rT, trace_exp=min(g3T, M * (g1T - 1)),
                         resid=rR, resid_exp=min(kR, M * (N - 1)), coupling=rF - rT - rR,
                         coupling_exp=min(max(M * (g1T - 1) - rT, 0), kR - rR)))
    dev = {k: [r['M'] for r in rows if r[k] != r[k + '_exp']] for k in ('full', 'trace', 'resid', 'coupling')}
    print(f'n={n}: capacity {cap:.1f}; deviations', {k: (v[:5], len(v)) for k, v in dev.items()}, f'({time.time()-t0:.0f}s)', flush=True)
    res.append(dict(n=n, seed=a.seed, capacity=cap, rows=rows, deviations=dev)); json.dump(res, open(a.out, 'w'), indent=1)
