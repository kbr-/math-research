"""Integer determinants and factor counts of the unit-step construction, small paths.

Statement tested (the draft proof of the path rank saturation lemma): for every word w with nonnegative partial
sums P_0 = 0, P_1, ..., P_d = 0, the unit-step construction of unit_step_paths.py gives a partial derivative
matrix of determinant +1 or -1 over Z (1 in the orders of the proof; this script's row and column orders are the
lexicographic ones of the digit tuples, which may permute rows and columns), and exactly
s(w) = sum_i 2^max(P_(i-1), P_i) factors.
Expected: |det| = 1 over Z and the count formula exact, for all 135 paths with k <= 2, d <= 6 and k = 3, d <= 5.
Refuted by: an integer determinant other than +1 or -1, or a factor count differing from the formula.
Possible because: the F_2 run showed only odd determinants, which allows 3 or -5, and the formula is a hand count.
Baseline: the plainest bound, |det| at most the product of the row norms, decides nothing; the F_2 ranks of
unit_step_paths.json give odd determinants only.
Record checked: the claims lem:nested-word-rank-saturation and imp:noncommutative-homogenization-lower-bound were
read; neither gives these determinants.
"""
import argparse
import json
import sys
from fractions import Fraction

import numpy as np

sys.path.insert(0, 'research/results/nested_word_rank_20261017')
from unit_step_paths import paths, sequence  # noqa: E402


def integer_pdm(p, seq):
    sizes = [2 ** abs(x) for x in p]
    levels = [np.ones(1, dtype=object)]
    for t in range(len(p)):
        levels.append(np.zeros(int(np.prod(sizes[:t + 1])), dtype=object))
    for (t, a) in seq:
        prev = levels[t]
        levels[t + 1].reshape(len(prev), sizes[t])[:, a] += prev
    coef = levels[len(p)].reshape(sizes)
    pos = [i for i, x in enumerate(p) if x > 0]
    neg = [i for i, x in enumerate(p) if x < 0]
    rows = int(np.prod([sizes[i] for i in pos]))
    return np.transpose(coef, pos + neg).reshape(rows, -1)


def det(m):
    a = [[Fraction(int(x)) for x in row] for row in m]
    n, d = len(a), Fraction(1)
    for c in range(n):
        piv = next((r for r in range(c, n) if a[r][c] != 0), None)
        if piv is None:
            return 0
        if piv != c:
            a[c], a[piv] = a[piv], a[c]
            d = -d
        d *= a[c][c]
        for r in range(c + 1, n):
            f = a[r][c] / a[c][c]
            if f:
                a[r] = [x - f * y for x, y in zip(a[r], a[c])]
    return d


def formula(p):
    s, prev = 0, 0
    for x in p:
        cur = prev + x
        s += 2 ** max(prev, cur)
        prev = cur
    return s


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--out', required=True)
    args = ap.parse_args()
    rows = []
    for k, dmax in ((1, 6), (2, 6), (3, 5)):
        for d in range(2, dmax + 1):
            for p in paths(k, d):
                seq = sequence(p)
                dt = det(integer_pdm(p, seq))
                rows.append(dict(path=p, det=int(dt), factors=len(seq), formula=formula(p)))
    print('paths:', len(rows), 'with |det| = 1:', sum(abs(r['det']) == 1 for r in rows),
          'with factors = formula:', sum(r['factors'] == r['formula'] for r in rows))
    print('exceptions:', [r for r in rows if abs(r['det']) != 1 or r['factors'] != r['formula']][:5])
    with open(args.out, 'w') as f:
        json.dump(rows, f)


if __name__ == '__main__':
    main()
