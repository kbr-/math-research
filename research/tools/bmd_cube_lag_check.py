"""Test the one-step lag law for the cube's per-order savings against exact kernel values.

Statement tested (one-step lag law, conjectured).  On {0,1}^n over a field of characteristic
p != 2, the savings h = n + 2(k-1) - delta(n,k,l) at m = k-l-1 satisfy
    kappa_n(m) - 1 <= h <= kappa_n(m)   for every l >= 0,
where kappa_n is the refined root-curve order function (0 at m = 0, 1 on the n-allowed parts,
otherwise max(2, min{d : N_{2,n}(d) > m})).  The upper bound is the stable per-order law; the
lower bound is the conjecture.  The refined kappa is proved in the parameter ranges used here
(n <= 3; n = 4, 5 with m <= 43 and 47; p > 2^{n-1} d in general).

The compiled kernel bmd_jet_orders_q (--cube) gives delta(n,k,l) for every l in one elimination
per k; this script runs it for k = 1..KMAX (one pass per k, each k a new diagonal l + m = k - 1),
and writes every value as it finishes.  It reports violations of either bound and, for each m,
the least l from which h = kappa in the data.
Usage: bmd_cube_lag_check.py KERNEL p n KMAX OUT
"""
import json, subprocess, sys, tempfile, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from bmd_cube_rho_cap_check import kappa_refined


def main():
    kernel, p, n, kmax, out = sys.argv[1], int(sys.argv[2]), int(sys.argv[3]), int(sys.argv[4]), sys.argv[5]
    assert p % 2 == 1
    lag_viol, up_viol, total, eq = [], [], 0, 0
    lagging = {}  # m -> list of l with h = kappa - 1
    tmp = tempfile.mkdtemp()
    with open(out, 'w') as fh:
        for k in range(1, kmax + 1):
            path = os.path.join(tmp, f'k{k}.json')
            subprocess.run([kernel, str(p), str(n), str(k), '--cube', '--out', path],
                           check=True, capture_output=True)
            d = json.load(open(path))
            for l, v in enumerate(d['delta']):
                m = k - l - 1
                h = n + 2 * (k - 1) - v
                kap = kappa_refined(p, n, m)
                total += 1
                eq += h == kap
                if h > kap:
                    up_viol.append((k, l, m, h, kap))
                if h < kap - 1:
                    lag_viol.append((k, l, m, h, kap))
                if h == kap - 1:
                    lagging.setdefault(m, []).append(l)
                fh.write(f'k={k} l={l} m={m} h={h} kappa={kap}\n')
            fh.flush()
            print(f'k={k} done ({d["seconds"]:.2f} s)', flush=True)
        summary = [f'p={p} n={n} k<={kmax}: {total} values, h = kappa: {eq}',
                   f'upper-bound violations (h > kappa): {up_viol}',
                   f'lag-law violations (h < kappa - 1): {lag_viol}',
                   'lagging l by m (h = kappa - 1): ' + str({m: sorted(ls) for m, ls in sorted(lagging.items())})]
        for line in summary:
            print(line)
            fh.write(line + '\n')


if __name__ == '__main__':
    main()
