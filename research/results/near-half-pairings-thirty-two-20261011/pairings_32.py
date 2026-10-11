"""Paired-pigeon subspaces without linear relations at 28 to 36 holes: exact degrees through four.

Queue check pigeonhole-affine-restriction; the run a reviewer required of it on 11 October 2026.  Class, rows
and filter as in ../near-half-block-free-pairing-20261011/block_free.py (imported): n holes, n/2 + 1 pairs,
three options to a pair, free dimension N = n + 2, pairings kept when the span of the rows has no nonzero
polynomial of degree at most one.

Prediction, written before any run.  The count compares, at degree D, the multiples available, rows times the
number of monomials of degree at most D - 2, with the number of monomials of degree at most D; the count
predicts a refutation at the least D where the first exceeds the second.  With about 4.5 n rows this is D = 3
up to about 27 holes and D = 4 from 28 to about 54.  So:
  - if the count governs the degree, every instance at 28, 32 and 36 holes has degree exactly 4;
  - if the degree stays where it was at 14 to 24 holes, every instance has degree 3;
  - if the degree grows faster than the count, some instance has no refutation through degree 4.
The control at 24 holes repeats the first instance of the recorded survey, degree 3, with the kernel as
extended beyond 26 variables.  The script prints both counts for each instance beside its degree.

Usage: python3 pairings_32.py KERNEL_BINARY SCRATCH_DIR OUT.json HOLES:INSTANCES ...
"""
import importlib.util
import json
import sys
import time
from math import comb
from pathlib import Path

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location(
    'block_free', HERE.parent / 'near-half-block-free-pairing-20261011' / 'block_free.py')
bf = importlib.util.module_from_spec(spec)
spec.loader.exec_module(bf)


def below(free, degree):
    return sum(comb(free, i) for i in range(degree + 1))


def predicted(free, rows):
    """The least D at which rows times the monomials of degree <= D - 2 exceed the monomials of degree <= D."""
    return next(d for d in range(2, free + 1) if rows * below(free, d - 2) > below(free, d))


def case(binary, scratch, n, seed_after):
    seed, free, rows = bf.relation_free(n, seed_after)
    assert free == n + 2 and not bf.has_linear_relation(rows)
    start = time.time()
    got = bf.pp.degree(binary, scratch, free, rows, 4)
    return seed, {'holes': n, 'seed': seed, 'free_dimension': free, 'rows': len(rows), 'degree': got['degree'],
                  'dimensions': got['dimensions'], 'predicted_by_count': predicted(free, len(rows)),
                  'multiples_at_3': len(rows) * below(free, 1), 'monomials_at_3': below(free, 3),
                  'multiples_at_4': len(rows) * below(free, 2), 'monomials_at_4': below(free, 4),
                  'seconds': round(time.time() - start, 1)}


def repeated(size):
    """'32:3' as [32, 32, 32]."""
    n, count = size.split(':')
    return [int(n)] * int(count)


def main(binary, scratch, out, sizes):
    wanted = sum(map(repeated, sizes), [])
    results, last = [], {}
    for n in wanted:
        # 24 holes continues the recorded survey's seeds (from 24000); the new sizes start at 1000 n
        last[n], result = case(binary, scratch, n, last.get(n, 1000 * n))
        results.append(result)
        with open(out, 'w') as handle:
            json.dump(results, handle, indent=1)
    print(json.dumps([{k: r[k] for k in ('holes', 'seed', 'rows', 'degree', 'predicted_by_count', 'seconds')}
                      for r in results]))


if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4:])
