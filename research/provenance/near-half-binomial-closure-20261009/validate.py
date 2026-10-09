#!/usr/bin/env python3
"""Validate binomial_closure against tools/truncated_buchberger.pc_degree.

Statement checked: for each system printed by the kernel with k = 2 and at most twelve bits (blocks read in F_4 with
y = b_1 + g b_2, g a generator), the kernel's refutation degree equals the polynomial-calculus
degree over F_2 of the system's clause polynomials.  Argument: kernel JSON-lines file.
"""
import itertools
import json
import sys
sys.path.insert(0, 'tools')
import truncated_buchberger as tb

LOG = {(1, 0): 0, (0, 1): 1, (1, 1): 2}          # log_g of b_1 + g b_2 in F_4, g^2 = g + 1
bad = checked = 0
for line in open(sys.argv[1]):
    if not line.startswith('{'):
        continue
    row = json.loads(line)
    if row['k'] != 2 or row['n'] > 12:      # the reference is pure Python
        continue
    n = row['n']
    axioms = []
    for blocks, exps, lam in row['rows']:
        for bits in itertools.product((0, 1), repeat=2 * len(blocks)):
            ys = [tuple(bits[2 * s:2 * s + 2]) for s in range(len(blocks))]
            allowed = all(y != (0, 0) for y in ys) and \
                sum(c * LOG[y] for c, y in zip(exps, ys)) % 3 == lam
            if not allowed:
                forms = [(1 << (2 * b + j), bits[2 * s + j] ^ 1)
                         for s, b in enumerate(blocks) for j in range(2)]
                axioms.append(tb.affine_product(n, forms))
    ref = tb.pc_degree(axioms, n, n)
    checked += 1
    bad += ref != row['degree']
    print('m', row['m'], 't', row['t'], 'seed', row['seed'], 'kernel', row['degree'], 'reference', ref)
print('checked', checked, 'mismatches', bad)
sys.exit(1 if bad else 0)
