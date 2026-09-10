"""Exact checks of the affine core/residual decomposition criterion.

No PHP proof search is done. Numerical checks concern finite-field subspaces,
optimal orderings/partitions in the stated criterion, and the explicit graph
subspace obstruction. All ranks are exact modulo a small prime.
"""
from __future__ import annotations
import itertools, json, math, os, time
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path
import numpy as np

ROOT = Path(__file__).resolve().parent

def rref(a: np.ndarray, p: int):
    a = np.array(a, dtype=np.int64, copy=True) % p
    row = 0
    pivots = []
    for col in range(a.shape[1]):
        candidates = np.flatnonzero(a[row:, col])
        if not len(candidates):
            continue
        pivot = row + int(candidates[0])
        a[[row, pivot]] = a[[pivot, row]]
        a[row] = (a[row] * pow(int(a[row, col]), -1, p)) % p
        factors = a[:, col].copy()
        factors[row] = 0
        a = (a - factors[:, None] * a[row][None, :]) % p
        pivots.append(col)
        row += 1
        if row == a.shape[0]:
            break
    return a[:row], pivots

def orthogonal(a: np.ndarray, p: int):
    rr, piv = rref(a, p)
    ambient = a.shape[1]
    free = np.array([j for j in range(ambient) if j not in piv], dtype=np.int64)
    out = np.zeros((len(free), ambient), dtype=np.int64)
    if len(free):
        out[np.arange(len(free)), free] = 1
        if piv:
            out[:, np.array(piv)] = (-rr[:, free].T) % p
    return out

def intersection_dimensions(bases, p):
    s, ambient = len(bases), bases[0].shape[1]
    annihilators = [orthogonal(a, p) for a in bases]
    dims = np.empty(1 << s, dtype=np.int64)
    dims[0] = ambient
    for mask in range(1, 1 << s):
        joined = np.concatenate([annihilators[i] for i in range(s) if mask >> i & 1], axis=0)
        dims[mask] = ambient - len(rref(joined, p)[1])
    return dims

def greedy_order(mask, space_dims, intersection_dims):
    order, radius = [], 0
    while mask:
        active = np.flatnonzero(mask & (1 << np.arange(len(space_dims))))
        deficits = space_dims[active] - intersection_dims[mask]
        chosen = int(active[np.argmin(deficits)])
        radius = max(radius, int(space_dims[chosen] - intersection_dims[mask]))
        order.append(chosen)
        mask ^= 1 << chosen
    return radius, order

