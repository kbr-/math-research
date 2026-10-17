"""Grid flow duality and the Raviart-Thomas cost step, checked numerically on small cell grids.

Statement tested: on the k x k cell graph (vertices the cells, edges between side-neighbours), for phi_e(t) =
A psi(|t|/B_e), psi(t) = exp(t^4) - 1 (B_e = B_1 on edges between horizontal neighbours, B_2 on vertical ones), and
any rho with sum zero,
  (a) min over flows theta with net outflow rho of sum_e phi_e(theta_e)
      = max over u of [sum_Q u_Q rho_Q - sum_e phi_e^*(u_head - u_tail)],  phi_e^*(v) = A psi^*(B_e |v| / A);
  (b) the lowest-order Raviart-Thomas field of an edge flow (first component affine in x on each cell through the two
      vertical-edge fluxes divided by delta, second affine in y), has int_Q psi(|Phi^1|/lam) + psi(|Phi^2|/lam) at most
      the edge cost delta^2 sum_e psi(|theta_e|/(delta lam)), with the boundary fluxes zero.
The primal is computed with BFGS over the circulations added to one flow of divergence rho, the dual with BFGS over u (one value
fixed, the dual being invariant under constants since sum rho = 0), psi^* by bounded scalar maximization; the two
are independent computations sharing only psi.

Expected before the run: (a) the primal minimum and the dual maximum agree to within 1e-4 relative on every grid
and draw, and (b) the field cost is at most the edge cost on every draw.
Refuted by: a relative gap above 1e-3 between the computed primal and dual values on some grid and draw.
Possible because: a sign convention (outflow against inflow, head minus tail) or the conjugate's scaling written
wrong would give unequal values, and a wrong field would violate (b).
Control: the quadratic cost psi(t) = t^2, whose minimizer is the weighted electrical flow (conductances B_e^2) and
whose dual is computed the same way; its primal must equal that flow's energy, computed by solving the weighted
Laplacian with numpy (asserted to 1e-6 relative).
Forced by counts: on a k x k grid the flows of given divergence form an affine space of dimension (k-1)^2, so the
primal has (k-1)^2 free parameters and is not forced by the constraint; the control's value is forced by linear
algebra and tests the solver and the conventions only.
Positive control: a wrong conjugate scaling, phi_e^*(v) = A psi^*(|v|) with B_e != 1, must give a visible gap on
the same draws (the script asserts it does), so the comparison can see a convention error.
Baseline: weak duality (dual <= primal) holds for every u and theta by Fenchel-Young; it decides the inequality one
way and leaves the equality, which is the statement, to the computation.
Record checked: lem:flow-matching-bound and lem:discrete-flow-bound (search "convex dual flow cost class bound
discrepancy minimal flow"): neither states the equality on the grid or the field step.
"""
import argparse
import json

import numpy as np
from scipy.linalg import null_space
from scipy.optimize import minimize, minimize_scalar


def grid_edges(k):
    edges, kinds = [], []
    for i in range(k):
        for j in range(k):
            q = i * k + j
            if j + 1 < k:
                edges.append((q, q + 1)); kinds.append(0)       # horizontal neighbours: flux in x
            if i + 1 < k:
                edges.append((q, q + k)); kinds.append(1)       # vertical neighbours: flux in y
    return np.array(edges), np.array(kinds)


def incidence(k, edges):
    """Net outflow of each cell: D @ theta, theta_e positive from tail to head."""
    D = np.zeros((k * k, len(edges)))
    for e, (a, b) in enumerate(edges):
        D[a, e] += 1.0
        D[b, e] -= 1.0
    return D


def make_psi(kind):
    if kind == 'quartic':
        return lambda t: np.expm1(np.abs(t) ** 4)
    return lambda t: np.abs(t) ** 2


def conjugate(psi, x):
    """psi^*(x) = sup_t >= 0 (x t - psi(t)) for x >= 0, by bounded scalar maximization."""
    res = minimize_scalar(lambda t: -(x * t - psi(t)), bounds=(0.0, 3.0 + x), method='bounded',
                          options={'xatol': 1e-12})
    return -res.fun


def primal(k, rho, A, B, psi):
    edges, kinds = grid_edges(k)
    D = incidence(k, edges)
    Be = np.where(kinds == 0, B[0], B[1])
    theta0 = np.linalg.lstsq(D, rho, rcond=None)[0]
    # The flows of divergence rho are theta0 + Z c, Z a basis of the circulations (the null space of D); a first
    # version minimized under the constraint with SLSQP and stopped above the minimum (the control caught it).
    Z = null_space(D)
    cost = lambda c: A * np.sum(psi((theta0 + Z @ c) / Be))
    res = minimize(cost, np.zeros(Z.shape[1]), method='BFGS', options={'gtol': 1e-12, 'maxiter': 5000})
    theta = theta0 + Z @ res.x
    assert np.allclose(D @ theta, rho, atol=1e-10)
    return float(cost(res.x)), theta


