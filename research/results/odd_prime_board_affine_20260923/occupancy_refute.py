"""PC refutation test for column-type (occupancy) affine systems on weak unary PHP over F_3.  A column-type form is
l_phi = sum_{i,j} phi(j) x_ij = sum_j phi(j) C_j (C_j the column sums).  For r forms and every right-hand side c in F_3^r,
decides whether PHP + {l_phi_b = c_b} has a degree-D PC refutation (exact closure, random_conditioning_fast.QSpace), and
compares with random affine systems of the same size.  Also reports whether the occupancy reduction explains the outcome:
is there a Boolean y in {0,1}^n with sum y = n+1 (mod 3) and sum_j phi_b(j) y_j = c_b for all b?
Robustness of the system: the least Q such that some nonzero combination (mod constants) is constant after deleting Q+1 labels.
Usage: --n --D --rs --trials --seed"""
import argparse, itertools, json, os, sys, time
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', 'odd_prime_one_count_20260922'))
sys.path.insert(0, os.path.join(HERE, '..', 'odd_prime_alignment_mechanism_20260922'))
from random_conditioning_fast import QSpace, refuted, base_rows, rref_stack
import gf3
from scipy import sparse
def close(space, P, W, piv, chunk=40):
    """Same closure as random_conditioning_fast.close, in smaller chunks converted to uint8 per variable: at n=8, D=3 the
    original chunk of 400 rows times 72 variables needs about 5 GB of dense integers."""
    cols = space.cols
    while True:
        old = P.shape[0]; low = np.nonzero(space.deg[piv] <= space.D - 1)[0]; Pold = P
        for s in range(0, len(low), chunk):
            Lm = sparse.csr_matrix(gf3.unpack(Pold[low[s:s + chunk]], W, cols), dtype=np.int32)
            prod = np.vstack([((Lm @ My).toarray() % 3).astype(np.uint8) for My in space.mult])
            P, W, piv = rref_stack(P, W, cols, prod)
        if P.shape[0] == old: return P, W, piv
def closure_of(space, gens):
    M = np.array([space.vec(g) for g in gens], dtype=np.uint8)
    P, W, piv = gf3.rref(M, parallel=True)
    return close(space, P, W, piv)
ap = argparse.ArgumentParser(); ap.add_argument('--n', type=int, default=6); ap.add_argument('--D', type=int, default=3)
ap.add_argument('--rs', default='1,2,3'); ap.add_argument('--trials', type=int, default=2); ap.add_argument('--seed', type=int, default=0)
ap.add_argument('--phis', default=None); ap.add_argument('--out'); opt = ap.parse_args(); n, D = opt.n, opt.D; rng = np.random.default_rng(opt.seed)
t0 = time.time(); space = QSpace(n, D); base = base_rows(n)
def form_eq(F, c):   # F: (n+1, n) row functions; equation l_F - c = 0
    p = {(i * n + j,): int(F[i, j]) for i in range(n + 1) for j in range(n) if F[i, j] % 3}
    if c % 3: p[()] = (-c) % 3
    return p
def robustness(phis):
    best = n
    for co in itertools.product(range(3), repeat=len(phis)):
        if not any(co): continue
        psi = sum(a * p for a, p in zip(co, phis)) % 3
        # distance from psi to the constants = number of labels to delete before psi becomes constant
        d = min(int((psi != c).sum()) for c in range(3))
        best = min(best, d - 1)   # psi is Q-robust iff d >= Q+1
    return best
def occupancy_sat(phis, cs):
    for y in itertools.product((0, 1), repeat=n):
        y = np.array(y)
        if (y.sum() - (n + 1)) % 3: continue
        if all((phi @ y - c) % 3 == 0 for phi, c in zip(phis, cs)): return True
    return False
res = dict(n=n, D=D, php_alone_refuted=bool(refuted(space, *closure_of(space, base)[:2])), runs=[])
print('PHP alone refuted:', res['php_alone_refuted'], f'({time.time()-t0:.0f}s)', flush=True)
for r in map(int, opt.rs.split(',')):
    for tr in range(opt.trials):
        while True:
            if opt.phis: phis = [np.array([int(x) for x in s_.split(',')]) for s_ in opt.phis.split(';')][tr * r:(tr + 1) * r]; break
            phis = [rng.integers(0, 3, size=n) for _ in range(r)]
            M = np.array(phis + [np.ones(n, dtype=int)])
            from itertools import product as _p
            if robustness(phis) >= 0: break
        Q = robustness(phis); col_ref = 0; col_explained = 0; per_rhs = []
        for cs in itertools.product(range(3), repeat=r):
            eqs = [form_eq(np.tile(phi, (n + 1, 1)), c) for phi, c in zip(phis, cs)]
            P, W, _ = closure_of(space, base + eqs); ref = bool(refuted(space, P, W))
            sat = occupancy_sat(phis, cs); col_ref += ref; col_explained += (ref == (not sat))
            sym = [int((2 * phi.sum() * pow(n % 3, 1, 3)) % 3) if n % 3 else None for phi in phis]
            per_rhs.append(dict(c=list(cs), refuted=ref, occupancy_solution=sat, symmetric_value=(list(cs) == [int(((n + 1) * phi.sum() * (1 if n % 3 == 1 else 2)) % 3) for phi in phis]) if n % 3 else None))
        rnd_ref = 0
        for s in range(3 ** r if r <= 2 else 9):
            Fs = [rng.integers(0, 3, size=(n + 1, n)) for _ in range(r)]; cs = rng.integers(0, 3, size=r)
            P, W, _ = closure_of(space, base + [form_eq(F, c) for F, c in zip(Fs, cs)]); rnd_ref += bool(refuted(space, P, W))
        row = dict(r=r, trial=tr, phis=[p.tolist() for p in phis], column_robustness_Q=Q, column_rhs=3 ** r, column_refuted=col_ref,
                   refuted_iff_no_occupancy_solution=col_explained, random_systems=3 ** r if r <= 2 else 9, random_refuted=rnd_ref, per_rhs=per_rhs)
        res['runs'].append(row); print(row, f'({time.time()-t0:.0f}s)', flush=True)
if opt.out: json.dump(res, open(opt.out, 'w'), indent=1, default=int)
