"""Run bmd_jet_orders_q over a list of (p, n, k), save each case, and print a table with the recorded
checks: order k-1 gives n(p-1)+p(k-1) and k=2, l=0 gives n(p-1)+p-1 (thm:finite-field-high-origin-cover,
lem:finite-field-punctured-first-jet-degree).  Usage: bmd_q_series.py BIN OUTDIR p:n:k1-k2 ...
"""
import json, subprocess, sys
from pathlib import Path


def cases(specs):
    out = []
    for spec in specs:
        p, n, ks = spec.split(':')
        lo, hi = ks.split('-')
        out += [(int(p), int(n), k) for k in range(int(lo), int(hi) + 1)]
    return out


def main():
    binary, outdir = sys.argv[1], Path(sys.argv[2])
    outdir.mkdir(parents=True, exist_ok=True)
    bad = 0
    for p, n, k in cases(sys.argv[3:]):
        path = outdir / f'p{p}-n{n}-k{k}.json'
        subprocess.run([binary, str(p), str(n), str(k), '--out', str(path)], check=True, stdout=subprocess.DEVNULL)
        d = json.loads(path.read_text())['delta']
        checks = [d[k - 1] == n * (p - 1) + p * (k - 1)] + ([d[0] == n * (p - 1) + p - 1] if k == 2 else [])
        bad += not all(checks)
        print(f'p={p} n={n} k={k}: delta {d}  recorded-checks {"ok" if all(checks) else "FAIL"}', flush=True)
    print(f'recorded-check failures: {bad}')


if __name__ == '__main__':
    main()
