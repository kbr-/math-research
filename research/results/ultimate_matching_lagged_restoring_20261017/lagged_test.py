#!/usr/bin/env python3
"""The lagged greedy restoring flow of the ultimate-matching notebook (queue item restoring-drift-construction, the
next attempt of the restoring drift entry) and its per-point tails.

Construction. The dyadic flow is built by level_step of
research/results/ultimate_matching_simultaneous_rule_20261017/simultaneous_rule_test.py, imported unchanged (rule
off). After the step of level j >= 1 (which uses the counts of level j+1), the level-j squares are paired inside
their level-(j-1) parents: in coordinate 1 the two vertically stacked level-j squares of each column of a parent,
in coordinate 2 the two horizontally adjacent ones of each row. Each pair gets the circulation of unit amplitude
of research/results/ultimate_matching_restoring_drift_20261017/drift_test.py's drift_step at the parent's level
(a mean shift +1 on one square and -1 on the other, carried by 2 tent profiles and the return leg 4 S (C s)),
times an amplitude a chosen by damped Newton descent on the quartic cost sum (F_1 + a phi_1)^4 + (F_2 + a phi_2)^4
of the running field over the pair's positions, both coordinates, so the leg of lem:sibling-exchange-leg is paid
for in the choice. Coordinate 1's pairs are corrected first, then coordinate 2's on the corrected field; each
descent does not raise its pair's quartic cost. The correction moves flux across the shared side of two level-j
squares, so it changes their means; thm:square-mean-flow-obstruction asks that "every step Phi_j with j >= j_1
has on every level-j square S the mean of the dyadic step", which the correction breaks when assigned to step j,
and assigned to step j-1 it would use the counts of level j+1, which that step may not; other decompositions of
the field into steps are not excluded.

Statement tested (Prediction): for J = 6 and 7, in each coordinate, the lagged flow's per-point exceedance
fractions are below the dyadic flow's at every threshold, in both normalizations (each position standardized by
its own mean and spread over the seeds, at t = 2.2 and 3.3, as ex:simultaneous-rule-exceedances; and the dyadic
flow's analytic spread, at t = 2.5, 3.0, 3.5), and the ratio to the dyadic flow at the largest threshold is below
the ratio at the smallest (a tail lighter than the dyadic flow's, lighter farther out).
Refuted by: a ratio of at least 1 at some threshold, or a ratio at the largest threshold above the ratio at the
smallest, in some coordinate, size and normalization.
Possible because: the paired restoring drift of the same circulations, chosen by a cubic rule, made the tails
heavier (ex:paired-restoring-drift-tails), and later levels add noise the descent cannot foresee.

Control: amplitude forced to 0 gives the dyadic field exactly (largest relative difference printed).
Refuted by: a relative difference above 1e-9 of the field's scale with the amplitude forced to 0.
Possible because: the pairing and reshaping code could change the field even with a zero amplitude.
Control: every pair's quartic cost after its descent is at most its cost before (largest relative rise printed).
Refuted by: a relative rise above 1e-9 in any pair, level, coordinate or seed.
Possible because: an undamped Newton step on a convex quartic can overshoot.
Control: global averages of the lagged and the dyadic fields agree (the correction has zero mean on each parent).
Refuted by: a difference above 1e-9 of the scale.
Possible because: a return leg that does not close inside its parent leaks a net flux.
Forced by counts: the zero-amplitude control is forced by the formula and tests only the routine; the cost control
is forced by the damping and tests its code; the global average is forced by the parent means up to the cumulative
matrix's end term; none forces the Prediction's fractions.
Positive control: the planted field sign(D)|D|^0.8 of the dyadic values over their analytic spread, a fixed lighter
law, has analytic-normalization ratios below 1 decreasing in t, as the Prediction requires of the lagged flow.
Refuted by: a planted ratio at 3.5 not below its ratio at 2.5, or at least 1 at 2.5.

Baseline: Gaussian fractions 0.0278 at 2.2, 0.000967 at 3.3 (two-sided), 0.0124 at 2.5, 0.00270 at 3.0, 0.000465
at 3.5; ex:simultaneous-rule-exceedances gives a rule keeping square means at 0.245 to 0.364 of the dyadic
flow's fractions at 3.3 under the per-position standardization with 512 seeds (a difference at two sizes, its
change with J undecided); ex:paired-restoring-drift-tails gives the paired drift at 45.6 and more at 3.5.
Record checked: these were read for whether together they decide the fractions, and none does:
thm:square-mean-flow-obstruction (quoted above, its hypothesis broken by the natural assignment),
lem:sibling-exchange-leg (prices the legs), ex:greedy-circulation-tails, ex:simultaneous-rule-exceedances,
ex:paired-restoring-drift-tails, thm:linear-flow-obstruction (whose class is "every linear flow rule W").
Decisive at these sizes: for ratios at t <= 3.5 standard deviations at J = 6, 7 only, against the spread over
seed halves printed; not for the tails at sqrt(log N) standard deviations nor the cost's limit in N.
Parallel use: seeds run in 14 processes, one thread each; two passes (spreads, then counts).
"""
import argparse
import importlib.util
import json
import math
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve()
RULE = HERE.parents[1] / 'ultimate_matching_simultaneous_rule_20261017' / 'simultaneous_rule_test.py'
_spec = importlib.util.spec_from_file_location('simultaneous_rule_test', RULE)
sr = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(sr)

