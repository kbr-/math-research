"""Bridge test (MacWilliams-type duality): is delta(3,k,l) + delta(3,k,k-1-l) independent of l for fixed k?"""
import sys
sys.path.insert(0, 'research/tools')
from bmd_cube_formula_check import delta
bad = 0
for k in range(2, 60):
    vals = {delta(k, l) + delta(k, k - 1 - l) for l in range(k)}
    if len(vals) > 1:
        bad += 1
        if bad <= 3:
            print(f"k={k}: sums {sorted(vals)}")
print(f"k in 2..59 with a non-constant sum: {bad}")
