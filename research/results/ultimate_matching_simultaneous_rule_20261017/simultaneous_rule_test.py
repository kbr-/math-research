#!/usr/bin/env python3
"""The item two-choice-routing of the ultimate-matching notebook, its next attempt from the sequential rules
entry: the simultaneous rule, which chooses each square's vertical and horizontal crossing profiles together,
with both compensations, to minimize the quartic load of both coordinates over the square given the coarser
field, level by level from the coarsest.

Model, that of research/results/ultimate_matching_water_filling_20261017/water_filling_test.py (the dyadic
flow of the adaptive circulation entry): on a level-j square of side rho, tent(t) = 2 min(t, 1-t),
  coordinate 2 gets (phibar + psi(t1)) tent(t2) - tent'(t1) Psi(t2),
  coordinate 1 gets (phibar1_b + chi(t2)) tent(t1) - tent'(t2) Phi(t1) on half b,
with phibar = -E_0/rho, phibar1_b = -2 d_b/rho, psi of zero mean over t1, chi of zero mean over each half,
Phi(t1) = int_0^t1 psi, Psi(t2) = int over the half of chi (point-centred sums, step 1/m). The dyadic flow is
psi = chi = 0. The rule minimizes sum over the square's m x m points of F1^4 + F2^4, F the running field with
the square's step added, over (psi, chi): a convex quartic in the linear variables, solved by Newton's method on
the KKT system of the three zero-mean constraints, from psi = chi = 0.

Hand step, written before the script (the entry's Smallest case and its two-level follow-up): at one square the
gradient at the dyadic choice is nonzero when d_0 != d_1; its equalizing direction Phi proportional to
tent(t1)(d_0 - d_1) makes psi constant on each half, and on the children the coarser loads then stay separable,
so a flow built from that direction alone stays linear in the counts; only the quartic optimum's nonlinearity
can depart from Gaussian per-point tails, which is what this run measures.

Statement tested (the sequential rules entry's Prediction, committed there before this script): the rule's
per-position standardized kurtosis stays at a constant offset from the dyadic flow's at J = 6..8 with no trend
in J; refuted if the gap grows by more than 0.15 from the smallest to the largest J, beyond twice the seed spread.

Expectations, written before any run.
- Control 1 (the optimizer lowers each square's cost): at every square of every level the rule's cost is at
  most the dyadic choice's from the same running field, up to 1e-9 relative.
  Refuted by: a printed largest relative increase above 1e-9.
  Possible because: a sign error in the gradient or in the compensation makes Newton climb.
  Tried where it must fail first: the script also evaluates the negated Newton step on the first level with
  d_0 != d_1 and prints whether it raises the cost; that line must read True.
- Control 2 (corrections have zero square averages): the rule's global average equals the dyadic flow's in
  each coordinate, relative difference below 1e-9.
  Refuted by: a printed relative global-average difference above 1e-9.
  Possible because: Phi or Psi may not close to zero at the far side of a square or half.
- Positive control (the rule acts): the per-coordinate variance ratio rule/dyadic differs from 1 by more than
  1e-6 at every size, since the gradient at the dyadic choice is nonzero wherever d_0 != d_1.
  Refuted by: a printed variance ratio within 1e-6 of 1 at some size.
  Possible because: the Newton step may be zero by an indexing error, as the levelling control of the
  water-filling run was constant by construction.
- Prediction: |g(Jmax) - g(Jmin)| <= 0.15 in both coordinates, g = kurtosis(dyadic) - kurtosis(rule) per
  position, pooled over 8 seeds.
  Refuted by: g(Jmax) - g(Jmin) > 0.15 in some coordinate, beyond twice the half-sample seed spread.
  Possible because: the quartic optimum is nonlinear in the counts and its departures at one level change the
  loads every finer level reads, so they could compound.
Baseline: the dyadic flow's per-position kurtosis was 2.88-3.11 and 2.96-3.06 at J = 6..9 (water-filling
run), and thm:dyadic-flow-obstruction proves its per-point obstruction; a greedy pyramid circulation by the
same cost gave a constant offset of 0.2-0.3 (ex:greedy-circulation-tails); neither decides this rule.
Record checked: these were read for whether they decide the rule's trend, and none does: lem:sequential-rules-dyadic,
ex:greedy-circulation-tails, thm:dyadic-flow-obstruction and lem:straight-cut-forced-flux.
Decisive at these sizes: only for a gap growing by more than 0.15 from J = 6 to 8; the run prints the
half-sample seed spread at each size, and a growth smaller than twice it is reported as not decided.
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


def counts_at(cells, j, J):
    f = 1 << (J - j)
    n = 1 << j
    return cells.reshape(n, f, n, f).sum(axis=(1, 3))


def excesses(cells, j, J):
    c = counts_at(cells, j + 1, J).astype(float)
    n = 1 << j
    ch = c.reshape(n, 2, n, 2)                           # [Y, b, X, a]
    parent = ch.sum(axis=(1, 3))
    e = ch - parent[:, None, :, None] / 4.0
    E = e.sum(axis=3)
    d = (e[:, :, :, 0] - e[:, :, :, 1]) / 2.0
    return E[:, 0, :], d


def cumulative(m, halves):
    """C (m x m): (C v)_i = (sum_{k<i} v_k + v_i/2)/m, restarting at each half when halves is True."""
    C = np.zeros((m, m))
    seg = m // 2 if halves else m
    for s in range(0, m, seg):
        for i in range(seg):
            C[s + i, s:s + i] = 1.0 / m
            C[s + i, s + i] = 0.5 / m
    return C


def level_step(F, cells, j, J, G, rule, stats):
    n = 1 << j
    m = G >> j
    rho = 1.0 / n
    E0, d = excesses(cells, j, J)
    u = (np.arange(m) + 0.5) / m
    T = tent(u)
    S = np.where(u < 0.5, -2.0, 2.0)                      # -tent'(u)
    half = m // 2
    # squares as a batch: (n*n, m, m) indexed [square, y, x]
    F1 = F[0].reshape(n, m, n, m).transpose(0, 2, 1, 3).reshape(n * n, m, m)
    F2 = F[1].reshape(n, m, n, m).transpose(0, 2, 1, 3).reshape(n * n, m, m)
    phibar = (-E0 / rho).reshape(n * n)
    db = np.concatenate([np.repeat(d[:, 0:1, :], half, axis=1), np.repeat(d[:, 1:2, :], half, axis=1)], axis=1)
    phibar1 = (-2.0 * db / rho).transpose(0, 2, 1).reshape(n * n, m)          # per square, per row y
    B1 = F1 + phibar1[:, :, None] * T[None, None, :]
    B2 = F2 + phibar[:, None, None] * T[None, :, None]
    if rule and m >= 2:
        Cm = cumulative(m, False)
        Ch = cumulative(m, True)
        K = B1.shape[0]
        psi = np.zeros((K, m))
        chi = np.zeros((K, m))

        def fields(psi, chi):
            Phi = psi @ Cm.T                                  # (K, m) over x
            Psi = chi @ Ch.T                                  # (K, m) over y
            f1 = B1 + chi[:, :, None] * T[None, None, :] + S[None, :, None] * Phi[:, None, :]
            f2 = B2 + psi[:, None, :] * T[None, :, None] + S[None, None, :] * Psi[:, :, None]
            return f1, f2

        def cost(psi, chi):
            f1, f2 = fields(psi, chi)
            return (f1 ** 4).sum(axis=(1, 2)) + (f2 ** 4).sum(axis=(1, 2))

        base = cost(psi, chi)
        E = np.zeros((3, 2 * m))
        E[0, :m] = 1.0
        E[1, m:m + half] = 1.0
        E[2, m + half:] = 1.0
        scale = max(float(np.abs(B1).max()), float(np.abs(B2).max()), 1.0)
        first_step = None
        for it in range(30):
            f1, f2 = fields(psi, chi)
            g1, g2 = 4 * f1 ** 3, 4 * f2 ** 3
            w1, w2 = 12 * f1 ** 2, 12 * f2 ** 2
            gpsi = np.einsum('kyx,y->kx', g2, T) + np.einsum('kyx,y->kx', g1, S) @ Cm
            gchi = np.einsum('kyx,x->ky', g1, T) + np.einsum('kyx,x->ky', g2, S) @ Ch
            dpp = np.einsum('kyx,y->kx', w2, T * T)
            a1 = np.einsum('kyx,y->kx', w1, S * S)
            Hpp = dpp[:, :, None] * np.eye(m)[None] + np.einsum('xa,kx,xb->kab', Cm, a1, Cm, optimize=True)
            dcc = np.einsum('kyx,x->ky', w1, T * T)
            a2 = np.einsum('kyx,x->ky', w2, S * S)
            Hcc = dcc[:, :, None] * np.eye(m)[None] + np.einsum('ya,ky,yb->kab', Ch, a2, Ch, optimize=True)
            # cross: F2 couples psi_x (via T(y)) with chi (via S(x) Psi(y)); F1 couples chi_y (via T(x)) with
            # psi (via S(y) Phi(x))
            M2 = np.einsum('kyx,y,x,yb->kxb', w2, T, S, Ch, optimize=True)
            N1 = np.einsum('kyx,x,y,xa->kay', w1, T, S, Cm, optimize=True)
            Hpc = M2 + N1
            H = np.zeros((K, 2 * m + 3, 2 * m + 3))
            H[:, :m, :m] = Hpp
            H[:, m:2 * m, m:2 * m] = Hcc
            H[:, :m, m:2 * m] = Hpc
            H[:, m:2 * m, :m] = Hpc.transpose(0, 2, 1)
            H[:, :2 * m, :2 * m] += 1e-12 * scale ** 2 * np.eye(2 * m)[None]
            H[:, 2 * m:, :2 * m] = E[None]
            H[:, :2 * m, 2 * m:] = E.T[None]
            rhs = np.zeros((K, 2 * m + 3))
            rhs[:, :m] = -gpsi
            rhs[:, m:2 * m] = -gchi
            rhs[:, 2 * m:] = -np.stack([psi.sum(1), chi[:, :half].sum(1), chi[:, half:].sum(1)], axis=1)
            step = np.linalg.solve(H, rhs[:, :, None])[:, :, 0]
            if first_step is None:
                first_step = step.copy()
            # damped Newton: halve until the cost does not rise
            t = np.ones(K)
            c0 = cost(psi, chi)
            for _ in range(20):
                cand = cost(psi + t[:, None] * step[:, :m], chi + t[:, None] * step[:, m:2 * m])
                bad = cand > c0 * (1 + 1e-12) + 1e-300
                if not bad.any():
                    break
                t = np.where(bad, t / 2, t)
            psi = psi + t[:, None] * step[:, :m]
            chi = chi + t[:, None] * step[:, m:2 * m]
            if np.abs(step).max() * t.max() < 1e-12 * scale:
                break
        final = cost(psi, chi)
        stats['control1_max_rel_increase'] = max(stats.get('control1_max_rel_increase', 0.0),
                                                 float(((final - base) / np.maximum(base, 1e-300)).max()))
        if 'negated_step_raises_cost' not in stats and j >= 1:
            neg = cost(-first_step[:, :m], -first_step[:, m:2 * m])
            moved = np.abs(first_step).max(axis=1) > 1e-9 * scale
            if moved.any():
                stats['negated_step_raises_cost'] = bool((neg[moved] > base[moved]).all())
        f1, f2 = fields(psi, chi)
    else:
        f1, f2 = B1, B2
    F[0] = f1.reshape(n, n, m, m).transpose(0, 2, 1, 3).reshape(G, G)
    F[1] = f2.reshape(n, n, m, m).transpose(0, 2, 1, 3).reshape(G, G)


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


def run(job):
    J, N, seed = job
    t0 = time.time()
    rng = np.random.default_rng(seed)
    cells = rng.multinomial(N, np.full(4 ** J, 4.0 ** -J)).reshape(1 << J, 1 << J)
    G = 1 << (J + 1)
    dy = np.zeros((2, G, G))
    sr = np.zeros((2, G, G))
    stats = {}
    for j in range(J):
        level_step(dy, cells, j, J, G, False, stats)
        level_step(sr, cells, j, J, G, True, stats)
    scale = float(dy.std())
    out = {'J': J, 'N': N, 'seed': seed, **stats,
           'control2_global_average_rel_diff': max(abs(float(sr[k].mean() - dy[k].mean())) for k in range(2)) / scale,
           'variance_rule_over_dyadic': [float(sr[k].var() / dy[k].var()) for k in range(2)],
           'seconds': time.time() - t0}
    sigma = dyadic_sigma(J, G, N)
    return out, dy / sigma, sr / sigma


def main():
    p = argparse.ArgumentParser(description=__doc__.split('\n\n')[0])
    p.add_argument('--levels', type=int, nargs='+', default=[6, 7, 8])
    p.add_argument('--per-cell', type=int, default=16)
    p.add_argument('--seeds', type=int, nargs='+', default=[1, 2, 3, 4, 5, 6, 7, 8])
    p.add_argument('--out', required=True)
    a = p.parse_args()
    jobs = [(J, a.per_cell * 4 ** J, s) for J in a.levels for s in a.seeds]
    with ProcessPoolExecutor(max_workers=min(8, len(a.seeds))) as pool:
        results = list(pool.map(run, jobs))
    runs, by = [], {}
    for r, dz, sz in results:
        runs.append(r)
        print(json.dumps(r), flush=True)
        by.setdefault(r['J'], []).append((dz, sz))
    pooled = []
    for J in a.levels:
        dzs = [x for x, _ in by[J]]
        szs = [y for _, y in by[J]]
        h = len(dzs) // 2
        e = {'J': J, 'kurtosis_dyadic': [kurtosis(dzs, k) for k in range(2)],
             'kurtosis_rule': [kurtosis(szs, k) for k in range(2)]}
        e['gap'] = [e['kurtosis_dyadic'][k] - e['kurtosis_rule'][k] for k in range(2)]
        halves = [[kurtosis(dzs[:h], k) - kurtosis(szs[:h], k), kurtosis(dzs[h:], k) - kurtosis(szs[h:], k)]
                  for k in range(2)]
        e['gap_seed_spread'] = [abs(x[0] - x[1]) for x in halves]
        pooled.append(e)
        print(json.dumps(e), flush=True)
    lo, hi = pooled[0], pooled[-1]
    growth = [hi['gap'][k] - lo['gap'][k] for k in range(2)]
    noise = [2.0 * max(lo['gap_seed_spread'][k], hi['gap_seed_spread'][k]) for k in range(2)]
    verdict = {'gap_growth': growth, 'twice_seed_spread': noise,
               'prediction_holds': all(abs(x) <= 0.15 for x in growth),
               'refuted_growing_gap': any(growth[k] > 0.15 and growth[k] > noise[k] for k in range(2))}
    print(json.dumps(verdict), flush=True)
    with open(a.out, 'w') as fh:
        json.dump({'per_cell': a.per_cell, 'pooled': pooled, 'verdict': verdict, 'runs': runs}, fh, indent=1)


if __name__ == '__main__':
    main()
