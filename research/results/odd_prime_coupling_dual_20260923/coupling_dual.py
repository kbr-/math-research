"""Coupling condition (C) of the row Horace corollary under specializations of the removed row's coefficients.

Tested statement: for forms l = l' + l_i (l' on the board without row i, l_i = sum_a c_{l,a} x_{i,a}) with l' uniform
random and l_i from a family, the coupling Z_res -> coker T has rank min(M(gamma'_1-1) - rank T, dim Z_res) for every M
up to 1.15 times the total capacity.  Trace and residual ranks depend only on l' and are computed once; only the full
double-point map is recomputed per family.  Families for l_i:
  uniform  : uniform random (the reference, as in horace_pieces.py)
  rowcell  : one cell x_{i,a(l)}, labels a(l) = l mod N (balanced), coefficient 1
  samecell : one cell x_{i,0} for every form (control; by a count its coupling image lies in one label slot and
             must fall short once the needed rank exceeds dim of that slot's dual, about M = 38 at n = 6)
Hypothesis asserted: every form is nonconstant modulo constants on every row.
Usage: python3 coupling_dual.py --ns 6,7 --seed S --out OUT.json"""
import argparse, json, os, sys, time
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', 'odd_prime_horace_pieces_20260923'))
from horace_pieces import Board, series
FAMILIES = ('uniform', 'rowcell', 'samecell')
def run(n, seed, t0):
    R, N = n + 1, n; b = Board(R, N); i = R - 1
    contains = np.array([i in S for S in b.sets[3]])
    colsT = np.nonzero(~contains[b.block_of_col])[0]; colsR = np.nonzero(contains[b.block_of_col])[0]
    g3, g3T, kR = b.Kb.shape[1], len(colsT), len(colsR); g1, g1T = R * (N - 1), (R - 1) * (N - 1)
    cap = g3 / (g1 - 1); Mmax = int(1.15 * cap) + 2
    rng = np.random.default_rng(seed); base = []
    while len(base) < Mmax:
        f = rng.integers(0, 3, size=(R, N)); f[i, :] = 0
        if all(len(set(f[x])) > 1 for x in range(R - 1)): base.append(f)
    trace = series([b.D2K(f, colsT) for f in base], g3T)
    resid = series([b.D2K(f, colsR) for f in base], kR)
    print(f'n={n}: trace and residual done ({time.time()-t0:.0f}s)', flush=True)
    out = dict(n=n, seed=seed, gamma3=g3, gamma3_trace=g3T, dim_residual=kR, capacity=cap, families={})
    for fam in FAMILIES:
        forms = []
        for k, f in enumerate(base):
            g = f.copy()
            if fam == 'uniform':
                while len(set(g[i])) < 2: g[i] = rng.integers(0, 3, size=N)
            else:
                g[i, :] = 0; g[i, (k % N) if fam == 'rowcell' else 0] = 1
            assert all(len(set(g[x])) > 1 for x in range(R)); forms.append(g)
        full = series([b.D2K(f, np.arange(g3)) for f in forms], g3); rows = []
        for M in range(1, Mmax + 1):
            rF, rT, rR = full[M - 1], trace[M - 1], resid[M - 1]
            rows.append(dict(M=M, full=rF, full_exp=min(g3, M * (g1 - 1)), trace=rT, resid=rR, coupling=rF - rT - rR,
                             coupling_exp=min(max(M * (g1T - 1) - rT, 0), kR - rR)))
        dev = [r['M'] for r in rows if r['coupling'] != r['coupling_exp']]
        tdev = [r['M'] for r in rows if r['trace'] != min(g3T, r['M'] * (g1T - 1))]
        rdev = [r['M'] for r in rows if r['resid'] != min(kR, r['M'] * (N - 1))]
        print(f'  {fam}: coupling deviations {dev[:6]}... ({len(dev)}); trace dev {len(tdev)}, resid dev {len(rdev)} '
              f'({time.time()-t0:.0f}s)', flush=True)
        out['families'][fam] = dict(rows=rows, coupling_deviations=dev, trace_deviations=tdev, resid_deviations=rdev)
    return out
if __name__ == '__main__':
    ap = argparse.ArgumentParser(); ap.add_argument('--ns', default='6,7'); ap.add_argument('--seed', type=int, default=1)
    ap.add_argument('--out', required=True); a = ap.parse_args(); t0 = time.time(); res = []
    for n in map(int, a.ns.split(',')):
        res.append(run(n, a.seed, t0)); json.dump(dict(results=res), open(a.out, 'w'), indent=1)
