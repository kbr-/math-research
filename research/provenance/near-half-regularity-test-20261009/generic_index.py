#!/usr/bin/env python3
"""Generic-series index of each measured system, against its product index and fall-free degree.

Statement computed (side notebook near-half-pc-degree, entry-2026-10-09-regularity-measurement): for each
line of series.jsonl (output of clause_regularity.c), the index G of the generic series
(1+z)^n / (1+z^k)^m of conj:parity-clause-semiregular-degree, i.e. the first d with
sum_i (-1)^i C(m+i-1, i) C(n, d-ki) <= 0; the product index as far as the run reached; and whether the
run shows no degree fall and 1 outside the static span at degree G (then 1 is not in the PC closure C_G).
Arguments: input path, output path (one JSON line per system).
"""
import json
import sys
from math import comb


def generic_index(n, m, k):
    for d in range(n + 1):
        if sum((-1) ** i * comb(m + i - 1, i) * comb(n, d - k * i) for i in range(d // k + 1)) <= 0:
            return d
    return None


out = open(sys.argv[2], 'w')
count = 0
for line in open(sys.argv[1]):
    if not line.startswith('{'):
        continue
    r = json.loads(line)
    g = generic_index(r['n'], r['m'], r['k'])
    by = {b['d']: b for b in r['by_degree']}
    survives = g in by and r['nofall_through'] >= g and by[g]['one'] == 0
    row = {'n': r['n'], 'm': r['m'], 'k': r['k'], 'seed': r['seed'], 'generic_index': g,
           'product_index': r['index'], 'top_degree_run': max(by), 'fall_free_through': r['nofall_through'],
           'unit_outside_closure_at_generic_index': survives}
    out.write(json.dumps(row) + '\n')
    count += survives and (r['index'] == -1 or r['index'] > g)
print('systems with no refutation at the generic index and product index above it:', count)
