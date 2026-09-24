"""Compare exact per-order minima D_l(n,k) with n+2k-2-s_2(k-l-1) (Menezes, arXiv 2609.19009, Cor. 1.3).

The published formula is proved for n >= k-1; values with n < k-1 are reported separately.
Usage: bmd_menezes_compare.py RESULTS_DIR (the c1-exact-table directory)
"""
import glob, json, sys

def formula(n, k, l):
    return n + 2 * k - 2 - bin(k - l - 1).count('1')

compared = in_range = 0
mismatches, below = [], set()
for path in sorted(glob.glob(sys.argv[1] + '/n*-k*.json')):
    d = json.load(open(path))
    n, k = d['n'], d['k']
    for l, o in enumerate(d['orders']):
        v = o['min_degree']
        if v is None:                       # order not computed exactly (degree cap)
            continue
        compared += 1
        if n >= k - 1:
            in_range += 1
        else:
            below.add((n, k))
        if v != formula(n, k, l):
            mismatches.append((n, k, l, v, formula(n, k, l)))
    D = d['D']
    Dform = min(formula(n, k, l) for l in range(k))
    if D != Dform:
        mismatches.append((n, k, 'min', D, Dform))
print(f'per-order values compared: {compared} | in their range n>=k-1: {in_range} | '
      f'below it: {compared - in_range} | mismatches: {mismatches} | below-range cases: {sorted(below)}')
