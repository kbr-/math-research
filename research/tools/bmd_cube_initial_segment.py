"""Test the initial-segment law for the cube's root-curve orders.

Statement tested.  If the Catalan numbers C_0, ..., C_{n-1} are nonzero in F, the orders of
polynomials of degree <= d in the cube root curve form the initial segment {0, ..., N_{2,n}(d) - 1},
so kappa_n(m) = min{d : N_{2,n}(d) > m}.  (Degree 1 already forces the hypothesis: the degree-1
orders are the n-allowed Catalan parts, an initial segment exactly when C_0..C_{n-1} are nonzero.)
Reads every KAPPA line with no COUNT DIFFER from bmd_root_curve_orders_grid.py outputs and reports,
per trial, for m with kappa below the computed degree, whether kappa matches the law.
Usage: bmd_cube_initial_segment.py FILE:p:n ...
"""
import sys
from pathlib import Path


def N(n, d):
    counts = [1]
    for _ in range(n):
        new = [0] * (len(counts) + 1)
        for i, c in enumerate(counts):
            new[i] += c
            new[i + 1] += c
        counts = new
    return sum(c for Qd in range(0, d + 1, 2) for i, c in enumerate(counts) if i <= d - Qd)


def main():
    for spec in sys.argv[1:]:
        path, p, n = spec.rsplit(':', 2)
        p, n = int(p), int(n)
        cat = [1]
        for j in range(1, n + 1):
            cat.append(cat[-1] * 2 * (2 * j - 1) // (j + 1))
        hyp = all(c % p for c in cat[:n])
        lines = Path(path).read_text().splitlines()
        bad = {l.split(' trial ')[1].split()[0] for l in lines if 'COUNT DIFFER' in l}
        results = []
        for t in lines:
            if not t.startswith('KAPPA') or t.split()[2].rstrip(':') in bad:
                continue
            kappa = dict((int(a), int(b)) for a, b in (x.split(':') for x in t.split(': ', 1)[1].split()))
            dmax = max(kappa.values())
            checked = [m for m in kappa if kappa[m] < dmax]
            law = {m: min(d for d in range(dmax + 2) if N(n, d) > m) for m in range(max(kappa) + 1)}
            miss = [m for m in checked if kappa[m] != law[m]]
            absent = [m for m in range(N(n, dmax - 1)) if m not in kappa or kappa[m] >= dmax]
            results.append((not miss and not absent, len(checked), miss, absent))
        holds = sum(r[0] for r in results)
        # a specialization can only lose orders or move them; the law is supported when some trial
        # attains it and the others are reported, not hidden
        print(f'p={p} n={n}: C_0..C_(n-1) nonzero: {hyp}; trials with full count: {len(results)}; '
              f'law holds in {holds} of them; per trial (holds, checked m, mismatches, absent): {results}',
              flush=True)


if __name__ == '__main__':
    main()
