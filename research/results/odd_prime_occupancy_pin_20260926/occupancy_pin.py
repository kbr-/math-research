"""Occupancy pin test (odd-prime thread, 26 September 2026).

Statement tested (a candidate route for column-statistic blocks under random prefixes): weak unary
PHP^{n+1}_n over F_3 plus the pins C_j = o*_j for every hole j, where C_j = sum_i x_ij is the column
sum and o* in {0,1}^n has sum o* = n+1 (mod 3), i.e. |E*| = 2 (mod 3) empty holes, has no PC
refutation of low degree.  The pinned system is an onto weak PHP of n+1 pigeons into n - |E*| holes
whose counts agree mod 3, so linear counting does not refute it.  For each n, D and |E*| the script
reports whether the exact degree-D closure contains 1, next to PHP alone, and a control whose
counts disagree mod 3 (|E*| = 1, refuted at degree 1 by counting), and the comparison
without onto: only the |E*| empty holes pinned, which is weak PHP of n+1 pigeons into n - |E*| holes.  Uses the recorded closure code
(occupancy_refute.close, random_conditioning_fast.QSpace).
Usage: occupancy_pin.py --ns 5,6,7 --Ds 2,3 [--es 1,2,4,5] --out FILE"""
import argparse, json, os, sys, time
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', 'odd_prime_one_count_20260922'))
sys.path.insert(0, os.path.join(HERE, '..', 'odd_prime_alignment_mechanism_20260922'))
from random_conditioning_fast import QSpace, refuted, base_rows
import numpy as np
import gf3
from scipy import sparse
from random_conditioning_fast import rref_stack

def close(space, P, W, piv, chunk=40):
    cols = space.cols
    while True:
        old = P.shape[0]; low = np.nonzero(space.deg[piv] <= space.D - 1)[0]; Pold = P
        for s in range(0, len(low), chunk):
            Lm = sparse.csr_matrix(gf3.unpack(Pold[low[s:s + chunk]], W, cols), dtype=np.int32)
            prod = np.vstack([((Lm @ My).toarray() % 3).astype(np.uint8) for My in space.mult])
            P, W, piv = rref_stack(P, W, cols, prod)
        if P.shape[0] == old: return P, W, piv

def is_refuted(space, gens):
    P, W, piv = gf3.rref(np.array([space.vec(g) for g in gens], dtype=np.uint8), parallel=True)
    P, W, piv = close(space, P, W, piv)
    return bool(refuted(space, P, W))

def pin(n, j, val):
    p = {(i * n + j,): 1 for i in range(n + 1)}
    if val % 3: p[()] = (-val) % 3
    return p

ap = argparse.ArgumentParser(); ap.add_argument('--ns', default='5,6'); ap.add_argument('--Ds', default='2,3')
ap.add_argument('--es', default='1,2,4,5'); ap.add_argument('--out', required=True); opt = ap.parse_args()
res = []; t0 = time.time()
for n in map(int, opt.ns.split(',')):
    for D in map(int, opt.Ds.split(',')):
        space = QSpace(n, D); base = base_rows(n)
        row = dict(n=n, D=D, php_refuted=is_refuted(space, base), pins={})
        for e in map(int, opt.es.split(',')):
            if e > n: continue
            o = [0] * e + [1] * (n - e)
            row['pins'][str(e)] = dict(counts_agree_mod3=((n - e) - (n + 1)) % 3 == 0,
                                       refuted=is_refuted(space, base + [pin(n, j, o[j]) for j in range(n)]),
                                       empties_only_refuted=is_refuted(space, base + [pin(n, j, 0) for j in range(e)]))
        res.append(row); print(json.dumps(row), f'({time.time()-t0:.0f}s)', flush=True)
        json.dump(res, open(opt.out, 'w'), indent=1)
