"""Exact, vectorized finite-field checks of factor-packed ENS substitutions.
Run: python checks.py --workers 6
No floating point arithmetic is used. Independent cases run in processes.
"""
import os
for name in ("OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "OMP_NUM_THREADS"):
    os.environ[name] = "1"
import argparse
import itertools
import json
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path
import numpy as np


def inverse_mod(A, p):
    A = np.asarray(A, dtype=np.int64)
    n = A.shape[0]
    W = np.concatenate((A.copy(), np.eye(n, dtype=np.int64)), axis=1) % p
    for j in range(n):
        nz = np.flatnonzero(W[j:, j])
        if not len(nz):
            raise ValueError("singular matrix")
        k = j + int(nz[0])
        W[[j, k]] = W[[k, j]]
        W[j] = W[j] * pow(int(W[j,j]), -1, p) % p
        factors = W[:, j].copy()
        factors[j] = 0
        W = (W - factors[:,None] * W[j][None,:]) % p
    return W[:,n:]


def reduced_degrees(values, p, domain, n):
    """Tensor-product exact interpolation on F_p^n or {0,1}^n."""
    b = len(domain)
    V = np.asarray([[pow(int(a), j, p) for j in range(b)] for a in domain],
                   dtype=np.int64)
    inv = inverse_mod(V, p)
    Z = values.reshape((-1,) + (b,) * n).copy()
    for axis in range(1, n+1):
        T = np.moveaxis(Z, axis, 0)
        shape = T.shape
        T = ((inv @ T.reshape(b, -1)) % p).reshape(shape)
        Z = np.moveaxis(T, 0, axis)
    C = Z.reshape(values.shape[0], -1)
    degrees = np.indices((b,)*n, dtype=np.int64).sum(axis=0).ravel()
    return np.where(C != 0, degrees[None,:], -1).max(axis=1)


def packed_beta(F, p, h, values):
    """F has one row per basis polynomial, one column per old assignment."""
    rank, count = F.shape
    events = [(j,a) for j in range(rank) for a in values]
    # Balanced ordered buckets, including empty buckets if h > len(events).
    buckets = np.array_split(np.arange(len(events)), h)
    beta = np.zeros((h, rank, count), dtype=np.int64)
    prefixes = np.ones((h, count), dtype=np.int64)
    for u, bucket in enumerate(buckets):
        prefix = np.ones(count, dtype=np.int64)
        for ix in bucket:
            j,a = events[int(ix)]
            inverse = pow(int(a), -1, p)
            beta[u,j] = (beta[u,j] + inverse * prefix) % p
            prefix = prefix * (1 - inverse * F[j]) % p
        prefixes[u] = prefix
    rowfactors = (1 - np.einsum("urk,rk->uk", beta, F, optimize=True)) % p
    if not np.array_equal(rowfactors, prefixes):
        raise AssertionError("telescoping row identity failed")
    product = np.ones(count, dtype=np.int64)
    for row in rowfactors:
        product = product * row % p
    target = np.all(F == 0, axis=0).astype(np.int64)
    if not np.array_equal(product, target):
        raise AssertionError("zero-indicator identity failed")
    return beta, product, len(events)


def run_case(spec):
    seed, p, n, rank_requested, fanin_extra, h, boolean_basis, linear_control = spec
    rng = np.random.default_rng(seed)
    domain = [0,1] if boolean_basis else list(range(p))
    b = len(domain)
    points = np.indices((b,)*n, dtype=np.int64).reshape(n,-1)
    points = np.asarray(domain, dtype=np.int64)[points]
    if linear_control:
        F = points.copy()
        rank = n
        delta = 1
    else:
        exponent_cap = 1 if boolean_basis else p-1
        exponents = np.asarray([e for e in itertools.product(range(exponent_cap+1), repeat=n)
                                if 1 <= sum(e) <= 3], dtype=np.int64)
        rng.shuffle(exponents)
        rank = min(rank_requested, len(exponents))
        exponents = exponents[:rank]
        M = np.ones((rank, points.shape[1]), dtype=np.int64)
        for axis in range(n):
            M = M * (points[axis][None,:] ** exponents[:,axis,None]) % p
        delta = int(exponents.sum(axis=1).max())
        if boolean_basis:
            F = M
        else:
            U = np.tril(rng.integers(0,p,size=(rank,rank), dtype=np.int64), -1)
            U += np.eye(rank, dtype=np.int64)
            F = (U @ M + rng.integers(0,p,size=(rank,1), dtype=np.int64)) % p
    # The first rank companions ARE the independent basis. Extra companions
    # are arbitrary linear combinations, testing effective-rank compression.
    A = np.concatenate((np.eye(rank, dtype=np.int64),
                        rng.integers(0,p,size=(fanin_extra,rank), dtype=np.int64)), axis=0)
    G = A @ F % p
    allowed_values = [1] if boolean_basis else list(range(1,p))
    beta, product, events = packed_beta(F,p,h,allowed_values)
    if np.any(G * product[None,:] % p):
        raise AssertionError("an extension companion does not vanish")
    flat = beta.reshape(h*rank,-1)
    degrees = reduced_degrees(flat,p,domain,n)
    Q = (events+h-1)//h
    L = delta * max(0,Q-1)
    if degrees.max(initial=-1) > L:
        raise AssertionError("degree bound failed")
    # Sharpness check for independent F_p-valued inputs (or Boolean inputs).
    if linear_control and int(degrees.max(initial=-1)) != max(0,Q-1):
        raise AssertionError("sharp-control degree mismatch")
    # Arbitrary F_p signed functional: not generally an evaluation homomorphism.
    weights = rng.integers(0,p,size=points.shape[1],dtype=np.int64)
    weights[0] = (weights[0] + 1 - int(weights.sum())) % p
    if int(weights.sum()) % p != 1:
        raise AssertionError("normalization failed")
    tests = 24
    # Simultaneous arbitrary monomial multipliers in OLD and NEW variables.
    allvalues = np.concatenate((points,flat),axis=0)
    monomials = np.ones((tests,points.shape[1]),dtype=np.int64)
    for _ in range(5):
        choice = rng.integers(0,allvalues.shape[0],size=tests)
        monomials = monomials * allvalues[choice] % p
    companions = G * product[None,:] % p
    selected = companions[rng.integers(0,G.shape[0],size=tests)]
    moments = np.einsum("tk,tk,k->t",monomials,selected,weights,optimize=True) % p
    if np.any(moments):
        raise AssertionError("annihilating-functional check failed")
    return dict(seed=seed,p=p,n=n,assignments=points.shape[1],rank=rank,
                fanin=G.shape[0],h=h,boolean_basis=boolean_basis,
                independent_input_control=linear_control,events=events,
                polynomial_degree_bound=L,
                actual_max_reduced_beta_degree=int(degrees.max(initial=-1)),
                degree_inflation=max(1,L),companion_point_checks=int(G.size),
                multiplier_moments=tests,passed=True)


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--workers',type=int,default=6)
    args=parser.parse_args()
    specs=[]
    seed=500
    for p in (2,3,5,7):
        for boolean in (False,True):
            for h in (1,2,4,8,16):
                seed+=1
                specs.append((seed,p,3 if p==7 else 4,7,11,h,boolean,False))
    for p in (2,3,5):
        for n in (2,3,4):
            for h in (1,2,3,(p-1)*n+1):
                seed+=1
                specs.append((seed,p,n,n,3,h,False,True))
    with ProcessPoolExecutor(max_workers=args.workers) as pool:
        rows=list(pool.map(run_case,specs))
    summary=dict(cases=len(rows),all_passed=all(r['passed'] for r in rows),
                 assignment_instances=sum(r['assignments'] for r in rows),
                 companion_point_checks=sum(r['companion_point_checks'] for r in rows),
                 multiplier_moments=sum(r['multiplier_moments'] for r in rows),
                 sharp_independent_input_controls=sum(r['independent_input_control'] for r in rows),
                 workers=args.workers,arithmetic='exact int64 modulo p')
    output=Path(__file__).resolve().parent/'results.json'
    output.write_text(json.dumps(dict(summary=summary,cases=rows),indent=2))
    print(json.dumps(summary,indent=2))

if __name__=='__main__':
    main()
