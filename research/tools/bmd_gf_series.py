"""Savings table for subspace grids S^n in GF(2^a): h(n,m) = n(s-1) + s(k-1) - delta(n,k,l), m = k-l-1.

Runs bmd_jet_orders_gf for n = 1..NMAX, k = 1..KMAX, saves each case, and prints one row per n
(a cell lists every observed value; one value means the savings depend only on m).
Usage: bmd_gf_series.py BIN OUTDIR a poly NMAX KMAX S0 S1 ...
"""
import itertools, json, subprocess, sys
from pathlib import Path


def run(binary, outdir, a, poly, S, n, k):
    path = outdir / f'gf{a}-S{"_".join(map(str, S))}-n{n}-k{k}.json'
    subprocess.run([binary, str(a), str(poly), str(n), str(k), *map(str, S), '--out', str(path)],
                   check=True, stdout=subprocess.DEVNULL)
    return json.loads(path.read_text())['delta']


def main():
    binary, outdir, a, poly, nmax, kmax = sys.argv[1], Path(sys.argv[2]), *map(int, sys.argv[3:7])
    S = [int(x) for x in sys.argv[7:]]
    s = len(S)
    outdir.mkdir(parents=True, exist_ok=True)
    seen = {}
    for n, k in itertools.product(range(1, nmax + 1), range(1, kmax + 1)):
        d = run(binary, outdir, a, poly, S, n, k)
        for l, v in enumerate(d):
            seen.setdefault((n, k - l - 1), set()).add(n * (s - 1) + s * (k - 1) - v)
    for n in range(1, nmax + 1):
        cells = [sorted(seen.get((n, m), ())) for m in range(kmax)]
        print(f'S={S} n={n}: ' + ' '.join(str(c[0]) if len(c) == 1 else str(c) for c in cells), flush=True)


if __name__ == '__main__':
    main()
