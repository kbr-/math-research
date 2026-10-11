#!/usr/bin/env python3
"""Largest degree drop of zeta^weight on a binary linear code, by exhaustive search at small sizes.

Statement behind the search (the entry's lemma).  For zeta of odd order p > 1 in an extension of F_2 and a
linear code C of length N and dimension k, written with an information set y and w = N - k further coordinates
that are linear forms of y, the function y -> zeta^{wt(c(y))} has degree at least k - w, and the drop
delta(C) = k - degree is what a row built from C contributes to a common-root symmetric barrier: rows of
codimension w with drop delta, placed on any coordinates, give a barrier at D = w + delta - 1.

Proved before the run, and asserted here on every configuration: 0 <= delta <= w; delta = 0 when w = 1.
Known configuration, asserted as the control: m triples (each information coordinate repeated twice more),
w = 2m, order 3, has delta = m exactly.

Question the search answers: is delta > w/2 possible?  Hypothesis written before the run, which I hold weakly:
no, max delta = floor(w/2) at order 3 for every (k, w) searched, so triples are best and the example's
3w/2 - 1 is the limit of common-root barriers of order 3.  A configuration with delta > w/2 refutes it and is
printed with its forms.  For order 7 both zeta and its inverse must drop (the row through the all-ones point is
the complement), and I expect a smaller maximum than at order 3, replication by seven costing six coordinates.

Search space: all multisets of w nonzero forms on k coordinates (repetition allowed), k and w as listed in
main(); the information coordinates are present once.  Field elements are integers with XOR as addition.

Usage: root_drop.py OUT.json
"""
import itertools
import json
import sys

import numpy as np

POWERS = {3: np.array([1, 2, 3], dtype=np.uint8),                      # F_4, zeta^2 = zeta + 1
          7: np.array([1, 2, 4, 3, 6, 7, 5], dtype=np.uint8)}          # F_8, zeta^3 = zeta + 1


def degrees(exponents, table, k):
    """Degree in y of the function with values table[exponents[:, y]], one row per configuration."""
    values = table[exponents]
    points = np.arange(1 << k)
    for bit in range(k):
        upper = points[(points >> bit) & 1 == 1]
        values[:, upper] ^= values[:, upper ^ (1 << bit)]               # Moebius transform, XOR as addition
    weight = np.array([bin(y).count('1') for y in points])
    return np.where(values != 0, weight[None, :], -1).max(axis=1)


def search(order, k, w, chunk=200000):
    points = np.arange(1 << k)
    forms = np.arange(1, 1 << k)
    parity = np.array([[bin(f & y).count('1') & 1 for y in points] for f in forms], dtype=np.int16)
    base = np.array([bin(y).count('1') for y in points], dtype=np.int16)
    best, witness, count = -1, None, 0
    iterator = itertools.combinations_with_replacement(range(forms.size), w)
    while True:
        block = np.array(list(itertools.islice(iterator, chunk)), dtype=np.int64)
        if block.size == 0:
            break
        count += block.shape[0]
        weight = base[None, :] + parity[block].sum(axis=1)
        drop = k - degrees(weight % order, POWERS[order], k)
        if order != 3:                                                   # the inverse root must drop too
            drop = np.minimum(drop, k - degrees((-weight) % order, POWERS[order], k))
        assert drop.min() >= 0 and drop.max() <= w, (order, k, w, drop.min(), drop.max())
        if w == 1:
            assert drop.max() == 0
        if drop.max() > best:
            best = int(drop.max())
            witness = [int(forms[i]) for i in block[int(drop.argmax())]]
    return {'order': order, 'k': k, 'w': w, 'configurations': count, 'max_drop': best, 'forms': witness}


def control():
    for m in (1, 2, 3):
        k = m
        points = np.arange(1 << k)
        weight = 3 * np.array([[bin(y).count('1') for y in points]])
        assert k - degrees(weight % 3, POWERS[3], k)[0] == m             # triples: the function is constant
    return 'triples: drop m at w = 2m for m = 1, 2, 3'


def main(argv):
    cases = [(3, k, w) for k in (2, 3, 4, 5) for w in range(1, 7)] + [(3, 6, w) for w in range(1, 5)]
    cases += [(7, k, w) for k in (2, 3, 4) for w in range(1, 7)]
    result = {'control': control(), 'cases': []}
    for order, k, w in cases:
        case = search(order, k, w)
        result['cases'].append(case)
        print(case['order'], case['k'], case['w'], case['configurations'], case['max_drop'], case['forms'],
              flush=True)
    with open(argv[1], 'w') as handle:
        json.dump(result, handle, indent=1)


if __name__ == '__main__':
    main(sys.argv)
