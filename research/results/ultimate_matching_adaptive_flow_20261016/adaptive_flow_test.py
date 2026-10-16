#!/usr/bin/env python3
"""Decisive test of the first route review of the ultimate-matching notebook: does a greedy adaptive
circulation make the per-point values of the dyadic Ajtai-Komlos-Tusnady flow lighter than Gaussian?

Model. N points i.i.d. uniform on [0,1]^2, counted in the dyadic cells of level J (multinomial). The
dyadic flow is the sum over levels j < J of the square flows of the notebook's dyadic flow bound
entry: on a square of side rho with child excesses e_{a,b} (a horizontal, b vertical half),
  coordinate 2: v = -2 E_0 t2/rho for t2 < 1/2, v = -E_0/rho - 2 E_1 (t2 - 1/2)/rho otherwise,
  coordinate 1 (on the half b containing the point): k = -4 d_{0,b} t1/rho for t1 < 1/2,
              k = -4 d_{0,b} (1 - t1)/rho otherwise,
with E_b = e_{0,b} + e_{1,b}, d_{0,b} = (e_{0,b} - e_{1,b})/2, t the relative position. The adaptive
flow adds, on every square at every level, c * curl(pyramid): coordinate 1 gets +c on the bottom
triangle and -c on the top one, coordinate 2 gets -c on the left triangle and +c on the right one
(divergence-free, zero normal flux on the square's boundary). The scalar c is chosen greedily, level
by level from the coarsest, to minimize the sum over the square's evaluation points of
(A_1 + D_1 + c s_1)^4 + (A_2 + D_2 + c s_2)^4, A the field of the coarser levels (with their
circulations), D this level's dyadic part: a quartic proxy for the (4,4) exponential cost.
Evaluation points: the centres of a grid of side 2^-(J+1) (four per finest cell).

Statement tested (the review's decisive test, a hypothesis about one construction): the greedy
circulation flow's standardized per-point values have tails lighter than Gaussian (kurtosis below 3
and a log-tail slope against t^2 steeper than -1/2 at 3 to 4 standard deviations), while the dyadic
flow's are Gaussian.

Expectations, written before the main run. An exploratory smoke run at J = 5 (not kept) showed that
three controls as first written were misstated, not that the flow was wrong; they were corrected
before this script was committed: a single realization's coarse levels carry only a few random
coefficients, so the variance control is per level and at deep levels only; the flux row lies a
fixed fraction of the finest squares below their top edges, which leaves a term of order
2^(-J/2) sqrt N; and a circulation on a square shifts its children's averages, so only the average
over the whole unit square is invariant.
- Control 1 (implementation of the dyadic flow): at every level j >= 4, the empirical per-point
  variance of the level-j field, divided by N times the mean of the coefficient weight over the
  evaluation positions (w_1 = 2 min(t1, 1-t1)^2, w_2 = min(t2, 1-t2)^2, from the dyadic flow
  obstruction entry), lies in [0.85, 1.15].
  Refuted by: a printed per-level ratio outside [0.85, 1.15] at some level j >= 4, at some size.
  Possible because: a sign, scaling or half-selection error in the square-flow formulas changes the
  per-level variance.
- Control 2 (flux, a check against the raw counts): the integral of coordinate 2 of the dyadic flow
  along the evaluation row just below y = 1/2 equals, in absolute value, |count in the bottom half
  - N/2| up to the deeper levels' contribution along that row, of order 0.6 * 2^(-J/2) sqrt N:
  the printed error over sqrt N is at most 1.5 * 2^(-J/2).
  Refuted by: a printed flux error above 1.5 * 2^(-J/2) sqrt N at some size.
  Possible because: the vertical-part formula or its orientation may be wrong.
- Control 3 (circulation keeps the global average): the average of the greedy flow over the unit
  square equals the dyadic flow's, up to floating-point error, since every circulation has zero mean
  over its own square and hence over the unit square.
  Refuted by: a difference above 1e-9 relative to the field scale.
  Possible because: an indexing error in applying the circulation.
Second run (after the entry's review, expectations written before it). The first run's greedy flow
had a discretization defect: evaluation points on the square's diagonals were assigned by argmin to
the left/right triangles, so the sampled circulation acted mostly on coordinate 2; diagonal points now
get 0 in both coordinates (the continuous curl gives the diagonals measure zero). The first run's
dyadic kurtosis above 3 is explained (reviewer) by the per-position variance sigma^2(x) = N sum_j
w(t_j(x)) varying with x, a scale mixture over positions with kurtosis about 3(1 + 0.8/J).
- Prediction for the dyadic flow, raw pooled kurtosis: within 0.12 of 3(1 + 0.8/J) in each coordinate.
  Refuted by: a raw pooled dyadic kurtosis further than 0.12 from 3(1 + 0.8/J) at some size.
  Possible because: the finest levels' discretized weights and the coarse levels' few coefficients
  change the mixture.
- Prediction for the dyadic flow divided by its analytic per-position sigma: kurtosis in [2.85, 3.15]
  and log-tail slope in [-0.6, -0.4] at every size.
  Refuted by: a per-position standardized dyadic kurtosis outside [2.85, 3.15] or slope outside
  [-0.6, -0.4] at some size.
  Possible because: per realization the coarse levels carry few coefficients, which could leave
  non-Gaussian structure.
- The greedy flow, divided by the same dyadic sigma(x): lighter tails would show as kurtosis below
  2.85 and slope steeper than -0.6 with the gap growing in J; Gaussian as values inside the dyadic
  bands. A variance moved between coordinates in the corrected run would point to another asymmetry.
  Refuted by: either outcome refutes the other branch.
  Possible because: the greedy circulation is a nonlinear, data-dependent correction.

All shape statistics are computed on the per-point values pooled over the seeds of one size (eight
by default), which estimates the per-point law; a single realization's coarse levels carry too few
random coefficients for its own empirical shape to mean anything.
- Prediction for the dyadic flow: kurtosis within 3 +- 0.15 and log-tail slope against t^2 near -1/2
  (between -0.6 and -0.4), at every size.
  Refuted by: a kurtosis outside [2.85, 3.15] or a slope outside [-0.6, -0.4] for the dyadic flow.
  Possible because: the per-point value is a finite sum of non-Gaussian level terms; at small J the
  shape could deviate.
- Prediction for the greedy flow (the hypothesis under test; no expectation about which way it goes):
  lighter tails would show as kurtosis below 2.85 and slope steeper than -0.6, with the gap growing
  with J; Gaussian tails as values within the dyadic flow's bands.
  Refuted by: either outcome refutes the other branch; the run is decisive at these sizes only if the
  dyadic flow's own values sit inside its bands.
  Possible because: the greedy circulation is a nonlinear, data-dependent correction.
"""
import argparse
import json
import math
import time

