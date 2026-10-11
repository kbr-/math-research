#!/usr/bin/env python3
"""Numerical control for entry sum-function-zero-count (finite configurations, the real line as the critical line).

Objects.  F(z) = prod (z - z_j), u zeros with Im z_j > 0, l zeros with Im z_j < 0, none real, n = u + l;
F#(z) = conj F(conj z) = prod (z - conj z_j);  A_theta = F + e^{i theta} F#.

Statements tested.
 C (count)       if e^{i theta} != -1, A_theta has degree n, at least |u - l| distinct real zeros, and at most
                 2 min(u, l) nonreal zeros.
 X (no converse) F(z) = (z - i)(z - T + i eps) has one zero in each half-plane, and A_0 = 2 (z^2 - T z + eps) has two
                 real zeros when T^2 > 4 eps.

Zeros are computed by numpy's companion-matrix routine; a zero counts as real when |Im| <= 1e-6 (1 + |Re|).  The
configurations are random with |Im z_j| >= 0.05, so that generic zeros of A_theta are not near the tolerance; the
script counts and reports the cases with a zero of A_theta whose |Im| lies between 1e-6 and 1e-3 times (1 + |Re|),
which are ambiguous, and leaves them out.

EXPECTED, WRITTEN BEFORE THE RUN (numbers are computed and printed by the script, none typed here):
 - C holds in every unambiguous case of 4000 random configurations with n from 2 to 12.
 - Negative control NC: the statement with |u - l| + 1 in place of |u - l|.  It differs from C exactly in the
   cases where the number of real zeros equals |u - l|; the script counts those cases, which are expected to
   exist, and in each of them the altered statement fails by construction of the count; reported as the number of
   cases where the bound |u - l| is attained.
 - The bound on nonreal zeros, 2 min(u, l), is expected to be attained in some cases as well.
 - X: both zeros of A_0 real for (T, eps) = (5, 0.1) and (1, 0.2); not both real for (1, 0.3), where T^2 < 4 eps.
"""
import argparse
import json
from pathlib import Path

import numpy as np


def real_count(roots):
    scale = 1 + np.abs(roots.real)
    real = np.abs(roots.imag) <= 1e-6 * scale
    ambiguous = (~real) & (np.abs(roots.imag) <= 1e-3 * scale)
    reals = np.sort(roots.real[real])
    distinct = 1 + int(np.sum(np.diff(reals) > 1e-6)) if len(reals) else 0
    return int(real.sum()), distinct, bool(ambiguous.any())


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--out', required=True)
    args = ap.parse_args()
    rng = np.random.default_rng(48)
    stats = {'cases': 0, 'ambiguous': 0, 'C_holds': 0, 'C_fails': 0, 'real_bound_attained': 0,
             'nonreal_bound_attained': 0, 'degree_drops': 0, 'by_degree': {}}
    failures = []
    for _ in range(4000):
        n = int(rng.integers(2, 13))
        re = rng.uniform(-3, 3, n)
        im = rng.uniform(0.05, 2.0, n) * rng.choice([-1.0, 1.0], n)
        z = re + 1j * im
        u, low = int((im > 0).sum()), int((im < 0).sum())
        theta = float(rng.uniform(-3.0, 3.0))
        F = np.poly(z)
        Fs = np.poly(z.conj())
        A = F + np.exp(1j * theta) * Fs
        stats['cases'] += 1
        if abs(A[0]) < 1e-9:
            stats['degree_drops'] += 1
            continue
        roots = np.roots(A)
        nreal, distinct, amb = real_count(roots)
        if amb:
            stats['ambiguous'] += 1
            continue
        ok = len(roots) == n and distinct >= abs(u - low) and (n - nreal) <= 2 * min(u, low)
        stats['C_holds' if ok else 'C_fails'] += 1
        if not ok and len(failures) < 5:
            failures.append({'n': n, 'u': u, 'l': low, 'theta': theta, 'real': nreal, 'distinct': distinct})
        stats['real_bound_attained'] += int(distinct == abs(u - low))
        stats['nonreal_bound_attained'] += int(n - nreal == 2 * min(u, low))
        d = stats['by_degree'].setdefault(str(n), [0, 0])
        d[0] += 1
        d[1] += int(ok)
    ex = []
    for T, eps in ((5.0, 0.1), (1.0, 0.2), (1.0, 0.3)):
        z = np.array([1j, T - 1j * eps])
        A = np.poly(z) + np.poly(z.conj())
        roots = np.roots(A)
        ex.append({'T': T, 'eps': eps, 'T2_minus_4eps': T * T - 4 * eps, 'roots': [[float(r.real), float(r.imag)] for r in roots],
                   'both_real': bool(np.all(np.abs(roots.imag) < 1e-9))})
    Path(args.out).write_text(json.dumps({'stats': stats, 'failures': failures, 'X': ex}, indent=1) + '\n')


if __name__ == '__main__':
    main()
