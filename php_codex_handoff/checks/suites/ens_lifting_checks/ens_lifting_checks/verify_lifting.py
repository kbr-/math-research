"""Exact finite-field checks for the simultaneous one-level ENS repair lemma.

Run: OPENBLAS_NUM_THREADS=1 python verify_lifting.py
NumPy vectorization over the Boolean cube; process-parallel independent cases.
No floating-point rank or probability computations.
"""
from __future__ import annotations
import json
import os
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path
from typing import Any
import numpy as np


def cube(n: int) -> tuple[np.ndarray, np.ndarray]:
    states = np.arange(1 << n, dtype=np.int64)
    counts = np.fromiter((int(s).bit_count() for s in states), dtype=np.int64)
    return states, counts


def moments(weights: np.ndarray, p: int) -> np.ndarray:
    """All squarefree monomial moments via a vectorized superset zeta transform."""
    out = weights.copy() % p
    step = 1
    while step < out.size:
        blocks = out.reshape(-1, 2, step)
        blocks[:, 0, :] = (blocks[:, 0, :] + blocks[:, 1, :]) % p
        step *= 2
    return out


def evaluate(states: np.ndarray, terms: dict[int, int], p: int) -> np.ndarray:
    masks = np.array(list(terms), dtype=np.int64)
    coeffs = np.array([terms[int(m)] for m in masks], dtype=np.int64)
    return (((states[:, None] & masks[None, :]) == masks[None, :]) @ coeffs) % p


def coefficient_measure(states: np.ndarray, mask: int, p: int) -> np.ndarray:
    """Weights representing coefficient-of-x^mask in the multilinear normal form."""
    result = np.zeros(states.size, dtype=np.int64)
    subset = states[(states & mask) == states]
    size = mask.bit_count()
    result[subset] = np.array([(-1) ** (size - int(s).bit_count()) for s in subset], dtype=np.int64) % p
    return result


def polynomial_degree(terms: dict[int, int]) -> int:
    return max(mask.bit_count() for mask, coefficient in terms.items() if coefficient)


