"""Exact polynomial-calculus degree over F_2 of small majority systems, with the reach of the closure kernel.

Object.  n variables, n + 1 rows MAJ(x on V_a) = b_a with independent uniform scopes of odd width w = 2k + 1 and
independent uniform labels: the fourth candidate of the portfolio at small width.  A row of label 0 is written as
the monomials x_T, T a (k+1)-subset of its scope (no k + 1 ones); a row of label 1 as the products of 1 + x_i
over such T (no k + 1 zeros).  An instance is redrawn until every variable is in a row and no assignment
satisfies all rows, by enumeration of the 2^n assignments; the number of draws is recorded.

Computed.  The exact refutation degree by tools/f2_closure_degree.cpp (compiled, passed as KERNEL), with its
seconds and the peak memory of the process; and rho(1), rho(0) of lem:majority-point-bound by enumeration of all
subsets, the largest set meeting each scope of the violated label in at most k elements.

This first use is a sizing run at n = 14 and 16: the question is how far the kernel reaches, so that the series
the review of 12 October named (increments of the degree over sizes four apart) is run or cancelled by a
measurement.  The estimate to be tested: the kernel keeps at most M rows of M bits, M the number of monomials of
degree at most D, so its memory at the largest D it computes is at most M^2 / 8 bytes plus a baseline.

Refuted by: a measured peak above twice M^2/8 plus 64 MB at the largest D computed, in any case.
Possible because: the kernel also keeps a hash index of the monomials and copies of rows, which the estimate omits.

Control one, the kernel against the lemma, which do not share a method: degree <= max(min(rho(1), rho(0)) + 1, k + 1).
Refuted by: an exact degree above that bound in any instance of the run.
Possible because: the bound comes from an enumeration of sets and the degree from elimination, with separate encodings.

Control two, monotonicity: with one more random row the degree does not rise (n = 14 only).
Refuted by: a degree with the added row above the degree without it.
Possible because: a wrong encoding of a row of either label would add a polynomial outside the ideal or drop one.

No expectation is written for the degrees themselves at this size: the two lines the review compares, n/4 and
0.4 n with an additive term of the order of the width, are not separable at n = 14 and 16.

Usage: degree_series.py KERNEL SCRATCH_DIR OUT.jsonl W DMAX SEEDS N ...
"""
import itertools
import json
import math
import random
import resource
import subprocess
import sys
import time

import numpy as np


def draw(n, w, rng):
    return [(sorted(rng.sample(range(n), w)), rng.getrandbits(1)) for _ in range(n + 1)]


def satisfiable(n, rows, k):
    points = np.arange(1 << n, dtype=np.uint32)
    alive = np.ones(1 << n, dtype=bool)
    for scope, label in rows:
        mask = sum(1 << i for i in scope)
        alive &= (np.bitwise_count(points & np.uint32(mask)) >= k + 1) == bool(label)
    return bool(alive.any())


def instance(n, w, seed):
    """The first draw of the seed's stream that uses every variable and is unsatisfiable, with the draws made."""
    rng, k = random.Random(100000 * w + 1000 * n + seed), w // 2
    for draws in itertools.count(1):
        rows = draw(n, w, rng)
        if len({i for scope, _ in rows for i in scope}) == n and not satisfiable(n, rows, k):
            return rows, draws


def polynomials(rows, k):
    polys = []
    for scope, label in rows:
        for subset in itertools.combinations(scope, k + 1):
            if label == 0:
                polys.append([sum(1 << i for i in subset)])
            else:
                polys.append([sum(1 << i for i in part) for size in range(k + 2)
                              for part in itertools.combinations(subset, size)])
    for poly, (scope, label) in zip(polys[::math.comb(len(rows[0][0]), k + 1)], rows):
        point = sum(1 << i for i in scope) if label == 0 else 0      # a forbidden assignment: the polynomial is 1
        assert sum(point & t == t for t in poly) % 2 == 1
    return polys


def rho(n, rows, k, label):
    """The largest set meeting the scope of every row of this label in at most k elements, by enumeration."""
    sets = np.arange(1 << n, dtype=np.uint32)
    good = np.ones(1 << n, dtype=bool)
    for scope, row_label in rows:
        if row_label == label:
            good &= np.bitwise_count(sets & np.uint32(sum(1 << i for i in scope))) <= k
    return int(np.bitwise_count(sets[good]).max())


def degree(kernel, scratch, n, polys, dmax, tag):
    path = f'{scratch}/majority_{tag}.txt'
    with open(path, 'w') as handle:
        handle.write(f'{n} {len(polys)}\n' + ''.join(f'{len(p)} ' + ' '.join(map(str, p)) + '\n' for p in polys))
    start = time.time()
    got = json.loads(subprocess.run([kernel, path, str(dmax)], check=True, capture_output=True, text=True).stdout)
    return got['degree'], got['dimensions'], round(time.time() - start, 2)


def main(kernel, scratch, out, w, dmax, seeds, sizes):
    k = w // 2
    with open(out, 'a') as handle:
        for n in sizes:                                  # ascending, so the children's peak is the current case's
            monomials = sum(math.comb(n, j) for j in range(dmax + 1))
            assert monomials ** 2 / 8 < 6e9, f'n = {n}, D = {dmax}: {monomials} monomials, beyond the memory budget'
            for seed in range(1, seeds + 1):
                rows, draws = instance(n, w, seed)
                d, dims, seconds = degree(kernel, scratch, n, polynomials(rows, k), dmax, f'{w}_{n}_{seed}')
                peak = resource.getrusage(resource.RUSAGE_CHILDREN).ru_maxrss * 1024
                bound = max(min(rho(n, rows, k, 0), rho(n, rows, k, 1)) + 1, k + 1)
                result = {'w': w, 'n': n, 'seed': seed, 'draws': draws, 'rows': len(rows), 'exact_degree': d,
                          'searched_through': dmax, 'closure_dimensions': dims, 'seconds': seconds,
                          'rho_ones': rho(n, rows, k, 0), 'rho_zeros': rho(n, rows, k, 1), 'point_bound': bound}
                if d is not None:
                    at = sum(math.comb(n, j) for j in range(d + 1))
                    result.update(monomials_at_degree=at, estimate_bytes=at * at // 8, peak_bytes=peak,
                                  memory_within_estimate=peak <= 2 * (at * at // 8) + 64 * 2 ** 20,
                                  degree_within_point_bound=d <= bound)
                if n == 14 and d is not None:
                    extra = rows + [draw(n, w, random.Random(7000 + seed))[0]]
                    more, _, _ = degree(kernel, scratch, n, polynomials(extra, k), dmax, f'{w}_{n}_{seed}_more')
                    result.update(degree_with_added_row=more, monotone=more is not None and more <= d)
                handle.write(json.dumps(result) + '\n')
                handle.flush()
                print(json.dumps({key: value for key, value in result.items() if key != 'closure_dimensions'}))


if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2], sys.argv[3], int(sys.argv[4]), int(sys.argv[5]), int(sys.argv[6]),
         sorted(map(int, sys.argv[7:])))
