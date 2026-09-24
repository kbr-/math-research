"""Tabulate delta(n,c,0) - n from bmd_jet_orders outputs, next to v_2((2c-2)!) = 2(c-1) - s_2(c-1).

The per-order conjecture predicts delta(n,c,0) - n = v_2((2c-2)!) for n >= floor(log2 c)+2.
Usage: bmd_order0_table.py DIR [DIR ...]
"""
import glob, json, sys

vals = {}
for d in sys.argv[1:]:
    for p in glob.glob(d + '/n*-k*.json'):
        r = json.load(open(p))
        vals[(r['n'], r['k'])] = r['delta'][0]
ns = sorted({n for n, _ in vals})
cs = sorted({c for _, c in vals})
print('c  v2((2c-2)!) | delta(n,c,0)-n for n = ' + ' '.join(map(str, ns)))
for c in cs:
    pred = 2 * (c - 1) - bin(c - 1).count('1')
    row = ' '.join(f'{vals[(n, c)] - n:3d}' if (n, c) in vals else '  .' for n in ns)
    print(f'{c:2d} {pred:5d}        | {row}')