import numpy as np


def tiles(a, j):
    """View a (G, G) array as (4^j, (G/2^j)^2): rows are the level-j squares, columns their points."""
    g = a.shape[0]
    m = g >> j
    return a.reshape(1 << j, m, 1 << j, m).transpose(0, 2, 1, 3).reshape(1 << (2 * j), m * m)


def untile(t, j, g):
    m = g >> j
    return t.reshape(1 << j, 1 << j, m, m).transpose(0, 2, 1, 3).reshape(g, g)


def counts_at(cells, j, J):
    """Counts of the level-j squares from the level-J cell counts (array indexed [y, x])."""
    f = 1 << (J - j)
    n = 1 << j
    return cells.reshape(n, f, n, f).sum(axis=(1, 3))


def level_fields(cells, j, J, G):
    """The dyadic flow's level-j field (both coordinates) at the evaluation points, shape (2, G, G)."""
    c = counts_at(cells, j + 1, J).astype(float)        # children counts, indexed [y, x]
    n = 1 << j
    ch = c.reshape(n, 2, n, 2)                           # [Y, b, X, a]
    parent = ch.sum(axis=(1, 3))
    e = ch - parent[:, None, :, None] / 4.0              # e[Y, b, X, a]
    E = e.sum(axis=3)                                    # E[Y, b, X]
    d0 = (e[:, :, :, 0] - e[:, :, :, 1]) / 2.0           # d_{0,b}[Y, b, X]
    rho = 1.0 / n
    m = G >> j
    u = (np.arange(m) + 0.5) / m                         # relative positions within a square
    T2 = u.reshape(1, m, 1, 1)                           # arrays are indexed [Y, y within, X, x within]
    T1 = u.reshape(1, 1, 1, m)
    E0 = E[:, 0, :][:, None, :, None]                    # [Y, 1, X, 1]
    E1 = E[:, 1, :][:, None, :, None]
    v = np.where(T2 < 0.5, -2.0 * E0 * T2 / rho, -E0 / rho - 2.0 * E1 * (T2 - 0.5) / rho)
    D0 = np.where(T2 < 0.5, d0[:, 0, :][:, None, :, None], d0[:, 1, :][:, None, :, None])
    k = np.where(T1 < 0.5, -4.0 * D0 * T1 / rho, -4.0 * D0 * (1.0 - T1) / rho)
    f1 = np.broadcast_to(k, (n, m, n, m)).reshape(G, G)
    f2 = np.broadcast_to(v, (n, m, n, m)).reshape(G, G)
    return f1, f2