def solve_case(spec: dict[str, Any]) -> dict[str, Any]:
    p, n, target = spec['p'], spec['n'], spec['D']
    rng = np.random.default_rng(spec['seed'])
    states, degrees = cube(n)
    blocks: list[dict[str, Any]] = []
    if spec['kind'] == 'random':
        # Base axiom x_0=0; this set of checks uses a signed measure supported there.
        mu = rng.integers(0, p, states.size, dtype=np.int64)
        mu[(states & 1) != 0] = 0
        mu[0] = (mu[0] + 1 - int(mu.sum() % p)) % p
        available = states[degrees <= spec['delta']]
        for _ in range(spec['blocks']):
            polys = []
            for __ in range(spec['fanin']):
                chosen = rng.choice(available, size=min(7, available.size), replace=False)
                terms = {int(m): int(rng.integers(1, p)) for m in chosen}
                polys.append(terms)
            blocks.append({'polys': polys, 'h': spec['h']})
    elif spec['kind'] == 'hidden_high_order':
        # mu(x_0 q)=0 through B, but mu is NOT pointwise supported on x_0=0.
        mu = np.zeros(states.size, dtype=np.int64)
        mu[0] = 1
        mu = (mu + coefficient_measure(states, 2, p)
                + coefficient_measure(states, (1 << n) - 1, p)) % p
        blocks = [{'polys': [{2: 1}], 'h': 1}]
    elif spec['kind'] == 'higher_moment_witness':
        mu = np.zeros(states.size, dtype=np.int64)
        mu[0] = 1
        mask = sum(1 << i for i in range(1, spec['order'] + 1))
        mu = (mu + coefficient_measure(states, mask, p)) % p
        blocks = [{'polys': [{2: 1}], 'h': 1}]
    elif spec['kind'] == 'zero_branch_nonvacuous':
        mu = np.zeros(states.size, dtype=np.int64)
        mu[0] = 1
        mask = sum(1 << i for i in range(1, spec['order'] + 1))
        mu = (mu + coefficient_measure(states, mask, p)) % p
        blocks = [{'polys': [{2: 1}], 'h': 1}]
    elif spec['kind'] == 'revisit':
        # Initially the x_1 and x_2 blocks have zero moments. Repairing 1+x_1+x_2
        # makes an earlier zero block nonzero, requiring a rescan.
        mu = np.zeros(states.size, dtype=np.int64)
        mu[0] = 1
        mu = (mu + coefficient_measure(states, 6, p)) % p
        blocks = [{'polys': [{2: 1}], 'h': 1},
                  {'polys': [{4: 1}], 'h': 1},
                  {'polys': [{0: 1, 2: 1, 4: 1}], 'h': 1}]
    else:
        raise ValueError(spec['kind'])

    for b in blocks:
        b['delta'] = [polynomial_degree(poly) for poly in b['polys']]
        maximum = max(b['delta'])
        b['e'] = [d + b['h'] * (maximum + 1) for d in b['delta']]
        b['c'] = max([0] + [target - e + (p-1)*d
                           for d, e in zip(b['delta'], b['e']) if e <= target])
        b['G'] = np.stack([evaluate(states, poly, p) for poly in b['polys']])
        b['beta'] = np.zeros((b['h'], len(b['polys'])), dtype=np.int64)
        b['locked'] = False
    base_degree = target + sum(b['c'] for b in blocks)
    x0 = states & 1
    input_base = moments((mu * x0) % p, p)
    assert np.all(input_base[degrees <= base_degree-1] == 0), 'Input not a design for x_0'
    assert int(mu.sum() % p) == 1

    W = np.ones(states.size, dtype=np.int64)
    trace = []
    while True:
        changed = False
        for a, b in enumerate(blocks):
            if b['locked']:
                continue
            for i, e in enumerate(b['e']):
                if e > target:
                    continue
                mom = moments((mu * W % p) * b['G'][i] % p, p)
                good = np.flatnonzero((degrees <= target-e) & (mom != 0))
                if not good.size:
                    continue
                qmask = int(min(good, key=lambda m: (degrees[m], m)))
                qvalues = ((states & qmask) == qmask).astype(np.int64)
                alpha = None
                for value in range(1, p):
                    candidate = qvalues * (b['G'][i] == value)
                    normalizer = int(((mu * W % p) * candidate).sum() % p)
                    if normalizer:
                        alpha, local_weight = value, candidate
                        break
                assert alpha is not None, 'Interpolation failed to provide a branch'
                W = (W * local_weight) % p
                assert int((mu * W).sum() % p) != 0
                b['beta'][0, i] = pow(alpha, -1, p)
                b['locked'] = True
                cost = int(degrees[qmask]) + (p-1)*b['delta'][i]
                assert cost <= b['c']
                trace.append({'block': a, 'companion': i, 'value': alpha,
                              'q_degree': int(degrees[qmask]), 'degree_cost_bound': cost})
                changed = True
                break
            if changed:
                break  # Rescan uncommitted blocks after every reweighting.
        if not changed:
            break
    assert len(trace) <= len(blocks)
    assert sum(t['degree_cost_bound'] for t in trace) <= base_degree-target
    Z = int((mu * W).sum() % p)
    lifted = ((mu * W) % p) * pow(Z, -1, p) % p
    assert int(lifted.sum() % p) == 1
    assert np.all(moments(lifted*x0 % p, p)[degrees <= target-1] == 0)

    n_tests, active_axioms, naive_failures = 0, 0, 0
    for b in blocks:
        assert np.all((np.power(b['beta'], p) - b['beta']) % p == 0)
        factors = (1 - b['beta'] @ b['G']) % p
        product = np.prod(factors, axis=0, dtype=np.int64) % p
        for i, e in enumerate(b['e']):
            E_values = (b['G'][i] * product) % p
            if b['locked']:
                assert np.all((W * E_values) % p == 0), 'A lock is not exact'
            if e > target:
                continue
            active_axioms += 1
            tested = degrees <= target-e
            n_tests += int(tested.sum())
            assert np.all(moments(lifted*E_values % p, p)[tested] == 0)
            naive_failures += int(np.count_nonzero(moments(mu*E_values % p, p)[tested]))
    assert active_axioms > 0, 'Vacuous check'
    if spec['kind'] == 'higher_moment_witness':
        assert trace and trace[0]['q_degree'] == spec['order'] - 1
    if spec['kind'] == 'zero_branch_nonvacuous':
        assert not trace
        higher = (degrees > target-blocks[0]['e'][0]) & (degrees <= target-blocks[0]['delta'][0])
        assert np.any(moments(mu * blocks[0]['G'][0] % p, p)[higher] != 0)
    if spec['kind'] == 'revisit':
        assert trace[0]['block'] == 2 and any(t['block'] == 0 for t in trace[1:])
    if spec['kind'] == 'hidden_high_order':
        assert np.any(mu[(states & 1) != 0] != 0), 'Did not exercise cancellation'
    return {'spec': spec, 'base_degree_bound': base_degree,
            'active_extension_axioms': active_axioms,
            'all_squarefree_multiplier_tests': n_tests,
            'repair_trace': trace,
            'naive_unreweighted_violations': naive_failures, 'passed': True}


def main() -> None:
    jobs: list[dict[str, Any]] = []
    for p in (2, 3, 5):
        for seed in range(12):
            delta = 1 + seed % 2
            h = 1 + seed % 3
            D = delta + h*(delta+1) + 2
            jobs.append({'kind': 'random', 'p': p, 'n': 8, 'D': D,
                         'seed': 1000*p+seed, 'delta': delta, 'h': h,
                         'blocks': 4, 'fanin': 5})
        jobs.append({'kind': 'hidden_high_order', 'p': p, 'n': 12, 'D': 4, 'seed': p})
        jobs.append({'kind': 'higher_moment_witness', 'p': p, 'n': 8,
                     'D': 6, 'order': 4, 'seed': p})
        jobs.append({'kind': 'zero_branch_nonvacuous', 'p': p, 'n': 8,
                     'D': 4, 'order': 3, 'seed': p})
    jobs.append({'kind': 'revisit', 'p': 2, 'n': 5, 'D': 3, 'seed': 999})
    with ProcessPoolExecutor(max_workers=min(6, os.cpu_count() or 1)) as pool:
        results = list(pool.map(solve_case, jobs))
    summary = {'cases': len(results), 'passed': sum(r['passed'] for r in results),
               'active_extension_axioms': sum(r['active_extension_axioms'] for r in results),
               'multiplier_tests': sum(r['all_squarefree_multiplier_tests'] for r in results),
               'naive_unreweighted_violations': sum(r['naive_unreweighted_violations'] for r in results)}
    destination = Path(__file__).with_name('results.json')
    destination.write_text(json.dumps({'summary': summary, 'results': results}, indent=2))
    print(json.dumps(summary, indent=2))


if __name__ == '__main__':
    main()
