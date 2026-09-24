"""Fit a part-size cap A_n to cube data over F_p.

Model: delta_F(n,k,l) = n + 2(k-1) - rho(k-l), where rho(s) is the least number of parts a with
Catalan C_{a-1} nonzero mod p and a <= A, summing to s-1.  For each n, report the caps A that fit
every computed value.  Over F_2 the proved law is this model with A = 2^(n-1).
Usage: bmd_cube_cap_fit.py DIR p
"""
import glob, json, sys
from math import comb


def rho_table(p, cap, smax):
    allowed = [a for a in range(1, cap + 1) if (comb(2 * (a - 1), a - 1) // a) % p]
    best = [0] + [None] * smax
    for m in range(1, smax + 1):
        opts = [best[m - a] + 1 for a in allowed if a <= m and best[m - a] is not None]
        best[m] = min(opts) if opts else None
    return best


def fits(cases, n, p, cap):
    kmax = max(k for k, _ in cases)
    best = rho_table(p, cap, kmax)
    return all(best[k - l - 1] is not None and d == n + 2 * (k - 1) - best[k - l - 1]
               for k, dl in cases for l, d in enumerate(dl))


d, p = sys.argv[1], int(sys.argv[2])
data = {}
for f in glob.glob(d + '/cube-p*-n*-k*.json'):
    r = json.load(open(f))
    data.setdefault(r['n'], []).append((r['k'], r['delta']))
for n in sorted(data):
    kmax = max(k for k, _ in data[n])
    caps = [cap for cap in range(1, kmax + 1) if fits(data[n], n, p, cap)]
    print(f'p={p} n={n} (k<={kmax}): fitting caps {caps}')