def circulation_pattern(m):
    """s1, s2 on an m x m block (index [y, x]): curl of the pyramid min(t1, 1-t1, t2, 1-t2)."""
    u = (np.arange(m) + 0.5) / m
    t1 = u[None, :]
    t2 = u[:, None]
    dist = np.stack(np.broadcast_arrays(t1, 1 - t1, t2, 1 - t2))
    side = np.argmin(dist, axis=0)                       # 0 left, 1 right, 2 bottom, 3 top
    tie = (dist == dist.min(axis=0)).sum(axis=0) > 1    # points on a diagonal: measure zero, value 0
    s1 = np.where(tie, 0.0, np.where(side == 2, 1.0, np.where(side == 3, -1.0, 0.0)))
    s2 = np.where(tie, 0.0, np.where(side == 0, -1.0, np.where(side == 1, 1.0, 0.0)))
    return s1, s2


def greedy_c(u1, u2, s1, s2, iters=40):
    """Per square (rows), the c minimizing sum (u1 + c s1)^4 + (u2 + c s2)^4 (Newton on a convex quartic)."""
    c = np.zeros(u1.shape[0])
    for _ in range(iters):
        w1 = u1 + c[:, None] * s1[None, :]
        w2 = u2 + c[:, None] * s2[None, :]
        g = (s1[None, :] * w1 ** 3).sum(1) + (s2[None, :] * w2 ** 3).sum(1)
        h = 3.0 * ((s1[None, :] ** 2) * w1 ** 2).sum(1) + 3.0 * ((s2[None, :] ** 2) * w2 ** 2).sum(1)
        step = np.where(h > 0, g / np.maximum(h, 1e-300), 0.0)
        c = c - step
    return c


def shape(z):
    z = z.ravel()
    z = z / z.std()
    kurt = float(np.mean(z ** 4))
    ts = np.array([2.0, 2.5, 3.0, 3.5, 4.0])
    tails = np.array([float(np.mean(np.abs(z) > t)) for t in ts])
    ok = tails > 0
    slope = float(np.polyfit(ts[ok] ** 2, np.log(tails[ok]), 1)[0]) if ok.sum() >= 2 else float('nan')
    gauss = np.array([math.erfc(t / math.sqrt(2)) for t in ts])
    return {'kurtosis': kurt, 'tail_t': ts.tolist(), 'tail': tails.tolist(), 'gauss_tail': gauss.tolist(),
            'slope_vs_t2': slope}


