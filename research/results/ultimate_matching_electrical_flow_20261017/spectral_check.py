"""Check the spectral bounds behind the electrical flow obstruction (entry-2026-10-17-electrical-flow-obstruction).

Statement tested, on the k x k grid of cells with unit conductances and Neumann (free) boundary: for each
horizontal edge e, M_e = ||Delta^+ b_e||^2 (b_e the edge's incidence vector, Delta^+ the pseudo-inverse of the
grid Laplacian) satisfies
  (i)   the mean of M_e over the k(k-1) horizontal edges is at least ln(k)/pi^4;
  (ii)  every M_e is at most (pi^3/16) ln(k) + 6.0;
  (iii) every entry of w_e = Delta^+ b_e has |w_e(Q)| <= 1 (the current on e of the unit flow from Q to the
        uniform sink);
  (iv)  the fraction of horizontal edges with M_e >= ln(k)/(2 pi^4) is at least m/(2U), m the mean and U the
        maximum, as the counting step of the proof gives.
Expected outcome, written before the run: (i)-(iv) hold at k = 8, 16, 32, 64, 128; the mean grows like
ln(k)/(4 pi) by the continuum heuristic (about 0.165 at k = 8 and 0.386 at k = 128).

M_e is computed from numeric eigenvectors of the path's Neumann Laplacian (numpy eigh), not from the cosine
formula the proof uses; for k <= 32 it is also computed by a direct pseudo-inverse of the k^2 x k^2 Laplacian,
a route sharing nothing with the spectral sum.
Control: the spectral and direct routes agree to 1e-9 at k <= 32 (printed beside the size of M_e).
Refuted by: a disagreement above 1e-9 between the two routes at some k at most 32.
Possible because: the spectral sum drops or double-counts eigenpairs if the (0,0) mode or the edge indexing is wrong.
Positive control: the same mean check run with every eigenvalue multiplied by 4 (planted error, M_e divided by 16)
must fail (i) at k = 128, where 16 ln(k)/pi^4 exceeds the true mean.
Refuted by: the planted run passing (i) at k = 128, which would show the check cannot see a factor 16.
Possible because: if the true mean exceeded 16 ln(k)/pi^4 the planted error would go unseen.
Prediction refuted by: any of (i)-(iv) failing at a k computed.
Possible because: the proof's inequalities sin x >= 2x/pi and the lattice-sum comparison could be misapplied.
Baseline: Cauchy-Schwarz gives M_e >= R_eff(e)^2/||b_e||^2, a constant (R_eff of a grid edge is at most 1), with no
growth in k; it does not decide (i).
Record checked: lem:balanced-sandpile-flow (its least-energy step bounds the average second moment, not one
edge), lem:straight-cut-forced-flux and thm:dyadic-flow-obstruction, read this cycle; none decides (i)-(iv).
"""
import math
import sys

import numpy as np


def path_modes(k):
    lap = np.diag([1.0] + [2.0] * (k - 2) + [1.0]) - np.eye(k, k=1) - np.eye(k, k=-1)
    vals, vecs = np.linalg.eigh(lap)
    vals[0] = 0.0
    return vals, vecs.T  # vecs.T[a] is the a-th unit eigenvector


def spectral_m(k, scale=1.0):
    vals, u = path_modes(k)
    mu = scale * (vals[:, None] + vals[None, :])
    w = np.zeros_like(mu)
    w[mu > 1e-12] = 1.0 / mu[mu > 1e-12] ** 2
    d = u[:, 1:] - u[:, :-1]                 # d[a, i] = u_a(i+1) - u_a(i), i = 0..k-2
    return (d ** 2).T @ w @ (u ** 2)          # [i, j]: M of the edge (i,j)-(i+1,j)


def direct(k):
    n = k * k
    idx = lambda i, j: i * k + j
    lap = np.zeros((n, n))
    edges = []
    for i in range(k):
        for j in range(k):
            for di, dj in ((1, 0), (0, 1)):
                if i + di < k and j + dj < k:
                    a, b = idx(i, j), idx(i + di, j + dj)
                    lap[a, a] += 1; lap[b, b] += 1; lap[a, b] -= 1; lap[b, a] -= 1
                    edges.append((a, b, di))
    pinv = np.linalg.pinv(lap)
    m = np.zeros((k - 1, k))
    wmax = 0.0
    for a, b, di in edges:
        w = pinv[:, a] - pinv[:, b]
        wmax = max(wmax, np.abs(w).max())
        if di == 1:
            m[a // k, a % k] = w @ w
    return m, wmax


def main():
    ks = [8, 16, 32, 64, 128]
    ok = True
    print('k  mean  ln(k)/pi^4  max  (pi^3/16)ln(k)+6  frac_good  m/(2U)  route_gap  |w|max')
    for k in ks:
        m = spectral_m(k)
        mean, mx = m.mean(), m.max()
        lo, hi = math.log(k) / math.pi ** 4, math.pi ** 3 / 16 * math.log(k) + 6.0
        frac = (m >= math.log(k) / (2 * math.pi ** 4)).mean()
        gap, wmax = float('nan'), float('nan')
        if k <= 32:
            md, wmax = direct(k)
            gap = np.abs(md - m).max()
            ok &= gap < 1e-9 and wmax <= 1 + 1e-12
        ok &= mean >= lo and mx <= hi and frac >= mean / (2 * mx)
        print(f'{k} {mean:.4f} {lo:.4f} {mx:.4f} {hi:.4f} {frac:.4f} {mean / (2 * mx):.4f} {gap:.2e} {wmax:.6f}')
    planted = spectral_m(128, scale=4.0).mean()
    seen = planted < math.log(128) / math.pi ** 4
    print(f'positive control: planted mean at k=128 {planted:.4f} against {math.log(128) / math.pi ** 4:.4f}: '
          f'{"failed (i) as it must" if seen else "PASSED (i): control blind"}')
    ok &= seen
    print('ALL CHECKS PASS' if ok else 'A CHECK FAILED')
    return 0 if ok else 1


if __name__ == '__main__':
    sys.exit(main())
