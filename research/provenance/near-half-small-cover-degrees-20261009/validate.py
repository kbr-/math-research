#!/usr/bin/env python3
"""Validate cover_degree against tools/truncated_buchberger.pc_degree on small covers.

Statement checked: for each cover printed by the kernel at n = 6, the kernel's polynomial-calculus degree
equals the reference tool's.  Arguments: kernel JSON-lines file, how many rows to check.
"""
import json
import sys
sys.path.insert(0, 'tools')
import truncated_buchberger as tb

limit = int(sys.argv[2])
checked = bad = 0
for line in open(sys.argv[1]):
    if not line.startswith('{'):       # the saved log starts with its command line
        continue
    row = json.loads(line)
    if row.get('summary') or checked >= limit:
        continue
    n = row['n']
    axioms = []
    for part in row['cover'].split(';'):
        nums = [int(x) for x in part.split()]
        if not nums:
            continue
        forms = [(nums[1 + 2 * j], nums[2 + 2 * j] ^ 1) for j in range(nums[0])]
        axioms.append(tb.affine_product(n, forms))
    assert row['valid'] == 1
    ref = tb.pc_degree(axioms, n, n)
    checked += 1
    bad += ref != row['climbed_degree']
    print(row['class'], row['restart'], 'kernel', row['climbed_degree'], 'reference', ref)
print('checked', checked, 'mismatches', bad)
sys.exit(1 if bad else 0)
