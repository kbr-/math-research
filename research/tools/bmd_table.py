"""Summarize bmd_min_degree JSON outputs: D(n,k), D_l by origin order, and the recorded bounds."""
import glob, json, sys
rows = []
for path in sorted(glob.glob(sys.argv[1] + '/n*-k*.json')):
    d = json.load(open(path))
    n, k = d['n'], d['k']
    by_l = [o['min_degree'] for o in d['orders']]
    upper = n if k == 1 else n + 2 * k - 3
    rows.append((n, k, d['msz_lower'], d['D'], upper, by_l))
rows.sort()
print('n k | MSZ lower | D(n,k) | n+2k-3 | D - MSZ | argmin l | D_l for l=0..k-1')
for n, k, lo, D, up, by_l in rows:
    arg = [l for l, v in enumerate(by_l) if v == D]
    print(f'{n} {k} | {lo:9d} | {D:6d} | {up:6d} | {D - lo:7d} | {str(arg):8s} | {by_l}')
