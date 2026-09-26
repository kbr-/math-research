#!/usr/bin/env python3
"""Compare the dimension-3 per-order formula with every recorded exact kernel run (entry-2026-09-26-cube-formula).

Statement tested (thm:cube-dimension-three-per-order, characteristic 0).  For k >= 1, 0 <= l <= k-1 and m = k-l-1,
delta(3,k,l) = 2k+1-h with h = 0 if m = 0, and otherwise
    h = 1 + max{ d in [0, floor(m/4)] : 5d <= m+1  or  B(d, m+1-4d) <= l },
where B(d,rho) = sum(pi_i^2 - 1) over the balanced partition of d into rho parts.

Input: the JSON files of the per-order kernels under research/results with "grid": 2 and "n": 3, each holding the
exact values delta[l] for l = 0..k-1 over F_p.  The script prints, per prime, the number of (k,l) values compared and
every disagreement.  The formula is proved in characteristic 0; odd p may differ (open statement 1 in characteristic p).
"""
import glob
import json
import sys


def B(d, rho):
    q, r = divmod(d, rho)
    return (rho - r) * (q * q - 1) + r * ((q + 1) * (q + 1) - 1)


def delta(k, l):
    m = k - l - 1
    if m == 0:
        return 2 * k + 1
    h = 1 + max(d for d in range(m // 4 + 1) if 5 * d <= m + 1 or B(d, m + 1 - 4 * d) <= l)
    return 2 * k + 1 - h


def main():
    rows = {}
    for path in sorted(glob.glob('research/results/**/*.json', recursive=True)):
        try:
            data = json.load(open(path))
        except (ValueError, UnicodeDecodeError):
            continue
        if not isinstance(data, dict) or data.get('grid') != 2 or data.get('n') != 3 or 'delta' not in data:
            continue
        p, k = data['p'], data['k']
        for l, v in enumerate(data['delta']):
            if v is None:
                continue
            rows.setdefault(p, {})[(k, l)] = (v, path)
    bad = 0
    for p in sorted(rows):
        mism = [(k, l, v, delta(k, l), path) for (k, l), (v, path) in sorted(rows[p].items()) if v != delta(k, l)]
        ks = sorted({k for k, _ in rows[p]})
        print(f"p={p}: {len(rows[p])} values, k in {ks[0]}..{ks[-1]} ({len(ks)} values of k), disagreements {len(mism)}")
        for k, l, v, f, path in mism:
            print(f"  k={k} l={l}: recorded {v}, formula {f} ({path})")
        bad += len(mism)
    return 1 if bad else 0


if __name__ == '__main__':
    sys.exit(main())