def dual(k, rho, A, B, psi, scale_conjugate=True):
    edges, kinds = grid_edges(k)
    Be = np.where(kinds == 0, B[0], B[1])

    def phistar(v, b):
        return A * conjugate(psi, (b if scale_conjugate else 1.0) * abs(v) / A)

    def neg(u_free):
        u = np.concatenate([[0.0], u_free])
        grad = u[edges[:, 1]] - u[edges[:, 0]]
        return -(u @ rho - sum(phistar(v, b) for v, b in zip(grad, Be)))

    res = minimize(neg, np.zeros(k * k - 1), method='BFGS', options={'gtol': 1e-10, 'maxiter': 5000})
    return -res.fun


def electrical_energy(k, rho, B):
    """min sum (theta_e/B_e)^2 under D theta = rho, by linear algebra: theta = C D^T u with C = diag(B_e^2) and
    D C D^T u = rho (weighted Laplacian), energy theta^T C^{-1} theta."""
    edges, kinds = grid_edges(k)
    D = incidence(k, edges)
    c = np.where(kinds == 0, B[0], B[1]) ** 2
    lap = D @ (c[:, None] * D.T)
    u = np.linalg.lstsq(lap, rho, rcond=None)[0]
    theta = c * (D.T @ u)
    return float(np.sum(theta ** 2 / c))


def field_cost(k, theta, delta, lam, psi, samples=400):
    """int over the square of psi(|Phi^1|/lam) + psi(|Phi^2|/lam) for the Raviart-Thomas field of theta."""
    edges, kinds = grid_edges(k)
    flux = {}
    for (a, b), kind, th in zip(edges, kinds, theta):
        flux[(a, b)] = th
    t = (np.arange(samples) + 0.5) / samples
    total = 0.0
    for i in range(k):
        for j in range(k):
            q = i * k + j
            left = flux.get((q - 1, q), 0.0) if j > 0 else 0.0
            right = flux.get((q, q + 1), 0.0) if j + 1 < k else 0.0
            down = flux.get((q - k, q), 0.0) if i > 0 else 0.0
            up = flux.get((q, q + k), 0.0) if i + 1 < k else 0.0
            phi1 = ((1 - t) * left + t * right) / delta      # affine in x, constant in y
            phi2 = ((1 - t) * down + t * up) / delta         # affine in y, constant in x
            total += delta ** 2 * (np.mean(psi(phi1 / lam)) + np.mean(psi(phi2 / lam)))
    edge_cost = delta ** 2 * np.sum(psi(theta / (delta * lam)))
    return total, edge_cost


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--out', required=True)
    args = parser.parse_args()
    rng = np.random.default_rng(20261017)
    rows = []
    for k in (2, 3, 4):
        for draw in range(3):
            counts = rng.poisson(4.0, size=k * k).astype(float)
            rho = (counts - counts.mean()) / 6.0          # scaled so the quartic stays moderate
            A, B = 1.0, (1.0, 1.7)
            row = {'k': k, 'draw': draw}
            for kind in ('quartic', 'quadratic'):
                psi = make_psi(kind)
                p, theta = primal(k, rho, A, B, psi)
                d = dual(k, rho, A, B, psi)
                row[kind] = {'primal': p, 'dual': d, 'relative_gap': abs(p - d) / max(abs(p), 1e-12)}
                if kind == 'quartic':
                    wrong = dual(k, rho, A, B, psi, scale_conjugate=False)
                    row['positive_control_gap'] = abs(p - wrong) / max(abs(p), 1e-12)
                    fc, ec = field_cost(k, theta, 1.0 / k, 1.0, psi)
                    row['field_cost'], row['edge_cost'] = fc, ec
                else:
                    row['electrical_energy'] = electrical_energy(k, rho, B)
                    assert abs(row['electrical_energy'] - p) <= 1e-6 * max(1.0, p), 'control: quadratic primal'
            rows.append(row)
            print(f"k={k} draw={draw}: quartic primal {row['quartic']['primal']:.8f} dual {row['quartic']['dual']:.8f} "
                  f"gap {row['quartic']['relative_gap']:.2e}; quadratic gap {row['quadratic']['relative_gap']:.2e}; "
                  f"wrong-conjugate gap {row['positive_control_gap']:.2e}; field {row['field_cost']:.6f} <= edge "
                  f"{row['edge_cost']:.6f}: {row['field_cost'] <= row['edge_cost'] + 1e-9}")
    worst = max(r['quartic']['relative_gap'] for r in rows)
    worst_q = max(r['quadratic']['relative_gap'] for r in rows)
    least_wrong = min(r['positive_control_gap'] for r in rows)
    field_ok = all(r['field_cost'] <= r['edge_cost'] + 1e-9 for r in rows)
    print(f'worst quartic gap {worst:.2e}; worst quadratic gap {worst_q:.2e}; smallest wrong-conjugate gap '
          f'{least_wrong:.2e}; field step on every draw: {field_ok}')
    assert least_wrong > 1e-2, 'positive control failed: a wrong conjugate scaling was not visible'
    with open(args.out, 'w') as handle:
        json.dump({'rows': rows, 'worst_quartic_gap': worst, 'worst_quadratic_gap': worst_q,
                   'smallest_wrong_conjugate_gap': least_wrong, 'field_step_holds': field_ok}, handle, indent=1)


if __name__ == '__main__':
    main()
