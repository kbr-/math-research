#!/usr/bin/env python3
"""Convex-optimal flows for the ultimate-matching notebook: does the best flow for an L^p cost keep the flow
bound's (4,4) cost bounded at a fixed constant as the number of dyadic levels grows?

Model. N = 16 * 4^J points i.i.d. uniform on [0,1]^2 counted in level-J dyadic cells; field evaluated at the
centres of a G x G grid, G = 2^(J+1). The dyadic flow D is the notebook's dyadic square flow summed over
levels (the same formulas as adaptive_flow_test.py, imported from it). Every flow with the same divergence and
zero normal flux on the boundary is D + curl psi with psi vanishing on the boundary (simply connected square);
discretely psi lives on the (G+1)^2 grid vertices, zero on the boundary, and curl psi at a centre is
(d_y psi, -d_x psi) by averaged differences. For p in (2, 4, 8) the flow Phi_p minimizes
sum_x sum_k (Phi_k(x)/s)^p over psi (s = sqrt(N J), a fixed scale), by L-BFGS, warm-started from p/2.
Phi_2 is the discrete electric (Helmholtz) projection.

Quantity. For a flow Phi, L_needed(Phi) is the least L such that, in each coordinate k, the mean over the
evaluation points of psi_4(4 |Phi_k| / (L sqrt(N log N))), psi_4(u) = exp(u^4) - 1, is at most 1/2: the
condition under which the flow bound of the dyadic flow bound entry gives the (4,4) conclusion (lambda' = N/4,
the error term aside). Found by bisection on L.

Statement tested: L_needed of the p = 8 optimal flow stays bounded (grows by less than 10% from J = 5 to
J = 8) while L_needed of the dyadic flow grows (thm:dyadic-flow-obstruction says it diverges, slowly).

Expectations, written before the run. A smoke run at J = 5, one seed (output kept under smoke/), was seen
before the range was reduced from J = 5..9 to J = 5..8 for run time and the iteration cap raised to 4000; its
values at J = 5 were therefore known when the predictions below, which concern the trend in J, were finalized.
- Control 1 (independent solver): at J = 5, the L-BFGS p = 2 optimum agrees with a direct sparse solve of its
  normal equations (scipy.sparse.linalg.spsolve) to relative error below 1e-4 in the field.
  Refuted by: a printed relative difference above 1e-4.
  Possible because: an error in the discrete curl's adjoint (the gradient) would stop L-BFGS at a non-optimum
  that the direct solve does not share.
- Control 2 (optimality): for each p the objective at the optimum is at most the objective of D itself, and
  the final gradient norm is below 1e-5 of its value at the warm start.
  Refuted by: an objective above D's, or a printed gradient ratio above 1e-5.
  Possible because: a non-convergent optimization or a sign error in the gradient.
- Prediction for the dyadic flow: L_needed increases from J = 5 to J = 8 (by at least 5%).
  Refuted by: L_needed of D not increasing by 5% over that range.
  Possible because: the divergence proved in thm:dyadic-flow-obstruction is slow, of order a power of
  log N, and may be invisible at these sizes.
- Prediction under test for the p = 8 optimum: L_needed grows by less than 10% from J = 5 to J = 8 and stays
  below the dyadic flow's at every J.
  Refuted by: an increase of 10% or more, or a value above the dyadic flow's.
  Possible because: the optimum minimizes an L^8 proxy, not the exponential cost, and the conjecture may be
  false or the flow route insufficient at (4,4).
"""
import argparse
import json
import math
import time
import pathlib
import sys

import numpy as np
from scipy.optimize import minimize
from scipy import sparse
from scipy.sparse.linalg import spsolve

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / 'ultimate_matching_adaptive_flow_20261016'))
from adaptive_flow_test import level_fields  # noqa: E402


def dyadic(cells, J):
    G = 1 << (J + 1)
    d = np.zeros((2, G, G))
    for j in range(J):
        f1, f2 = level_fields(cells, j, J, G)
        d[0] += f1
        d[1] += f2
    return d


def curl(inner, G):
    """curl of psi (vertex grid (G+1)^2, zero on the boundary, interior given) at the G x G centres."""
    psi = np.zeros((G + 1, G + 1))
    psi[1:-1, 1:-1] = inner.reshape(G - 1, G - 1)
    dy = 0.5 * ((psi[1:, :-1] + psi[1:, 1:]) - (psi[:-1, :-1] + psi[:-1, 1:]))
    dx = 0.5 * ((psi[:-1, 1:] + psi[1:, 1:]) - (psi[:-1, :-1] + psi[1:, :-1]))
    return dy, -dx


def curl_adjoint(g1, g2, G):
    """The adjoint of curl: interior vertex values of C^T (g1, g2)."""
    out = np.zeros((G + 1, G + 1))
    # g1 multiplies d_y psi
    out[1:, :-1] += 0.5 * g1
    out[1:, 1:] += 0.5 * g1
    out[:-1, :-1] -= 0.5 * g1
    out[:-1, 1:] -= 0.5 * g1
    # g2 multiplies -d_x psi
    out[:-1, 1:] -= 0.5 * g2
    out[1:, 1:] -= 0.5 * g2
    out[:-1, :-1] += 0.5 * g2
    out[1:, :-1] += 0.5 * g2
    return out[1:-1, 1:-1].ravel()


