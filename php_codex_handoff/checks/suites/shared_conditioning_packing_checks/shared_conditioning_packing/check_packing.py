#!/usr/bin/env python3
"""Exact, vectorized checks of shared-conditioning ENS packing.

These are finite-domain identity tests, NOT computations of PHP designs.
The old functional is a signed F_p combination of evaluations satisfying
column exclusion, Boolean equations, and one row-sum equation. This permits
independent checks of normalization and preservation of an old non-field axiom.
Each test uses several levels and reuses a single conditioning weight.
"""
import os
for name in ('OPENBLAS_NUM_THREADS', 'OMP_NUM_THREADS', 'MKL_NUM_THREADS'):
    os.environ[name] = '1'
import json
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path
import numpy as np


def one_case(args):
    seed, p, mode = args
    rng = np.random.default_rng(seed)
    rows, cols = 3, 5
    # A column is empty (0) or occupied by one of `rows` possible rows.
    states = np.indices((rows + 1,) * cols, dtype=np.int64).reshape(cols, -1).T
    count = len(states)
    x = (states[:, :, None] == np.arange(1, rows + 1)[None, None, :]).astype(np.int64)
    xflat = x.reshape(count, cols * rows)
    # One actual row equation is also imposed on this satisfiable test domain.
    valid = (x[:, :, 0].sum(axis=1) % p == 1)
    weights = rng.integers(0, p, size=count, dtype=np.int64) * valid
    v = np.flatnonzero(valid)[0]
    weights[v] = (weights[v] + 1 - int(weights.sum() % p)) % p
    assert weights.sum() % p == 1

    if mode == 'columns':
        selected = rng.choice(cols, size=3, replace=False)
        f = x[:, selected, :].reshape(count, -1)
        feature_degrees = [1] * f.shape[1]
        query_features = [states[:, j] for j in selected]
        query_value_sets = [range(rows + 1)] * len(selected)
        weight_degree = len(selected)
    else:
        number = 4
        coefficients = rng.integers(0, p, size=(cols * rows, number), dtype=np.int64)
        f = (xflat @ coefficients) % p
        # Two nonlinear common features, of total degree at most two.
        f[:, 2] = (f[:, 2] * f[:, 0]) % p
        f[:, 3] = (f[:, 3] * f[:, 1]) % p
        feature_degrees = [1, 1, 2, 2]
        query_features = [f[:, j] for j in range(number)]
        query_value_sets = [range(p)] * number
        weight_degree = (p - 1) * sum(feature_degrees)

    # Greedy branch selection: never enumerate all combinations of feature values.
    W = np.ones(count, dtype=np.int64)
    oracle_queries = 0
    for values, allowed in zip(query_features, query_value_sets):
        found = False
        for alpha in rng.permutation(list(allowed)):
            candidate = W * (values == alpha)
            mass = int(np.sum(weights * candidate) % p)
            oracle_queries += 1
            if mass:
                W = candidate.astype(np.int64)
                found = True
                break
        assert found
    denominator = int(np.sum(weights * W) % p)
    assert denominator != 0
    lifted_weights = (weights * W * pow(denominator, -1, p)) % p
    assert lifted_weights.sum() % p == 1
    # Reweighting preserves the actual old row equation at every moment.
    row_axiom = (x[:, :, 0].sum(axis=1) - 1) % p
    assert np.all((lifted_weights * row_axiom) % p == 0)
    cell = np.flatnonzero(W)[0]
    assert np.all(f[W.astype(bool)] == f[cell])

    # A dense polynomial basis in the common features, including quadratic terms.
    q1, q2 = np.triu_indices(f.shape[1])
    basis = np.column_stack((np.ones(count, dtype=np.int64), f, (f[:, q1] * f[:, q2]) % p))
    delta_bound = 2 * max(feature_degrees)
    accuracy = 1 + seed % 2
    extension_degree_bound = delta_bound + accuracy * (delta_bound + 1)
    target_degree = extension_degree_bound + 2
    base_degree = target_degree + weight_degree

    beta_all = []
    companions = point_checks = multiplier_checks = blocks = 0
    levels = 4
    for level in range(levels):
        old_beta = np.array(beta_all, dtype=np.int64)
        new_beta = []
        for block in range(8):
            width = 8 + (seed + block) % 9
            coefficients = rng.integers(0, p, size=(basis.shape[1], width), dtype=np.int64)
            g = (basis @ coefficients) % p
            # Explicit dependence on extension variables from prior levels:
            # terms r, and r*f_j. Substitution uses the already selected scalars.
            if old_beta.size:
                selected_r = rng.choice(old_beta.size, size=min(8, old_beta.size), replace=False)
                coeff_r = rng.integers(0, p, size=(selected_r.size, width), dtype=np.int64)
                r_part = (old_beta[selected_r] @ coeff_r) % p
                g = (g + r_part[None, :] * (1 + f[:, [block % f.shape[1]]])) % p
            # Exercise the all-zero-on-cell case as well as the nonzero-witness case.
            if block % 4 == 0:
                g = (g - g[cell][None, :]) % p
            b = g[cell].copy()
            assert np.all(g[W.astype(bool)] == b)
            beta = np.zeros((accuracy, width), dtype=np.int64)
            nz = np.flatnonzero(b)
            if nz.size:
                i = int(nz[0])
                beta[0, i] = pow(int(b[i]), -1, p)
            factors = (1 - g @ beta.T) % p
            product = np.prod(factors, axis=1, dtype=np.int64) % p
            E = (g * product[:, None]) % p
            assert np.all((W[:, None] * E) % p == 0)
            # Original extension degree is bounded by extension_degree_bound.
            # Degree-<=2 multipliers are consequently active at target_degree.
            picks = rng.integers(0, cols * rows, size=(24, 2))
            multipliers = np.column_stack((
                np.ones(count, dtype=np.int64),
                xflat[:, picks[:, 0]],
                (xflat[:, picks[:, 0]] * xflat[:, picks[:, 1]]) % p,
            ))
            moments = (multipliers.T @ ((lifted_weights[:, None] * E) % p)) % p
            assert not np.any(moments)
            assert np.all((np.power(beta, p) - beta) % p == 0)
            new_beta.extend(beta.ravel().tolist())
            blocks += 1
            companions += width
            point_checks += count * width
            multiplier_checks += multipliers.shape[1] * width
        beta_all.extend(new_beta)

    return dict(seed=seed, p=p, mode=mode, states=count, levels=levels,
                blocks=blocks, companions=companions,
                weighted_companion_point_checks=point_checks,
                multiplier_moment_checks=multiplier_checks,
                oracle_queries=oracle_queries, weight_degree_bound=weight_degree,
                target_degree=target_degree, sufficient_base_degree=base_degree,
                passed=True)


def main():
    cases = [(9000 + 100 * p + 10 * j + k, p, mode)
             for p in (2, 3, 5, 7)
             for j, mode in enumerate(('features', 'columns'))
             for k in range(6)]
    with ProcessPoolExecutor(max_workers=min(6, os.cpu_count() or 1)) as pool:
        results = list(pool.map(one_case, cases))
    summary = dict(cases=len(results), primes=[2, 3, 5, 7], all_passed=all(r['passed'] for r in results),
                   total_blocks=sum(r['blocks'] for r in results),
                   total_companions=sum(r['companions'] for r in results),
                   weighted_companion_point_checks=sum(r['weighted_companion_point_checks'] for r in results),
                   multiplier_moment_checks=sum(r['multiplier_moment_checks'] for r in results),
                   max_levels=max(r['levels'] for r in results),
                   note='Finite-domain algebraic identity checks, not PHP design computations or a lower-bound verification.')
    output = Path(__file__).resolve().parent / 'results.json'
    output.write_text(json.dumps(dict(summary=summary, cases=results), indent=2))
    print(json.dumps(summary, indent=2))

if __name__ == '__main__':
    main()
