#!/usr/bin/env python3
"""The item two-choice-routing of the ultimate-matching notebook, its test reading: does a less-loaded
routing rule make the per-point values of the dyadic flow lighter than Gaussian as J grows?

Model, that of the adaptive-circulation entry (research/results/ultimate_matching_adaptive_flow_20261016):
N points i.i.d. uniform on [0,1]^2 counted in the dyadic cells of level J; the dyadic flow is the sum over
levels j < J of square flows. On a square of side rho with child excesses e_{a,b} (a horizontal, b vertical
half), E_b = e_{0,b} + e_{1,b}, d_b = (e_{0,b} - e_{1,b})/2, t the relative position, tent(t) = 2 min(t, 1-t):
  coordinate 2: v = (-E_0/rho) tent(t2)                  (moves E_0 across the mid-line t2 = 1/2),
  coordinate 1: k = (-2 d_b/rho) tent(t1) on half b     (moves d_b across t1 = 1/2 inside half b),
which is the old script's formulas rewritten (E_0 + E_1 = 0).

The rule (the continuum limit of sending each unit along the less loaded crossing edge, water-filling,
with signed loads): level by level from the coarsest, the crossing profile along each mid-line is chosen to
make the total load there constant. Vertical move: with A2(t1) the coordinate-2 field of the coarser levels
on the mid-line (mean of the two evaluation rows beside it), phi(t1) = -E_0/rho - (A2 - mean A2), so A2 + phi
is constant and the mean crossing is unchanged; v = phi(t1) tent(t2), and the divergence is kept by
k' = -tent'(t2) Phi(t1), Phi' = phi - mean phi, Phi(0) = Phi(1) = 0 (zero normal flux on the square's
boundary). Horizontal move, inside each half, the same with the roles of the coordinates exchanged, against
the coordinate-1 field of the coarser levels plus this level's vertical part. The corrections integrate to
zero over their square, so square averages, and the global average, are the dyadic flow's.

Statement tested (the Prediction of the straight-cut forced flux entry, committed there before this run):
the rule's per-position standardized kurtosis (each coordinate divided by the dyadic flow's analytic
per-position sigma(x)) stays at a constant offset from the dyadic flow's at J = 6..9, with no trend in J;
refuted if the gap grows with J, the balls-into-bins effect.

Expectations, written before any run.
- Control 1 (the rule's code reduces to the dyadic flow): with the levelling switched off (deviations set
  to zero) the field equals the old script's dyadic flow at every point, max difference below 1e-9 times the
  field's standard deviation, at J = 6, seed 1.
  Refuted by: a printed relative difference above 1e-9 between the switched-off rule and the dyadic flow.
  Possible because: an index, sign or half-selection error in rewriting the formulas changes the field.
- Control 2 (the corrections have zero square averages): the rule's global average equals the dyadic flow's
  in each coordinate, relative difference below 1e-9.
  Refuted by: a printed relative global-average difference above 1e-9 at some size and seed.
  Possible because: the cumulative profile Phi may not close to zero at the square's far side.
- Control 3 (the levelling acts, checked right after each level's vertical step): along each square's
  mid-line the total coordinate-2 load is constant, its spread over t1 below 1e-9 times the coarser load's
  spread there, at every level with m >= 4.
  Refuted by: a printed ratio above 1e-9 at some level.
  Possible because: the mid-line rows may be taken at the wrong index.
No positive control: no flow with lighter-than-Gaussian per-point values is known (one would bear on the
open conjecture), so the effect cannot be planted; Control 3 shows the levelling acts where it is applied.
- Prediction (the statement tested): the gap g(J) = kurtosis(dyadic) - kurtosis(rule), per position and
  pooled over 8 seeds, per coordinate, satisfies |g(9) - g(6)| <= 0.15 in both coordinates.
  Refuted by: g(9) - g(6) > 0.15 in some coordinate, a gap growing with J.
  Possible because: the rule is nonlinear in the counts, and where the finer crossing flux cannot level
  the coarser loads the levelling is partial, which could compound over levels.
Baseline: the dyadic flow's per-position kurtosis was 2.88-3.19 at J = 6..10 (ex:greedy-circulation-tails),
and thm:dyadic-flow-obstruction proves its per-point values Gaussian; neither decides the rule.
Record checked: these four were read for whether together they decide the rule's kurtosis trend, and
none does: ex:greedy-circulation-tails, thm:dyadic-flow-obstruction, lem:straight-cut-forced-flux and
lem:grid-flow-duality.
Power (written before the run): a balls-into-bins gain grows like a power of log N or of log log N, and
J = 6..9 spans log N from about 11 to 17, so a slow trend can be missed; a gap growing by more than 0.15
over these sizes is what the run can see, and an outcome inside the band leaves slower trends open.
Decisive at these sizes: only for a gap growing by more than 0.15 from J = 6 to 9; the run prints the
kurtosis of the two half-samples of seeds (1-4 and 5-8) at each size, whose difference measures the
spread between seeds, and a growth smaller than twice that spread is reported as not decided.
Parallel use: the seeds of one size run in separate processes, up to 8 at a time, one thread each.
"""
import argparse
import json
import math
import time
from concurrent.futures import ProcessPoolExecutor