def optimize(d, p, x0, G, iters):
    def f(x):
        c1, c2 = curl(x, G)
        u1, u2 = d[0] + c1, d[1] + c2
        val = float(np.sum(u1 ** p) + np.sum(u2 ** p))
        grad = curl_adjoint(p * u1 ** (p - 1), p * u2 ** (p - 1), G)
        return val, grad
    start = np.linalg.norm(f(x0)[1])
    res = minimize(f, x0, jac=True, method='L-BFGS-B', options={'maxiter': iters, 'maxcor': 30,
                                                                  'ftol': 1e-15, 'gtol': 1e-12 * max(start, 1e-300)})
    return res.x, float(res.fun), float(np.linalg.norm(res.jac) / max(start, 1e-300)), int(res.nit)


def direct_p2(d, G):
    """Normal equations C^T C psi = -C^T d, assembled sparsely, solved directly (control 1)."""
    n = (G - 1) ** 2
    cols = []
    for idx in range(n):
        e = np.zeros(n)
        e[idx] = 1.0
        c1, c2 = curl(e, G)
        cols.append(np.concatenate([c1.ravel(), c2.ravel()]))
    C = sparse.csr_matrix(np.array(cols).T)
    rhs = -(C.T @ np.concatenate([d[0].ravel(), d[1].ravel()]))
    A = (C.T @ C).tocsc() + 1e-12 * sparse.identity(n, format='csc')   # checkerboard modes are in the kernel
    return spsolve(A, rhs)


def l_needed(phi, N):
    base = math.sqrt(N * math.log(N))
    out = []
    for k in range(2):
        a = np.abs(phi[k]).ravel() * 4.0 / base
        lo, hi = 0.05, 50.0
        for _ in range(60):
            mid = math.sqrt(lo * hi)
            cost = float(np.mean(np.expm1(np.minimum((a / mid) ** 4, 700.0))))
            lo, hi = (mid, hi) if cost > 0.5 else (lo, mid)
        out.append(hi)
    return out


def kurt(phi):
    z = phi.ravel() / phi.std()
    return float(np.mean(z ** 4))


def run(J, seed, iters, control):
    N = 16 * 4 ** J
    rng = np.random.default_rng(seed)
    cells = rng.multinomial(N, np.full(4 ** J, 4.0 ** -J)).reshape(1 << J, 1 << J)
    G = 1 << (J + 1)
    d = dyadic(cells, J)
    s = math.sqrt(N * J)
    dn = d / s
    rec = {'J': J, 'N': N, 'seed': seed, 'dyadic': {'L_needed': l_needed(d, N), 'kurtosis': [kurt(d[0]), kurt(d[1])]}}
    x = np.zeros((G - 1) ** 2)
    for p in (2, 4, 8):
        t0 = time.time()
        x, obj, gratio, nit = optimize(dn, p, x, G, iters)
        c1, c2 = curl(x, G)
        phi = np.stack([d[0] + s * c1, d[1] + s * c2])
        d_obj = float(np.sum(dn[0] ** p) + np.sum(dn[1] ** p))
        rec[f'p{p}'] = {'objective': obj, 'dyadic_objective': d_obj, 'gradient_ratio': gratio, 'iterations': nit,
                        'L_needed': l_needed(phi, N), 'kurtosis': [kurt(phi[0]), kurt(phi[1])],
                        'variance_over_dyadic': [float(phi[k].var() / d[k].var()) for k in range(2)],
                        'max_over_dyadic_std': [float(np.abs(phi[k]).max() / d[k].std()) for k in range(2)],
                        'seconds': time.time() - t0}
        if p == 2 and control:
            xd = direct_p2(dn, G)
            a1, a2 = curl(x, G)
            b1, b2 = curl(xd, G)
            num = math.sqrt(float(np.sum((a1 - b1) ** 2) + np.sum((a2 - b2) ** 2)))
            den = math.sqrt(float(np.sum((dn[0] + b1) ** 2) + np.sum((dn[1] + b2) ** 2)))
            rec['control_direct_p2_rel_diff'] = num / den
    rec['dyadic']['max_over_std'] = [float(np.abs(d[k]).max() / d[k].std()) for k in range(2)]
    return rec


def main():
    ap = argparse.ArgumentParser(description=__doc__.split('\n\n')[0])
    ap.add_argument('--levels', type=int, nargs='+', default=[5, 6, 7, 8])
    ap.add_argument('--seeds', type=int, nargs='+', default=[1, 2, 3, 4])
    ap.add_argument('--iters', type=int, default=4000)
    ap.add_argument('--out', required=True)
    a = ap.parse_args()
    runs = []
    for J in a.levels:
        for seed in a.seeds:
            r = run(J, seed, a.iters, control=(J == 5 and seed == a.seeds[0]))
            runs.append(r)
            print(json.dumps(r), flush=True)
            with open(a.out, 'w') as fh:
                json.dump({'runs': runs}, fh, indent=1)


if __name__ == '__main__':
    main()