def run(J, N, seed):
    rng = np.random.default_rng(seed)
    cells = rng.multinomial(N, np.full(4 ** J, 4.0 ** -J)).reshape(1 << J, 1 << J)
    G = 1 << (J + 1)
    dy = np.zeros((2, G, G))
    ad = np.zeros((2, G, G))
    level_ratio = []
    for j in range(J):
        f1, f2 = level_fields(cells, j, J, G)
        if j >= 4:
            m = G >> j
            t = (np.arange(m) + 0.5) / m
            w1 = float(np.mean(2.0 * np.minimum(t, 1 - t) ** 2))
            w2 = float(np.mean(np.minimum(t, 1 - t) ** 2))
            level_ratio.append([j, float(f1.var() / (N * w1)), float(f2.var() / (N * w2))])
        dy[0] += f1
        dy[1] += f2
        m = G >> j
        s1, s2 = circulation_pattern(m)
        s1, s2 = s1.ravel(), s2.ravel()
        u1 = tiles(ad[0] + f1, j)
        u2 = tiles(ad[1] + f2, j)
        c = greedy_c(u1, u2, s1, s2)
        ad[0] = untile(u1 + c[:, None] * s1[None, :], j, G)
        ad[1] = untile(u2 + c[:, None] * s2[None, :], j, G)
    # controls
    row = G // 2 - 1                                      # the evaluation row just below y = 1/2
    flux = float(dy[1][row].mean())                      # integral over x of coordinate 2 along the row
    bottom = float(cells[: (1 << J) // 2].sum())
    flux_err = abs(abs(flux) - abs(bottom - N / 2.0)) / math.sqrt(N)
    avg_diff = max(abs(float(ad[k].mean() - dy[k].mean())) for k in range(2))
    avg_rel = avg_diff / float(dy.std())
    sigma = dyadic_sigma(J, G, N)
    return {
        'J': J, 'N': N, 'seed': seed, 'points': G * G,
        'control_variance_ratio': level_ratio,
        'control_flux_error_over_sqrtN': flux_err, 'flux_bound_over_sqrtN': 1.5 * 2.0 ** (-J / 2),
        'flux': flux, 'bottom_excess': bottom - N / 2.0,
        'control_square_average_rel_diff': avg_rel,
        'variance_greedy_over_dyadic': [float(ad[k].var() / dy[k].var()) for k in range(2)],
    }, dy / math.sqrt(N * J), ad / math.sqrt(N * J), dy / sigma, ad / sigma


def dyadic_sigma(J, G, N):
    """The dyadic flow's per-position standard deviation, sqrt(N sum_j w_k(t_j(x))), shape (2, G, G):
    w_1 = 2 min(t1, 1-t1)^2 along x and w_2 = min(t2, 1-t2)^2 along y (dyadic flow obstruction entry)."""
    s2 = np.zeros((2, G, G))
    for j in range(J):
        m = G >> j
        t = (np.arange(m) + 0.5) / m
        w = np.tile(np.minimum(t, 1 - t) ** 2, 1 << j)
        s2[0] += N * 2.0 * w[None, :]
        s2[1] += N * w[:, None]
    return np.sqrt(s2)


def pooled_shapes(arrs):
    """Shape statistics of each coordinate, pooled over the seeds' per-point values."""
    return [shape(np.concatenate([x[k].ravel() for x in arrs])) for k in range(2)]


def report_lines(entry):
    return [f'J={entry["J"]} pooled {name} coord {k + 1}: kurtosis {s["kurtosis"]:.3f} slope '
            f'{s["slope_vs_t2"]:.3f} tails {["%.2e" % x for x in s["tail"]]}'
            for name in ('dyadic', 'greedy', 'dyadic_per_position', 'greedy_per_position')
            for k, s in enumerate(entry[name])]


def main():
    p = argparse.ArgumentParser(description=__doc__.split('\n\n')[0])
    p.add_argument('--levels', type=int, nargs='+', default=[6, 7, 8, 9])
    p.add_argument('--per-cell', type=int, default=16, help='expected points per finest cell')
    p.add_argument('--seeds', type=int, nargs='+', default=[1, 2, 3, 4, 5, 6, 7, 8])
    p.add_argument('--out', required=True)
    a = p.parse_args()
    results, pooled = [], []
    for J in a.levels:
        dys, ads, dzs, azs = [], [], [], []
        for seed in a.seeds:
            t0 = time.time()
            r, dy, ad, dz, az = run(J, a.per_cell * 4 ** J, seed)
            r['seconds'] = time.time() - t0
            results.append(r)
            dys.append(dy)
            ads.append(ad)
            dzs.append(dz)
            azs.append(az)
            print(json.dumps(r), flush=True)
        entry = {'J': J, 'seeds': a.seeds, 'dyadic': pooled_shapes(dys), 'greedy': pooled_shapes(ads),
                 'dyadic_per_position': pooled_shapes(dzs), 'greedy_per_position': pooled_shapes(azs),
                 'mixture_kurtosis_reference': 3.0 * (1.0 + 0.8 / J)}
        print('\n'.join(report_lines(entry)), flush=True)
        pooled.append(entry)
        with open(a.out, 'w') as fh:
            json.dump({'per_cell': a.per_cell, 'pooled': pooled, 'runs': results}, fh, indent=1)


if __name__ == '__main__':
    main()
