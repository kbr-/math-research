"""Tally squarefreeness outcomes of bmd_cube_nu_squarefree by monotonicity of the degree vector.

A degree vector is monotone when nu_r >= nu_{r'} whenever r <= r' (as subsets).
Usage: nutally.py N OUTPUT...
"""
import re
import sys
from collections import Counter

n = int(sys.argv[1])
tally = Counter()
fails = []
for path in sys.argv[2:]:
    for line in open(path):
        m = re.search(r'nu=([-0-9,]+) .*\| (SQUAREFREE|REPEATED|DEGREE-DROP)', line)
        if not m:
            continue
        nu = [int(x) for x in m.group(1).split(',')]
        mono = all(nu[r] >= nu[r | (1 << i)] for r in range(1 << n) for i in range(n) if not r >> i & 1)
        tally[(mono, m.group(2))] += 1
        if m.group(2) != 'SQUAREFREE':
            fails.append((nu, mono))
print(dict(tally))
print('non-squarefree:', fails)
