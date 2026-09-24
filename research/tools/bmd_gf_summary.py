"""Summarize saved subspace-grid runs: savings h = n(s-1) + s(k-1) - delta by m = k-l-1.

Reads every gf*-S*-n*-k*.json under RESULTS (written by bmd_gf_series.py) and prints, per field,
subspace and n, the savings for m = 0, 1, ...; a cell lists every value observed over l, so a
bracketed cell means the savings depend on l as well as m.  Also prints the coefficients of
L(x) = prod_{t in S}(x - t) at x^(2^i) and marks S as a scaled subfield when only the first and
last are nonzero.
Usage: bmd_gf_summary.py RESULTS POLY_a=poly ...   (e.g. 3=11 4=19 5=37 6=67 7=131)
"""
import json, sys
from pathlib import Path


def lcoeffs(a, poly, S):
    Q = 1 << a

    def mul(x, y):
        r = 0
        while y:
            if y & 1:
                r ^= x
            y >>= 1
            x <<= 1
            if x & Q:
                x ^= poly
        return r
    L = [1]
    for t in S:
        L = [0] + L
        for i in range(len(L) - 1):
            L[i] ^= mul(t, L[i + 1])
    return [L[1 << i] for i in range(len(S).bit_length())]


def main():
    root = Path(sys.argv[1])
    polys = dict(tuple(map(int, x.split('='))) for x in sys.argv[2:])
    table = {}
    for f in sorted(root.rglob('gf*-S*-n*-k*.json')):
        d = json.loads(f.read_text())
        a, S, n, k = d['a'], tuple(d['S']), d['n'], d['k']
        s = len(S)
        for l, v in enumerate(d['delta']):
            table.setdefault((a, S, n), {}).setdefault(k - l - 1, set()).add(n * (s - 1) + s * (k - 1) - v)
    for (a, S, n), row in sorted(table.items()):
        c = lcoeffs(a, polys[a], S)
        kind = 'scaled subfield' if all(x == 0 for x in c[1:-1]) else 'not a scaled subfield'
        cells = [sorted(row[m]) for m in range(max(row) + 1)]
        print(f'GF(2^{a}) S={list(S)} L-coeffs={c} ({kind}) n={n}: '
              + ' '.join(str(x[0]) if len(x) == 1 else str(x) for x in cells))


if __name__ == '__main__':
    main()
