"""Exact checks for base-aware, degree-preserving ENS substitutions.

All matrix operations are integer NumPy arithmetic followed by reduction mod p.
Independent instances are process-parallel. Tests use satisfiable finite domains;
they do not constitute an ENS/PHP lower bound. The symbolic degree arguments are
separate from these evaluation checks.
"""
from __future__ import annotations
import json, os
from concurrent.futures import ProcessPoolExecutor
from itertools import product
from pathlib import Path
import numpy as np


def case(spec: tuple[int, int, int, int, int]) -> dict:
    p, m, n, levels, seed = spec
    rng = np.random.default_rng(seed)
    states = np.array(list(product(range(m+1), repeat=n)), dtype=np.int64)
    X = (states[:, None, :] == np.arange(1, m+1)[None, :, None]).astype(np.int64)
    X = X.reshape(len(states), m*n)
    Z = np.concatenate((np.ones((len(X), 1), dtype=np.int64), X), axis=1)
    row_sums = X.reshape(-1,m,n).sum(axis=2) % p
    sat = np.all(row_sums == 1, axis=1)
    assert sat.any()
    nonfunctional = sat & (np.max(X.reshape(-1,m,n).sum(axis=2), axis=1) > 1)
    # Every introduced variable will have an explicit affine form in original x.
    prior_forms: list[np.ndarray] = []
    counts = dict(blocks=0, companion_assignment_checks=0,
                  field_assignment_checks=0, mixed_multiplier_moments=0)
    weights = rng.integers(0,p,size=int(sat.sum()),dtype=np.int64)
    if weights.sum() % p == 0:
        weights[0] = (weights[0]+1) % p
    weights = weights * pow(int(weights.sum()%p),-1,p) % p
    assert int(weights.sum()%p) == 1
    for level in range(levels):
        # An entire level refers only to previous levels, not its siblings.
        level_forms: list[np.ndarray] = []
        for b in range(8):
            kind = 'row' if b%2 == 0 else 'column'
            if kind == 'row':
                i = int(rng.integers(m)); ids = np.arange(i*n,(i+1)*n)
            else:
                j = int(rng.integers(n)); ids = np.arange(m)*n+j
            U = X[:,ids]; k = len(ids)
            cut = max(1,k//2)
            # A has support I x J for disjoint I,J, so A^2=0 formally.
            # Each entry is affine in original variables and previous r's.
            mats = np.zeros((k,k,m*n+1), dtype=np.int64)
            for i in range(cut):
                for j in range(cut,k):
                    f = rng.integers(0,p,size=m*n+1,dtype=np.int64)
                    if prior_forms:
                        picks = rng.integers(len(prior_forms),size=min(5,len(prior_forms)))
                        cs = rng.integers(0,p,size=len(picks),dtype=np.int64)
                        f = (f + cs @ np.stack([prior_forms[int(t)] for t in picks])) % p
                    mats[i,j] = f % p
            A = np.einsum('xa,ija->xij',Z,mats,optimize=True) % p
            assert not np.any(np.einsum('xij,xjk->xik',A,A,optimize=True) % p)
            G = (U + np.einsum('xij,xj->xi',A,U,optimize=True)) % p
            qforms = -mats.sum(axis=0) % p
            qforms[:,0] = (qforms[:,0]+1) % p
            Q = Z @ qforms.T % p
            assert np.array_equal((Q*G).sum(axis=1)%p, U.sum(axis=1)%p)
            # Set r_1j=q_j, and all later-factor coefficients to zero.
            first = (1-(Q*G).sum(axis=1)) % p
            EE = G * first[:,None] % p
            rhs = G * ((1-U.sum(axis=1))%p)[:,None] % p
            assert np.array_equal(EE,rhs)
            if kind == 'column':
                assert not np.any(EE)
            assert not np.any(EE[sat])
            counts['companion_assignment_checks'] += int(EE.size)
            assert not np.any((np.power(Q,p)-Q)%p)
            counts['field_assignment_checks'] += int(Q.size)
            for _ in range(4):
                # Mixed old/new multiplier, rather than just constant tests.
                a = int(rng.integers(m*n)); j = int(rng.integers(k))
                mult = X[sat,a]*Q[sat,j] % p
                if prior_forms:
                    pf = prior_forms[int(rng.integers(len(prior_forms)))]
                    mult = mult*(Z[sat]@pf%p) % p
                assert not np.any((weights*mult)@EE[sat] % p)
                counts['mixed_multiplier_moments'] += k
            level_forms.extend(qforms)
            counts['blocks'] += 1
        prior_forms.extend(level_forms)
    return dict(p=p,m=m,n=n,levels=levels,seed=seed,assignments=len(X),
                base_solutions=int(sat.sum()),
                nonfunctional_base_solutions=int(nonfunctional.sum()),
                **counts,passed=True)


def main() -> None:
    specs = [(p,2,n,4,3000+100*p+10*n+s)
             for p in (2,3,5) for n in (5,7) for s in range(3)]
    workers=min(6,os.cpu_count() or 1)
    with ProcessPoolExecutor(max_workers=workers) as pool:
        results=list(pool.map(case,specs))
    summary={
        'instances':len(results),'workers':workers,
        'all_passed':all(t['passed'] for t in results),
        'blocks':sum(t['blocks'] for t in results),
        'companion_assignment_checks':sum(t['companion_assignment_checks'] for t in results),
        'field_assignment_checks':sum(t['field_assignment_checks'] for t in results),
        'mixed_multiplier_moments':sum(t['mixed_multiplier_moments'] for t in results),
        'instances_with_nonfunctional_solutions':sum(t['nonfunctional_base_solutions']>0 for t in results),
        'scope':'Finite-domain tests, not a PHP design or lower-bound computation.'}
    out=Path(__file__).parent
    (out/'results.json').write_text(json.dumps({'summary':summary,'instances':results},indent=2))
    print(json.dumps(summary,indent=2))

if __name__=='__main__': main()
