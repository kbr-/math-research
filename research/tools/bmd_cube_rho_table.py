"""Implied savings rho_n(m) = n + 2(k-1) - delta(n,k,l), m = k-l-1, from cube outputs.

Prints one row per n; a cell lists every value observed (a single value means the savings depend
only on m, the exchange law).  Usage: bmd_cube_rho_table.py DIR p MMAX
"""
import glob, json, sys

d, p, mmax = sys.argv[1], int(sys.argv[2]), int(sys.argv[3])
seen = {}
for f in glob.glob(f'{d}/cube-p{p}-n*-k*.json'):
    r = json.load(open(f))
    for l, v in enumerate(r['delta']):
        seen.setdefault((r['n'], r['k'] - l - 1), set()).add(r['n'] + 2 * (r['k'] - 1) - v)
for n in sorted({n for n, _ in seen}):
    cells = [sorted(seen.get((n, m), ())) for m in range(mmax + 1)]
    print(f'p={p} n={n}: ' + ' '.join(str(c[0]) if len(c) == 1 else ('.' if not c else str(c)) for c in cells))