def inflation(r, h, p):
    return np.maximum(1, ((p - 1) * np.asarray(r) + h - 1) // h - 1)

def exact_partition_dp(space_dims, intersection_dims, p, h, D):
    """Best certified degree, allowing every batch order and batch partition."""
    s = len(space_dims)
    radii = np.zeros(1 << s, dtype=np.int64)
    largest = np.zeros(1 << s, dtype=np.int64)
    for mask in range(1, 1 << s):
        radii[mask], _ = greedy_order(mask, space_dims, intersection_dims)
        active = np.flatnonzero(mask & (1 << np.arange(s)))
        largest[mask] = space_dims[active].max()
    t_core = inflation(radii, h, p)
    t_zero = inflation(largest, h, p)
    dp = np.full(1 << s, np.iinfo(np.int64).max // 16, dtype=np.int64)
    dp[0] = D
    all_masks = np.arange(1 << s, dtype=np.int64)
    last_batch = np.zeros(1 << s, dtype=np.int64)
    for mask in range(1, 1 << s):
        subsets = all_masks[(all_masks != 0) & ((all_masks & mask) == all_masks)]
        before = dp[mask ^ subsets]
        costs = np.minimum(t_core[subsets] * before + (p - 1), t_zero[subsets] * before)
        idx = int(np.argmin(costs))
        dp[mask], last_batch[mask] = costs[idx], subsets[idx]
    return int(dp[-1]), radii, last_batch

def check_random_case(spec):
    p, seed = spec
    start = time.perf_counter()
    rng = np.random.default_rng(seed)
    ambient, s = 8, 6
    bases = []
    for i in range(s):
        rows = int(rng.integers(1, ambient + 1))
        a, _ = rref(rng.integers(0, p, size=(rows, ambient)), p)
        if not len(a):
            a = np.eye(ambient, dtype=np.int64)[:1]
        bases.append(a)
    dims = np.array([len(a) for a in bases], dtype=np.int64)
    intdims = intersection_dimensions(bases, p)
    permutations_checked = 0
    for mask in range(1, 1 << s):
        active = np.flatnonzero(mask & (1 << np.arange(s)))
        orders = np.array(list(itertools.permutations(active.tolist())), dtype=np.int64)
        suffixes = np.bitwise_or.accumulate((1 << orders)[:, ::-1], axis=1)[:, ::-1]
        all_costs = (dims[orders] - intdims[suffixes]).max(axis=1)
        greedy, _ = greedy_order(mask, dims, intdims)
        assert greedy == int(all_costs.min())
        # Independent min-max obstruction formula, over all subsets of this mask.
        inner = []
        for sub in range(1, 1 << s):
            if sub & mask == sub:
                ids = np.flatnonzero(sub & (1 << np.arange(s)))
                inner.append(int(dims[ids].min() - intdims[sub]))
        assert greedy == max(inner)
        permutations_checked += len(orders)
    D, h = 7, 2
    optimum, _, _ = exact_partition_dp(dims, intdims, p, h, D)
    assert optimum <= D + (p - 1) * s  # all singleton cores are always an option
    return {'type':'ordering','p':p,'seed':seed,'subsets':63,
            'permutations_checked':permutations_checked,'best_certified_degree':optimum,
            'elapsed_worker_s':time.perf_counter()-start}

def multiplication_matrices(p, d, modulus):
    """All multiplication maps in F_p[t]/(monic modulus), columns are basis images."""
    q = p ** d
    elements = ((np.arange(q)[:, None] // (p ** np.arange(d))[None, :]) % p).astype(np.int64)
    out = np.empty((q, d, d), dtype=np.int64)
    current = elements.copy()
    mod = np.array(modulus[:d], dtype=np.int64)
    for j in range(d):
        out[:, :, j] = current
        high = current[:, -1].copy()
        current = np.roll(current, 1, axis=1)
        current[:, 0] = 0
        current = (current - high[:, None] * mod[None, :]) % p
    return out

def all_invertible(batch, p):
    """Exact, vectorized simultaneous Gaussian elimination of square matrices."""
    a = np.array(batch, dtype=np.int64, copy=True) % p
    count, d, _ = a.shape
    ids = np.arange(count)
    for col in range(d):
        nonzero = a[:, col:, col] != 0
        assert nonzero.any(axis=1).all(), 'singular matrix detected'
        rows = col + nonzero.argmax(axis=1)
        pivot = a[ids, rows].copy()
        old = a[:, col].copy()
        a[ids, rows] = old
        inverses = np.array([0] + [pow(v, -1, p) for v in range(1, p)], dtype=np.int64)
        a[:, col] = (pivot * inverses[pivot[:, col]][:, None]) % p
        factors = a[:, :, col].copy()
        factors[:, col] = 0
        a = (a - factors[:, :, None] * a[:, col, :][:, None, :]) % p
    assert np.array_equal(a, np.broadcast_to(np.eye(d, dtype=np.int64), a.shape))

def check_spread_case(spec):
    p, d, modulus, h = spec
    start = time.perf_counter()
    n = p ** d
    copies = (n*n - 1) // (2*d)
    r = copies * d
    mats = multiplication_matrices(p, d, modulus)
    ia, ib = np.triu_indices(n, 1)
    all_invertible((mats[ia] - mats[ib]) % p, p)
    # Pairwise injectivity of every difference also certifies the modulus is a field.
    quotient_checks = 0
    if n <= 9:
        m, width = n+1, 1+n*(n+1)
        H = np.zeros((m, width), dtype=np.int64)
        for row in range(m):
            H[row, 0] = -1
            H[row, 1+row*n:1+(row+1)*n] = 1
        coordinates = np.array([1+i*n+j for i in range(m) for j in range(n-1)][:2*r])
        def embedded(index):
            alpha = np.kron(np.eye(copies, dtype=np.int64), mats[index])
            a = np.zeros((r, width), dtype=np.int64)
            a[:, coordinates[:r]] = np.eye(r, dtype=np.int64)
            a[:, coordinates[r:]] = alpha.T
            return a
        for x,y in [(0,1),(1,2),(2,3)]:
            both = np.concatenate([H, embedded(x), embedded(y)], axis=0)
            assert len(rref(both,p)[1]) == m+2*r
            constant = np.zeros((1,width),dtype=np.int64); constant[0,0]=1
            assert len(rref(np.concatenate([both,constant]),p)[1]) == m+2*r+1
            quotient_checks += 2
    D = 3*h+1
    t = int(inflation(r,h,p))
    msmall = min(n,8)
    sdims = np.full(msmall,r,dtype=np.int64)
    idims = np.zeros(1<<msmall,dtype=np.int64); idims[0] = 2*r
    for i in range(msmall): idims[1<<i] = r
    optimal_small, _, _ = exact_partition_dp(sdims,idims,p,h,D)
    formula_small = min(D+(p-1)*msmall,t*D)
    assert optimal_small == formula_small
    return {'type':'spread','p':p,'n':n,'field_degree':d,'rank':r,'h':h,'D':D,
            'blocks':n,'pairs_checked':len(ia),'quotient_rank_checks':quotient_checks,
            'T_full':t,'best_certified_degree_formula':min(D+(p-1)*n,t*D),
            'singletons_budget':D+(p-1)*n,'one_batch_budget':t*D,
            'small_partition_dp_size':msmall,'small_partition_dp_optimum':optimal_small,
            'base_target_n_over_2':n//2,'elapsed_worker_s':time.perf_counter()-start}

def main():
    start = time.perf_counter()
    spread = [
        (2,3,[1,1,0,1],1), (2,4,[1,1,0,0,1],2),
        (2,5,[1,0,1,0,0,1],3), (2,8,[1,1,0,1,1,0,0,0,1],8),
        (3,2,[1,0,1],1), (5,2,[2,0,1],2), (7,2,[1,0,1],3),
    ]
    random_cases = [(p,1000*p+i) for p in [2,3,5] for i in range(3)]
    with ProcessPoolExecutor(max_workers=4) as pool:
        f1 = [pool.submit(check_spread_case,s) for s in spread]
        f2 = [pool.submit(check_random_case,s) for s in random_cases]
        results = [f.result() for f in f1+f2]
    report = {
        'scope':'Exact subspace/decomposition checks; not an ENS refutation or PHP lower-bound computation.',
        'workers_max':4,'cases':len(results),'all_passed':True,
        'pairs_checked':sum(r.get('pairs_checked',0) for r in results),
        'ordering_permutations_checked':sum(r.get('permutations_checked',0) for r in results),
        'quotient_rank_checks':sum(r.get('quotient_rank_checks',0) for r in results),
        'wall_s':time.perf_counter()-start,'results':results,
    }
    (ROOT/'results.json').write_text(json.dumps(report,indent=2))
    print(json.dumps({k:v for k,v in report.items() if k!='results'},indent=2))
    print('n=256:',json.dumps(results[3],indent=2))

if __name__ == '__main__':
    main()
