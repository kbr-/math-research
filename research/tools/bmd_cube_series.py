"""Per-order minima on the cube {0,1}^n over F_p (p odd) and comparison with Menezes' formula.

Menezes (arXiv 2609.19009, Theorem 1.1, statement only): for n >= k-1,
delta_F(n,k,l) = n + 2k - 2 - rho_F(k-l), rho_F(s) the least r with s-1 = a_1+...+a_r and every
Catalan number C_{a_i - 1} nonzero in F.  Values come from bmd_jet_orders_q --cube.
Usage: bmd_cube_series.py BIN OUTDIR p NMAX KMAX
"""
import itertools, json, subprocess, sys
from math import comb
from pathlib import Path


def rho(p, s, kmax):
    allowed = [a for a in range(1, kmax + 1) if (comb(2 * (a - 1), a - 1) // a) % p]
    best = [0] + [None] * kmax
    for m in range(1, kmax + 1):
        opts = [best[m - a] + 1 for a in allowed if a <= m and best[m - a] is not None]
        best[m] = min(opts) if opts else None
    return best[s - 1]


def menezes(p, n, k, kmax):
    return [n + 2 * k - 2 - rho(p, k - l, kmax) for l in range(k)]


def one_case(binary, outdir, p, n, k, kmax):
    path = outdir / f'cube-p{p}-n{n}-k{k}.json'
    subprocess.run([binary, str(p), str(n), str(k), '--cube', '--out', str(path)], check=True,
                   stdout=subprocess.DEVNULL)
    d = json.loads(path.read_text())['delta']
    men = menezes(p, n, k, kmax) if k >= 2 and n >= k - 1 else None
    print(f'p={p} n={n} k={k}: delta {d}' + (f'  Menezes {men}' if men else '  (below Menezes range)'), flush=True)
    if not men:
        return 0, 0
    return len(d), sum(a != b for a, b in zip(d, men))


def main():
    binary, outdir, p, nmax, kmax = sys.argv[1], Path(sys.argv[2]), int(sys.argv[3]), int(sys.argv[4]), int(sys.argv[5])
    outdir.mkdir(parents=True, exist_ok=True)
    checked = bad = 0
    for n, k in itertools.product(range(1, nmax + 1), range(1, kmax + 1)):
        c, b = one_case(binary, outdir, p, n, k, kmax)
        checked += c
        bad += b
    print(f'values in Menezes range: {checked}; mismatches: {bad}')


if __name__ == '__main__':
    main()
