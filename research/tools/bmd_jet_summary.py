"""Summarize bmd_jet_orders results in a directory against n+2k-2-s_2(k-l-1).

Counts cases and per-order values, separates base dimension n = floor(log2 k)+2, lists mismatches
and the open orders (l <= k-3 with s_2(k-l-1) < floor(log2 k)), i.e. those not settled by D(n,k)
or by the high-origin cover theorem.  Usage: bmd_jet_summary.py DIR
"""
import glob, json, sys


def formula(n, k, l):
    return n + 2 * k - 2 - bin(k - l - 1).count('1')


rows = [json.load(open(p)) for p in sorted(glob.glob(sys.argv[1] + '/n*-k*.json'))]
rows.sort(key=lambda r: (r['n'], r['k']))
values = base = open_orders = 0
bad = []
for r in rows:
    n, k = r['n'], r['k']
    J = k.bit_length() - 1
    is_base = n == J + 2
    for l, d in enumerate(r['delta']):
        values += 1
        base += is_base
        open_orders += is_base and l <= k - 3 and bin(k - l - 1).count('1') < J
        if d != formula(n, k, l):
            bad.append((n, k, l, d, formula(n, k, l)))
print(f'cases {len(rows)}: ' + ', '.join(f"({r['n']},{r['k']})" for r in rows))
print(f'per-order values {values}, at base dimension {base}, open orders at base dimension {open_orders}')
print(f'mismatches with n+2k-2-s_2(k-l-1): {len(bad)} {bad}')
