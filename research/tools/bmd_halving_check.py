"""Check two all-dimension patterns on bmd_jet_orders outputs.

(H) delta(n,c,0) = n + sum_{j<n} floor((c-1)/2^j)   for every n >= 1, c >= 1;
(X) delta(n,k,l) = 2l + delta(n,k-l,0)              for every n >= 1, 0 <= l < k.
Together they give delta(n,k,l) = 2l + n + sum_{j<n} floor((k-l-1)/2^j), which equals
n+2k-2-s_2(k-l-1) once 2^n > k-l-1.  Usage: bmd_halving_check.py DIR [DIR ...]
"""
import glob, json, sys


def halving(n, c):
    return n + sum((c - 1) >> j for j in range(n))


delta = {}
for d in sys.argv[1:]:
    for p in glob.glob(d + '/n*-k*.json'):
        r = json.load(open(p))
        delta[(r['n'], r['k'])] = r['delta']
h_bad = [(n, c) for (n, c), dl in delta.items() if dl[0] != halving(n, c)]
x_pairs = [(n, k, l) for (n, k), dl in delta.items() for l in range(k) if (n, k - l) in delta]
x_bad = [(n, k, l) for n, k, l in x_pairs if delta[(n, k)][l] != 2 * l + delta[(n, k - l)][0]]
phi_pairs = [(n, k, l) for (n, k), dl in delta.items() for l in range(k)]
phi_bad = [(n, k, l) for n, k, l in phi_pairs if delta[(n, k)][l] != 2 * l + halving(n, k - l)]
print(f'cases {len(delta)}, n in {sorted({n for n, _ in delta})}, k up to {max(k for _, k in delta)}')
print(f'(H) checked {len(delta)} values of delta(n,c,0); mismatches {len(h_bad)} {sorted(h_bad)[:20]}')
print(f'(Phi) checked {len(phi_pairs)} per-order values against 2l + halving(n,k-l); mismatches {len(phi_bad)}')
print(f'(X) checked {len(x_pairs)} per-order values; mismatches {len(x_bad)} {sorted(x_bad)[:20]}')
