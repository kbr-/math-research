#!/usr/bin/env python3
"""Majority rows: the first-moment bound for the constant point, and a search by block moves.

Statements tested (the entry's proposition and the quantity of lem:majority-point-bound).

A. First moment.  For m0 rows MAJ = 0 of odd width w = 2k + 1 with independent uniform scopes among n
   variables, rho(1) is the largest set S of variables with |S meet V_a| <= k for every row.  For every t,
       P(rho(1) >= t) <= C(n, t) * q_t ** m0,   q_t = P(Hypergeometric(n, t, w) <= k),
   and q_{n/2} = 1/2 exactly for n even.  first_moment() returns the least t at and above which that bound is
   below 1/1000; with probability at least 1 - n/1000 the true rho(1) is below it.
   Test: on sampled systems the greedy feasible set, a lower bound for rho(1), must be smaller than that t.
   Output that would refute the statement or the code: a greedy set of size at least the returned t.  It is
   possible: greedy sets reach about 0.52 n at m0 = n/2, and nothing in the search for S uses the bound.
   Expectation: no such output in any of the nine systems (three densities, three seeds).
   Not known to me before the run: the returned t at m0 = n/2, n and 2n for n = 1900, w = 19, and where the
   linear programme, an upper bound of another kind, falls against it.  The proposition says t <= n/2 at
   m0 >= n + 10, which the script asserts for m0 = 2n and prints for m0 = n.

B. Block moves, on the candidate as defined: n + 1 rows, uniform scopes of width 19, uniform labels.  From the
   point of all ones, a block move sets to zero the whole scope of a row of label 1, which makes that row
   violated with all its positions violating and shortens the violating positions of the rows of label 0
   through those variables.  The search tries the moves in a random order and keeps one when the linear
   programme's value at the new point is lower.
   Expectation: few moves are kept and the programme's value falls by less than 0.01 n.
   Output that would refute it: a fall of 0.01 n or more; a value below n/2 would be a ceiling for the sampled
   system.  It is possible: each move adds a constraint with a full scope, and I have no proof that the
   relaxation of the other rows outweighs it.

Usage: density.py OUT.json
"""
import json
import sys

import numpy as np
from scipy.optimize import linprog
from scipy.sparse import csr_matrix
from scipy.special import gammaln
from scipy.stats import hypergeom


def bracket(scopes, labels, sigma, k):
    """(violated rows, LP value, greedy feasible size) of rho(sigma); as in the point-bound script."""
    n = sigma.size
    violating = sigma[scopes] != labels[:, None]
    rows = np.nonzero(violating.sum(axis=1) >= k + 1)[0]
    if rows.size == 0:
        return 0, float(n), n
    mask = violating[rows]
    row_index = np.repeat(np.arange(rows.size), mask.sum(axis=1))
    matrix = csr_matrix((np.ones(row_index.size), (row_index, scopes[rows][mask])), shape=(rows.size, n))
    solved = linprog(-np.ones(n), A_ub=matrix, b_ub=np.full(rows.size, float(k)), bounds=(0, 1), method='highs')
    assert solved.status == 0, solved.message
    used = np.zeros(rows.size)
    columns = matrix.tocsc()
    chosen = 0
    for variable in np.argsort(-solved.x, kind='stable'):
        hit = columns.indices[columns.indptr[variable]:columns.indptr[variable + 1]]
        if np.all(used[hit] < k):
            used[hit] += 1
            chosen += 1
    return int(rows.size), float(-solved.fun), int(chosen)


def first_moment(n, w, m0):
    """Least t with C(n, t') q_t' ** m0 < 1/1000 for every t' >= t."""
    k = (w - 1) // 2
    t = np.arange(k + 1, n + 1)
    log_bound = (gammaln(n + 1) - gammaln(t + 1) - gammaln(n - t + 1)
                 + m0 * hypergeom.logcdf(k, n, t, w))                  # population n, t marked, w drawn
    bad = np.nonzero(log_bound >= np.log(1e-3))[0]
    return int(t[bad.max()] + 1) if bad.size else int(t[0])


def uniform_scopes(rng, rows, n, w):
    return np.argsort(rng.random((rows, n)), axis=1)[:, :w]


def part_a(n, w):
    k = (w - 1) // 2
    assert abs(hypergeom.cdf(k, n, n // 2, w) - 0.5) < 1e-12           # q at n/2 is one half, n even
    out = []
    for m0 in (n // 2, n, 2 * n):
        threshold = first_moment(n, w, m0)
        if m0 == 2 * n:
            assert threshold <= n // 2, threshold
        # Changed after two runs were stopped by their time limits (12 October 2026): the programme with 2n
        # rows took about 190 s for one system, so that density has one seed.  The six systems of the lower
        # densities and the first of this one had been seen; the test and its expectation are unchanged.
        for seed in ((1,) if m0 == 2 * n else (1, 2, 3)):
            rng = np.random.default_rng(1000 * m0 + seed)
            scopes = uniform_scopes(rng, m0, n, w)
            _, value, greedy = bracket(scopes, np.zeros(m0, dtype=np.int64), np.ones(n, dtype=np.int64), k)
            assert greedy < threshold, (m0, seed, greedy, threshold)   # the statement's test
            out.append({'n': n, 'w': w, 'm0': m0, 'seed': seed, 'first_moment_over_n': threshold / n,
                        'greedy_over_n': greedy / n, 'lp_over_n': value / n})
            print('A', out[-1], flush=True)
    return out


def part_b(n, w, seed, tries):
    rng = np.random.default_rng(seed)
    k = (w - 1) // 2
    scopes = uniform_scopes(rng, n + 1, n, w)
    labels = rng.integers(0, 2, n + 1)
    sigma = np.ones(n, dtype=np.int64)
    _, start, start_greedy = bracket(scopes, labels, sigma, k)
    value, kept = start, 0
    for row in rng.permutation(np.nonzero(labels == 1)[0])[:tries]:
        trial = sigma.copy()
        trial[scopes[row]] = 0
        _, trial_value, _ = bracket(scopes, labels, trial, k)
        if trial_value < value - 1e-9:
            sigma, value, kept = trial, trial_value, kept + 1
    _, final, final_greedy = bracket(scopes, labels, sigma, k)
    out = {'n': n, 'w': w, 'seed': seed, 'tries': tries, 'kept': kept, 'start_lp_over_n': start / n,
           'final_lp_over_n': final / n, 'start_greedy_over_n': start_greedy / n,
           'final_greedy_over_n': final_greedy / n, 'zeros_at_end': int((sigma == 0).sum())}
    print('B', out, flush=True)
    return out


def main(argv):
    result = {'block_moves': [part_b(570, 19, seed, 120) for seed in (1, 2, 3)]}
    with open(argv[1], 'w') as handle:                                  # the searches first, saved at once
        json.dump(result, handle, indent=1)
    result['first_moment'] = part_a(1900, 19)
    with open(argv[1], 'w') as handle:
        json.dump(result, handle, indent=1)


if __name__ == '__main__':
    main(sys.argv)
