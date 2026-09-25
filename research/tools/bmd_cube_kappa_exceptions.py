"""List the m where the cube's root-curve orders kappa_n(m) fall below the capped Catalan count.

Statement tested (exception-set conjecture).  On {0,1}^n over F_p, kappa_n(m) <= rho_{<=n}(m+1)
always (Catalan linear forms); the conjecture is that equality holds except on a sparse set.
Reads KAPPA lines (the first trial with no COUNT DIFFER, and checks that all trials agree on the
reported range) from bmd_root_curve_orders_grid.py outputs, and prints, per (p, n), every m with
kappa < rho_{<=n}(m+1), together with rho_F(m+1) (uncapped) for reference.
Usage: bmd_cube_kappa_exceptions.py FILE:p:n ...
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
from bmd_cube_rho_cap_check import rho_capped


def main():
    for spec in sys.argv[1:]:
        path, p, n = spec.rsplit(':', 2)
        p, n = int(p), int(n)
        lines = Path(path).read_text().splitlines()
        bad = {l.split(' trial ')[1].split()[0] for l in lines if 'COUNT DIFFER' in l}
        trials = [l for l in lines if l.startswith('KAPPA')]
        kap = [dict((int(a), int(b)) for a, b in (x.split(':') for x in t.split(': ', 1)[1].split())) for t in trials]
        good = [k for t, k in zip(trials, kap) if t.split()[2].rstrip(':') not in bad]
        kappa = good[0]
        dmax = max(kappa.values())
        top = max(kappa)
        agree = all(all(k.get(m) == kappa.get(m) for m in kappa if kappa[m] < dmax) for k in good)
        capped = rho_capped(p, n, top + 1)
        free = rho_capped(p, 10 ** 6, top + 1)
        exc = [m for m in sorted(kappa) if kappa[m] < dmax and kappa[m] < capped[m]]
        # only m with kappa < dmax are certain (kappa = dmax may hide nothing, kappa > dmax is unseen)
        print(f'p={p} n={n}: trials agree: {agree}; m with kappa < {dmax} checked: '
              f'{sum(1 for m in kappa if kappa[m] < dmax)}; exceptions (m, kappa, capped, rho_F): '
              + ' '.join(f'({m},{kappa[m]},{capped[m]},{free[m]})' for m in exc), flush=True)


if __name__ == '__main__':
    main()