T_SELF = (2.2, 3.3)
T_ANA = (2.5, 3.0, 3.5)


def unit_shapes(m):
    """For a parent of side 2m positions with level-j children of side m: phi_main (2, m, m) [yb, yy, xx] and
    phi_other (2, m, m) of the coordinate-1 exchange (+1 on the bottom child, -1 on the top), as drift_step."""
    u = (np.arange(m) + 0.5) / m
    T = sr.tent(u)
    S = np.where(u < 0.5, -2.0, 2.0)
    C = sr.cumulative(2 * m, False)
    s = np.concatenate([np.ones(m), -np.ones(m)])
    c = C @ s                                                        # (2m,) over y in the parent column
    main = 2.0 * np.concatenate([np.ones(m), -np.ones(m)])[:, None] * T[None, :]
    other = 4.0 * c[:, None] * S[None, :]
    return main.reshape(2, m, m), other.reshape(2, m, m)


def descend(A, B, pa, pb, iters=30):
    """Amplitudes a (P,) minimizing sum (A + a pa)^4 + (B + a pb)^4 over the last three axes, damped Newton from 0;
    returns a and the largest relative cost rise (expected 0)."""
    # The cost is the quartic polynomial sum_k c_k a^k in a; its coefficients are summed once over the positions.
    ax = (1, 2, 3)
    c = [((A ** 4).sum(axis=ax) + (B ** 4).sum(axis=ax)),
         4 * ((A ** 3 * pa).sum(axis=ax) + (B ** 3 * pb).sum(axis=ax)),
         6 * ((A ** 2 * pa ** 2).sum(axis=ax) + (B ** 2 * pb ** 2).sum(axis=ax)),
         4 * ((A * pa ** 3).sum(axis=ax) + (B * pb ** 3).sum(axis=ax)),
         float((pa ** 4).sum() + (pb ** 4).sum()) * np.ones(A.shape[0])]
    cost = lambda a: c[0] + a * (c[1] + a * (c[2] + a * (c[3] + a * c[4])))
    a = np.zeros(A.shape[0])
    cur = c[0].copy()
    for _ in range(iters):                                           # damped Newton on scalars
        g = c[1] + a * (2 * c[2] + a * (3 * c[3] + a * 4 * c[4]))
        h = 2 * c[2] + a * (6 * c[3] + a * 12 * c[4])
        step = -g / np.maximum(h, 1e-300)
        t = np.ones_like(a)
        for _ in range(40):
            bad = cost(a + t * step) > cur
            if not bad.any():
                break
            t = np.where(bad, t / 2, t)
        trial = cost(a + t * step)
        ok = trial <= cur
        a = np.where(ok, a + t * step, a)
        cur = np.where(ok, trial, cur)
    # the rise is checked on the field itself, not the polynomial
    x = A + a[:, None, None, None] * pa
    y = B + a[:, None, None, None] * pb
    after = (x ** 4).sum(axis=ax) + (y ** 4).sum(axis=ax)
    rise = float(np.max((after - c[0]) / np.maximum(c[0], 1e-300)))
    return a, rise


