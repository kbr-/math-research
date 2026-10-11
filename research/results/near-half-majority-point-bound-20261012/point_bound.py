#!/usr/bin/env python3
"""The relaxation bound at a point for systems of majority rows, on sampled scopes.

Statement tested.  Rows a have scopes V_a of odd width w = 2k + 1 among n variables and labels b_a in {0, 1}:
MAJ(x on V_a) = b_a, written as literal clauses.  At a point sigma put P_a = {i in V_a : sigma_i = 1 - b_a}; the
row is violated at sigma exactly when |P_a| >= k + 1, and then every monomial, in the literals that are one at
sigma, on k + 1 indices of P_a is a consequence of the row.  So with

    rho(sigma) = max |S| over sets S of variables with |S meet P_a| <= k for every row violated at sigma,

the system, if unsatisfiable, is refuted in degree max{rho(sigma) + 1, w} (the entry's lemma).  This script
computes, for sampled systems, two numbers that bracket rho(sigma): the linear programme
max sum mu_i, mu(P_a) <= k, 0 <= mu <= 1, an upper bound, and the size of a feasible set found greedily from
the programme's solution, a lower bound.

Inputs meeting the hypotheses.  (1) Control: n = w t variables, the rows of value 0 are the blocks of two
partitions into w-sets (the second a random permutation of the first), sigma all ones.  Every variable lies in
exactly two violated rows, so by the lemma on fractional covers the programme's value is at most k n / w, and
the set taking k variables of each block of the first partition, if it also meets every block of the second in
at most k... is not guaranteed; so the control asserts only the programme's value: LP = k n / w exactly, by the
uniform solution mu = k / w and the dual lambda = 1/2 on every row.  (2) The candidate of the portfolio: n + 1
rows with independent uniform scopes of size w = 19 and independent uniform labels.

Expectations, written before the run.
  Control: LP / n equals k / w = 9/19 to solver accuracy (asserted); the greedy set is at most that.
  Candidate at sigma all ones and all zeros: unknown to me; a reviewer's rough estimate, not computed, is an LP
    value about 0.52 n.  A value below 0.5 would be a ceiling below a half for the sampled system; a greedy
    value above 0.5 shows the bound at that point is above a half.
  Candidate at random points of bias 0.9, 0.75 and 0.5: I expect larger values than at the two constant points,
    violated rows having fewer violating positions there.
  Candidate at the point that sets each variable to the value violating more of its rows' labels: no
    expectation.

Usage: point_bound.py OUT.json [N [SEEDS]]
"""
import json
import sys

import numpy as np
from scipy.optimize import linprog
from scipy.sparse import csr_matrix


def bracket(scopes, labels, sigma, k):
    """(violated rows, LP value, greedy feasible size) at the point sigma."""
    n = sigma.size
    violating = sigma[scopes] != labels[:, None]              # row a, position j: scope variable is in P_a
    violated = violating.sum(axis=1) >= k + 1
    rows = np.nonzero(violated)[0]
    if rows.size == 0:
        return 0, float(n), n
    mask = violating[rows]
    row_index = np.repeat(np.arange(rows.size), mask.sum(axis=1))
    col_index = scopes[rows][mask]
    matrix = csr_matrix((np.ones(col_index.size), (row_index, col_index)), shape=(rows.size, n))
    solved = linprog(-np.ones(n), A_ub=matrix, b_ub=np.full(rows.size, float(k)), bounds=(0, 1), method='highs')
    assert solved.status == 0, solved.message
    # Greedy: take variables in decreasing order of their LP weight while every violated row keeps at most k.
    used = np.zeros(rows.size)
    columns = matrix.tocsc()
    chosen = 0
    for variable in np.argsort(-solved.x, kind='stable'):
        hit = columns.indices[columns.indptr[variable]:columns.indptr[variable + 1]]
        if np.all(used[hit] < k):
            used[hit] += 1
            chosen += 1
    return int(rows.size), float(-solved.fun), int(chosen)


def control(w, t, rng):
    n, k = w * t, (w - 1) // 2
    first = np.arange(n).reshape(t, w)
    second = rng.permutation(n).reshape(t, w)
    scopes = np.vstack([first, second])
    labels = np.zeros(2 * t, dtype=np.int64)
    violated, value, greedy = bracket(scopes, labels, np.ones(n, dtype=np.int64), k)
    assert violated == 2 * t
    assert abs(value - k * n / w) < 1e-6 * n, (value, k * n / w)       # the tolerance beside the quantity: n k / w
    assert greedy <= value + 1e-6
    return {'n': n, 'w': w, 'rows': 2 * t, 'lp_over_n': value / n, 'k_over_w': k / w, 'greedy_over_n': greedy / n}


def candidate(n, w, seed):
    rng = np.random.default_rng(seed)
    k = (w - 1) // 2
    scopes = np.argsort(rng.random((n + 1, n)), axis=1)[:, :w]          # n + 1 uniform w-subsets
    labels = rng.integers(0, 2, n + 1)
    zero_rows = np.bincount(scopes[labels == 0].ravel(), minlength=n)
    one_rows = np.bincount(scopes[labels == 1].ravel(), minlength=n)
    points = {'all ones': np.ones(n, dtype=np.int64), 'all zeros': np.zeros(n, dtype=np.int64),
              'by rows': (zero_rows >= one_rows).astype(np.int64)}
    for bias in (0.9, 0.75, 0.5):
        points[f'bias {bias}'] = (rng.random(n) < bias).astype(np.int64)
    out = {'n': n, 'w': w, 'seed': seed, 'rows': n + 1, 'least_zero_row_degree': int(zero_rows.min()),
           'variables_in_no_zero_row': int((zero_rows == 0).sum()), 'points': {}}
    for name, sigma in points.items():
        violated, value, greedy = bracket(scopes, labels, sigma, k)
        out['points'][name] = {'violated_rows': violated, 'lp_over_n': value / n, 'greedy_over_n': greedy / n}
    return out


def main(argv):
    n = int(argv[2]) if len(argv) > 2 else 1900
    seeds = int(argv[3]) if len(argv) > 3 else 3
    result = {'control': control(19, 100, np.random.default_rng(0)),
              'candidate': [candidate(n, 19, seed) for seed in range(1, seeds + 1)]}
    with open(argv[1], 'w') as handle:
        json.dump(result, handle, indent=1)
    print(json.dumps(result['control']))
    for run in result['candidate']:
        print(run['seed'], run['variables_in_no_zero_row'], run['least_zero_row_degree'],
              {name: (p['violated_rows'], round(p['greedy_over_n'], 4), round(p['lp_over_n'], 4))
               for name, p in run['points'].items()})


if __name__ == '__main__':
    main(sys.argv)