import numpy as np


def tent(t):
    return 2.0 * np.minimum(t, 1.0 - t)


def tent_prime(t):
    return np.where(t < 0.5, 2.0, -2.0)


def counts_at(cells, j, J):
    f = 1 << (J - j)
    n = 1 << j
    return cells.reshape(n, f, n, f).sum(axis=(1, 3))


def excesses(cells, j, J):
    """E_0[Y, X] and d_b[Y, b, X] of the level-j squares."""
    c = counts_at(cells, j + 1, J).astype(float)
    n = 1 << j
    ch = c.reshape(n, 2, n, 2)                           # [Y, b, X, a]
    parent = ch.sum(axis=(1, 3))
    e = ch - parent[:, None, :, None] / 4.0
    E = e.sum(axis=3)                                    # [Y, b, X]
    d = (e[:, :, :, 0] - e[:, :, :, 1]) / 2.0            # [Y, b, X]
    return E[:, 0, :], d


def half_cumulative(dev, m, axis):
    """Phi at the point centres: the integral from the start of each half (or of the square, for the
    vertical move) of -dev, dt = 1/m; dev has zero mean over each segment, so Phi closes to zero."""
    val = -dev
    c = np.cumsum(val, axis=axis)
    return (c - 0.5 * val) / m


def level_step(F, cells, j, J, G, level):
    """Add level j of the rule (level=True) or of the dyadic flow (level=False) to F (shape (2, G, G),
    indexed [k, y, x]); returns the Control 3 ratio for this level's vertical step (or None)."""
    n = 1 << j
    m = G >> j
    rho = 1.0 / n
    E0, d = excesses(cells, j, J)
    u = (np.arange(m) + 0.5) / m
    T2 = u.reshape(1, m, 1, 1)
    T1 = u.reshape(1, 1, 1, m)
    F1 = F[0].reshape(n, m, n, m)                        # views [Y, y, X, x]
    F2 = F[1].reshape(n, m, n, m)
    # vertical move
    A2 = 0.5 * (F2[:, m // 2 - 1, :, :] + F2[:, m // 2, :, :])           # [Y, X, x]
    dev = A2 - A2.mean(axis=2, keepdims=True) if level else np.zeros_like(A2)
    phi = -E0[:, :, None] / rho - dev
    v = phi[:, None, :, :] * tent(T2)
    Phi = half_cumulative(dev, m, axis=2)
    kp = -tent_prime(T2) * Phi[:, None, :, :]
    ratio = None
    if level and m >= 4:
        after = A2 + phi                                  # the mid-line total right after the step
        spread = float(A2.std(axis=2).max())
        ratio = float(after.std(axis=2).max()) / spread if spread > 0 else 0.0
    F2 += v
    F1 += kp
    # horizontal move, inside each half
    A1 = 0.5 * (F1[:, :, :, m // 2 - 1] + F1[:, :, :, m // 2])           # [Y, y, X]
    half = m // 2
    D = np.concatenate([np.repeat(d[:, 0:1, :], half, axis=1), np.repeat(d[:, 1:2, :], half, axis=1)], axis=1)
    if level:
        dev1 = np.empty_like(A1)
        for b in (0, 1):
            seg = A1[:, b * half:(b + 1) * half, :]
            dev1[:, b * half:(b + 1) * half, :] = seg - seg.mean(axis=1, keepdims=True)
    else:
        dev1 = np.zeros_like(A1)
    phi1 = -2.0 * D / rho - dev1
    k = phi1[:, :, :, None] * tent(T1)
    Psi = np.empty_like(A1)
    for b in (0, 1):
        Psi[:, b * half:(b + 1) * half, :] = half_cumulative(dev1[:, b * half:(b + 1) * half, :], m, axis=1)
    vp = -tent_prime(T1) * Psi[:, :, :, None]
    F1 += k
    F2 += vp
    return ratio


def old_dyadic(cells, J, G):
    """The old script's dyadic flow (adaptive-circulation entry), for Control 1."""
    out = np.zeros((2, G, G))
    for j in range(J):
        c = counts_at(cells, j + 1, J).astype(float)
        n = 1 << j
        ch = c.reshape(n, 2, n, 2)
        parent = ch.sum(axis=(1, 3))
        e = ch - parent[:, None, :, None] / 4.0
        E = e.sum(axis=3)
        d0 = (e[:, :, :, 0] - e[:, :, :, 1]) / 2.0
        rho = 1.0 / n
        m = G >> j
        u = (np.arange(m) + 0.5) / m
        T2 = u.reshape(1, m, 1, 1)
        T1 = u.reshape(1, 1, 1, m)
        E0 = E[:, 0, :][:, None, :, None]
        E1 = E[:, 1, :][:, None, :, None]
        v = np.where(T2 < 0.5, -2.0 * E0 * T2 / rho, -E0 / rho - 2.0 * E1 * (T2 - 0.5) / rho)
        D0 = np.where(T2 < 0.5, d0[:, 0, :][:, None, :, None], d0[:, 1, :][:, None, :, None])
        k = np.where(T1 < 0.5, -4.0 * D0 * T1 / rho, -4.0 * D0 * (1.0 - T1) / rho)
        out[0] += np.broadcast_to(k, (n, m, n, m)).reshape(G, G)
        out[1] += np.broadcast_to(v, (n, m, n, m)).reshape(G, G)
    return out


def dyadic_sigma(J, G, N):
    s2 = np.zeros((2, G, G))
    for j in range(J):
        m = G >> j
        t = (np.arange(m) + 0.5) / m
        w = np.tile(np.minimum(t, 1 - t) ** 2, 1 << j)
        s2[0] += N * 2.0 * w[None, :]
        s2[1] += N * w[:, None]
    return np.sqrt(s2)


def kurtosis(arrs, k):
    z = np.concatenate([a[k].ravel() for a in arrs])
    z = z / z.std()
    return float(np.mean(z ** 4))


def run(J, N, seed, control1=False):
    rng = np.random.default_rng(seed)
    cells = rng.multinomial(N, np.full(4 ** J, 4.0 ** -J)).reshape(1 << J, 1 << J)
    G = 1 << (J + 1)
    dy = np.zeros((2, G, G))
    wf = np.zeros((2, G, G))
    ratios = []
    for j in range(J):
        level_step(dy, cells, j, J, G, level=False)
        r = level_step(wf, cells, j, J, G, level=True)
        if r is not None:
            ratios.append([j, r])
    out = {'J': J, 'N': N, 'seed': seed, 'control3_ratios': ratios,
           'control3_max': max((r for _, r in ratios), default=0.0)}
    scale = float(dy.std())
    out['control2_global_average_rel_diff'] = max(abs(float(wf[k].mean() - dy[k].mean())) for k in range(2)) / scale
    if control1:
        out['control1_rel_diff'] = float(np.abs(dy - old_dyadic(cells, J, G)).max()) / scale
    out['variance_rule_over_dyadic'] = [float(wf[k].var() / dy[k].var()) for k in range(2)]
    sigma = dyadic_sigma(J, G, N)
    return out, dy / sigma, wf / sigma


def timed_run(job):
    J, N, seed, control1 = job
    t0 = time.time()
    r, dz, wz = run(J, N, seed, control1=control1)
    r['seconds'] = time.time() - t0
    return r, dz, wz


def main():
    p = argparse.ArgumentParser(description=__doc__.split('\n\n')[0])
    p.add_argument('--levels', type=int, nargs='+', default=[6, 7, 8, 9])
    p.add_argument('--per-cell', type=int, default=16)
    p.add_argument('--seeds', type=int, nargs='+', default=[1, 2, 3, 4, 5, 6, 7, 8])
    p.add_argument('--out', required=True)
    a = p.parse_args()
    runs, pooled = [], []
    jobs = [(J, a.per_cell * 4 ** J, seed, J == a.levels[0] and seed == a.seeds[0]) for J in a.levels for seed in a.seeds]
    with ProcessPoolExecutor(max_workers=min(8, len(a.seeds))) as pool:
        results = list(pool.map(timed_run, jobs))
    by_level = {}
    for r, dz, wz in results:
        runs.append(r)
        print(json.dumps(r), flush=True)
        by_level.setdefault(r['J'], []).append((dz, wz))
    for J in a.levels:
        dzs = [dz for dz, _ in by_level[J]]
        wzs = [wz for _, wz in by_level[J]]
        h = len(dzs) // 2
        entry = {'J': J, 'kurtosis_dyadic': [kurtosis(dzs, k) for k in range(2)],
                 'kurtosis_rule': [kurtosis(wzs, k) for k in range(2)]}
        entry['gap'] = [entry['kurtosis_dyadic'][k] - entry['kurtosis_rule'][k] for k in range(2)]
        halves = [[kurtosis(d[:h], k) - kurtosis(w[:h], k), kurtosis(d[h:], k) - kurtosis(w[h:], k)]
                  for k in range(2) for d, w in [(dzs, wzs)]]
        entry['gap_half_samples'] = halves
        entry['gap_seed_spread'] = [abs(x[0] - x[1]) for x in halves]
        print(json.dumps(entry), flush=True)
        pooled.append(entry)
        g = {e['J']: e['gap'] for e in pooled}
        verdict = None
        if 6 in g and 9 in g:
            growth = [g[9][k] - g[6][k] for k in range(2)]
            spread = {e['J']: e['gap_seed_spread'] for e in pooled}
            noise = [2.0 * max(spread[6][k], spread[9][k]) for k in range(2)]
            verdict = {'gap_growth_9_minus_6': growth, 'twice_seed_spread': noise,
                       'prediction_holds': all(abs(x) <= 0.15 for x in growth),
                       'refuted_growing_gap': any(x > 0.15 for x in growth),
                       'decided': [abs(growth[k]) > noise[k] or abs(growth[k]) <= 0.15 for k in range(2)]}
        with open(a.out, 'w') as fh:
            json.dump({'per_cell': a.per_cell, 'pooled': pooled, 'verdict': verdict, 'runs': runs}, fh, indent=1)
        if verdict:
            print(json.dumps(verdict), flush=True)


if __name__ == '__main__':
    main()