def lagged_step(F, j, G, stats, zero=False):
    """The lagged correction after level j (in place)."""
    if j < 1:
        return
    n = 1 << (j - 1)                 # parents per side
    m = G >> j                       # child side in positions
    main, other = unit_shapes(m)
    # coordinate 1: pairs (Y, X, xa); positions (yb, yy, xx)
    F1 = F[0].reshape(n, 2, m, n, 2, m).transpose(0, 3, 4, 1, 2, 5).reshape(-1, 2, m, m)
    F2 = F[1].reshape(n, 2, m, n, 2, m).transpose(0, 3, 4, 1, 2, 5).reshape(-1, 2, m, m)
    a, rise = descend(F1, F2, main[None], other[None])
    if zero:
        a = np.zeros_like(a)
    F1 = F1 + a[:, None, None, None] * main[None]
    F2 = F2 + a[:, None, None, None] * other[None]
    F[0] = F1.reshape(n, n, 2, 2, m, m).transpose(0, 3, 4, 1, 2, 5).reshape(G, G)
    F[1] = F2.reshape(n, n, 2, 2, m, m).transpose(0, 3, 4, 1, 2, 5).reshape(G, G)
    stats['max_cost_rise'] = max(stats.get('max_cost_rise', 0.0), rise)
    # coordinate 2: pairs (Y, yb, X); positions (xa, xx, yy): the same shapes with the axes exchanged
    G2 = F[1].reshape(n, 2, m, n, 2, m).transpose(0, 1, 3, 4, 5, 2).reshape(-1, 2, m, m)   # [P, xa, xx, yy]
    G1 = F[0].reshape(n, 2, m, n, 2, m).transpose(0, 1, 3, 4, 5, 2).reshape(-1, 2, m, m)
    a, rise = descend(G2, G1, main[None], other[None])
    if zero:
        a = np.zeros_like(a)
    G2 = G2 + a[:, None, None, None] * main[None]
    G1 = G1 + a[:, None, None, None] * other[None]
    F[1] = G2.reshape(n, 2, n, 2, m, m).transpose(0, 1, 5, 2, 3, 4).reshape(G, G)
    F[0] = G1.reshape(n, 2, n, 2, m, m).transpose(0, 1, 5, 2, 3, 4).reshape(G, G)
    stats['max_cost_rise'] = max(stats.get('max_cost_rise', 0.0), rise)


def fields(J, N, seed, zero=False):
    rng = np.random.default_rng(seed)
    cells = rng.multinomial(N, np.full(4 ** J, 4.0 ** -J)).reshape(1 << J, 1 << J)
    G = 1 << (J + 1)
    dy = np.zeros((2, G, G))
    lg = np.zeros((2, G, G))
    stats = {}
    for j in range(J):
        sr.level_step(dy, cells, j, J, G, False, stats)
        sr.level_step(lg, cells, j, J, G, False, stats)
        lagged_step(lg, j, G, stats, zero)
    return dy, lg, stats


def pass1(job):
    J, N, seeds = job
    G = 1 << (J + 1)
    sig = sr.dyadic_sigma(J, G, N)
    acc = {k: np.zeros((2, 2, G, G)) for k in ('s', 'q')}           # [flow, coord]
    ana = np.zeros((3, 2, len(T_ANA)), dtype=np.int64)               # [dyadic, lagged, planted]
    out = {'max_cost_rise': 0.0, 'global_average_diff': 0.0}
    for seed in seeds:
        dy, lg, st = fields(J, N, seed)
        out['max_cost_rise'] = max(out['max_cost_rise'], st.get('max_cost_rise', 0.0))
        scale = float(dy.std())
        out['global_average_diff'] = max(out['global_average_diff'],
                                         max(abs(float(lg[k].mean() - dy[k].mean())) / scale for k in range(2)))
        for f, x in enumerate((dy, lg)):
            acc['s'][f] += x
            acc['q'][f] += x * x
        zd = dy / sig
        ana += exceed(np.stack([zd, lg / sig, np.sign(zd) * np.abs(zd) ** 0.8]), T_ANA)
    return acc['s'], acc['q'], ana, out


def exceed(z, ts):
    """Counts of |z| > t over the last two axes, for every leading index and every threshold t."""
    return (np.abs(z)[..., None, :, :] > np.asarray(ts)[:, None, None]).sum(axis=(-2, -1))


def pass2(job):
    J, N, seeds, mean, sd = job
    per = {}
    for seed in seeds:
        dy, lg, _ = fields(J, N, seed)
        per[seed] = exceed((np.stack([dy, lg]) - mean) / sd, T_SELF)
    return per


def main():
    p = argparse.ArgumentParser(description=__doc__.split('\n\n')[0])
    p.add_argument('--levels', type=int, nargs='+', default=[6, 7])
    p.add_argument('--per-cell', type=int, default=16)
    p.add_argument('--seeds', type=int, default=512)
    p.add_argument('--out', required=True)
    a = p.parse_args()
    J0 = a.levels[0]
    dy0, lg0, _ = fields(J0, a.per_cell * 4 ** J0, 777, zero=True)
    c0 = float(np.abs(dy0 - lg0).max() / dy0.std())
    print(json.dumps({'control_zero_amplitude_max_rel_diff': c0}), flush=True)
    summary = []
    with ProcessPoolExecutor(max_workers=14) as pool:
        for J in a.levels:
            N = a.per_cell * 4 ** J
            seeds = list(range(1, a.seeds + 1))
            chunks = [seeds[i::14] for i in range(14)]
            r1 = list(pool.map(pass1, [(J, N, c) for c in chunks]))
            S = sum(r[0] for r in r1)
            Q = sum(r[1] for r in r1)
            ana = sum(r[2] for r in r1)
            mean = S / a.seeds
            sd = np.sqrt(np.maximum(Q / a.seeds - mean ** 2, 1e-300))
            jobs2 = [(J, N, c, mean, sd) for c in chunks]
            per = {}
            for r in pool.map(pass2, jobs2):
                per.update(r)
            cnt = sum(per.values())
            half = a.seeds // 2
            rh = [sum(per[s] for s in seeds[:half]), sum(per[s] for s in seeds[half:])]
            npos = a.seeds * (1 << (J + 1)) ** 2
            e = {'J': J, 'positions': npos,
                 'max_cost_rise': max(r[3]['max_cost_rise'] for r in r1),
                 'global_average_diff': max(r[3]['global_average_diff'] for r in r1),
                 'self_dyadic_fraction': (cnt[0] / npos).tolist(),
                 'self_ratio': (cnt[1] / np.maximum(cnt[0], 1)).tolist(),
                 'self_ratio_half_spread': (np.abs(rh[0][1] / np.maximum(rh[0][0], 1) -
                                                   rh[1][1] / np.maximum(rh[1][0], 1)) / 2).tolist(),
                 'analytic_dyadic_fraction': (ana[0] / npos).tolist(),
                 'analytic_ratio': (ana[1] / np.maximum(ana[0], 1)).tolist(),
                 'planted_ratio': (ana[2] / np.maximum(ana[0], 1)).tolist(),
                 'variance_ratio': [float((sd[1, k] ** 2).mean() / (sd[0, k] ** 2).mean()) for k in range(2)]}
            summary.append(e)
            print(json.dumps(e), flush=True)
    ok = lambda r: all(x < 1 for x in r) and r[-1] < r[0]
    verdict = {'prediction': all(ok(e['self_ratio'][k]) and ok(e['analytic_ratio'][k])
                                 for e in summary for k in range(2)),
               'control_zero_amplitude': c0 <= 1e-9,
               'control_cost_rise': all(e['max_cost_rise'] <= 1e-9 for e in summary),
               'control_global_average': all(e['global_average_diff'] <= 1e-9 for e in summary),
               'positive_control': all(ok(e['planted_ratio'][k]) for e in summary for k in range(2))}
    print(json.dumps(verdict), flush=True)
    Path(a.out).write_text(json.dumps({'summary': summary, 'verdict': verdict}, indent=1))


if __name__ == '__main__':
    main()
