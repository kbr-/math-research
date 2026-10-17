#!/usr/bin/env python3
"""The restoring-drift flow of the ultimate-matching notebook (queue item restoring-drift-construction, picked by
the user): the dyadic flow built level by level, with after each level a divergence-free correction that moves
flux between sibling squares against the cube of their running means, and its per-point tails.

Construction. The dyadic flow is built by level_step of
research/results/ultimate_matching_simultaneous_rule_20261017/simultaneous_rule_test.py, imported unchanged (rule
off). After the step of level j, for coordinate 1, the two vertically stacked children (level j+1, side h
positions) of each level-j square in each x-half have running coordinate-1 means R_b, R_t; with sigma the dyadic
flow's analytic per-position standard deviation (dyadic_sigma, its final value) averaged over the child,
r = R/sigma and d(r) = sign(r) min(kappa |r|^3, |r|), kappa = c ln(J)/J, the children get mean shifts
m_b = -(D_b - (D_b + D_t)/2), m_t = -(D_t - (D_b + D_t)/2), D = sigma d(r): sum zero. The shift is carried by
w_1 = 2 m tent(x_loc) on each child (mean m, zero on its left and right sides) and the return flow
w_2 = 4 S(x_loc) (C m)(y) on the parent's column, C the cumulative matrix of the record's script, S = -tent', so
div w = 0 to the record's discretization and w has zero mean on every parent square. Coordinate 2 likewise with
horizontally adjacent children. The correction changes the means of the level-(j+1) squares, so the step means
are not the dyadic ones and thm:square-mean-flow-obstruction's hypothesis fails for it; it is nonlinear in the
counts, so thm:linear-flow-obstruction does not apply.

Statement tested (Prediction): at c = 2, for J = 6 and 7, in each coordinate, the fraction of positions with
|F|/sigma > t, pooled over 64 seeds, is below 0.3 of the dyadic flow's at t = 3.5 and its ratio to the dyadic
flow's decreases from t = 2.5 to t = 3.5 (a tail lighter than the dyadic flow's Gaussian one, growing lighter
farther out).
Refuted by: a ratio of at least 0.3 at t = 3.5, or a ratio at 3.5 above the ratio at 2.5, in some coordinate and J.
Possible because: the drift acts on square means while the cost is pointwise, and the return flows add loads of
their own in the other coordinate; either can leave the per-point tail Gaussian or heavier.

Control: c = 0 gives the dyadic flow exactly (largest absolute difference of the fields printed, expected 0).
Refuted by: a nonzero difference larger than 1e-9 times the field's scale at c = 0 in any seed.
Possible because: the correction code could act even with a zero drift if its pairing or return flow were wrong.
Control: the corrected field has zero mean over every level-0 square, as the dyadic flow (global averages equal).
Refuted by: a global-average difference above 1e-9 of the scale between the drift flow and the dyadic flow.
Possible because: a return flow that does not close inside its parent leaks a net flux.
Control: the dyadic fractions are within a factor 1.5 of the Gaussian erfc(t/sqrt 2) at t = 2.5, 3.0, 3.5.
Refuted by: a dyadic fraction outside a factor 1.5 of the Gaussian value at one of these t.
Possible because: positions of one seed are correlated and the analytic sigma is the dyadic flow's own.
Positive control: the planted field sign(D)|D|^0.8 (D the dyadic values over sigma), a fixed lighter law, has
ratios to the dyadic below 1 decreasing in t, as the Prediction requires of the drift flow.
Refuted by: a planted ratio at 3.5 not below the planted ratio at 2.5.
Possible because: a pooled fraction from correlated positions could be too noisy at 3.5 to order the ratios.

Baseline: Gaussian fractions erfc(t/sqrt 2): 0.0124 at 2.5, 0.00270 at 3.0, 0.000465 at 3.5; with
64 seeds of 4^(J+1) positions (262,144 at J = 6, 1,048,576 at J = 7) the dyadic counts at 3.5 are about 122 and
488, Poisson spreads of 9% and 4.5% if positions were independent (they are not: the spread over seed halves is
printed). Recorded rules: ex:simultaneous-rule-exceedances gave ratios 0.245-0.364 at 3.3 for a rule keeping
square means.
Record checked: these were read and none decides the fractions of a rule that changes square means:
ex:greedy-circulation-tails, ex:simultaneous-rule-tails, ex:simultaneous-rule-exceedances,
thm:square-mean-flow-obstruction, thm:linear-flow-obstruction, lem:equalized-flow-separable.
Decisive at these sizes: only for the per-point fractions at t <= 3.5 at J = 6, 7, against the seed-half spread
printed; it does not decide the tails at sqrt(log N) standard deviations, nor the cost's limit in N.
Parallel use: seeds run in 14 processes, one thread each.
"""
import argparse
import importlib.util
import json
import math
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

import numpy as np

RULE = Path(__file__).resolve().parents[1] / 'ultimate_matching_simultaneous_rule_20261017' / 'simultaneous_rule_test.py'
_spec = importlib.util.spec_from_file_location('simultaneous_rule_test', RULE)
sr = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(sr)

THRESHOLDS = (2.5, 3.0, 3.5)
CS = (0.0, 0.5, 2.0, 8.0)


def drift(r, kappa):
    a = np.abs(r)
    return np.sign(r) * np.minimum(kappa * a ** 3, a)


def drift_step(F, sig, j, G, kappa):
    """Add the restoring correction after level j (in place)."""
    m = G >> j
    h = m // 2
    if h < 1:
        return
    n = 1 << j
    u = (np.arange(h) + 0.5) / h
    T = sr.tent(u)
    S = np.where(u < 0.5, -2.0, 2.0)
    C = sr.cumulative(2 * h, False)
    # [Y, yb, yy, X, xa, xx]
    A1 = F[0].reshape(n, 2, h, n, 2, h)
    A2 = F[1].reshape(n, 2, h, n, 2, h)
    s1 = sig[0].reshape(n, 2, h, n, 2, h).mean(axis=(2, 5))
    s2 = sig[1].reshape(n, 2, h, n, 2, h).mean(axis=(2, 5))
    D1 = s1 * drift(A1.mean(axis=(2, 5)) / s1, kappa)                # [Y, yb, X, xa]
    D2 = s2 * drift(A2.mean(axis=(2, 5)) / s2, kappa)
    m1 = -(D1 - D1.mean(axis=1, keepdims=True))                       # vertical siblings (over yb)
    m2 = -(D2 - D2.mean(axis=3, keepdims=True))                       # horizontal siblings (over xa)
    # coordinate 1: shift on children, return flow in coordinate 2 along each parent column
    w1 = 2.0 * m1[:, :, None, :, :, None] * T[None, None, None, None, None, :]
    v1 = np.repeat(m1, h, axis=1)                                     # [Y, (yb yy), X, xa]
    c1 = np.einsum('ab,YbXx->YaXx', C, v1)
    w2r = 4.0 * c1[:, :, :, :, None] * S[None, None, None, None, :]   # [Y, (yb yy), X, xa, xx]
    # coordinate 2: shift on children, return flow in coordinate 1 along each parent row
    w2 = 2.0 * m2[:, :, None, :, :, None] * T[None, None, :, None, None, None]
    v2 = np.repeat(m2, h, axis=3)                                     # [Y, yb, X, (xa xx)]
    c2 = np.einsum('ab,YyXb->YyXa', C, v2)
    w1r = 4.0 * c2[:, :, None, :, :] * S[None, None, :, None, None]   # [Y, yb, yy, X, (xa xx)]
    F[0] += w1.reshape(G, G) + w1r.reshape(G, G)
    F[1] += w2.reshape(G, G) + w2r.reshape(G, G)


def counts(z):
    return [[int((np.abs(z[k]) > t).sum()) for t in THRESHOLDS] for k in range(2)]


def run(job):
    J, N, seed = job
    rng = np.random.default_rng(seed)
    cells = rng.multinomial(N, np.full(4 ** J, 4.0 ** -J)).reshape(1 << J, 1 << J)
    G = 1 << (J + 1)
    sig = sr.dyadic_sigma(J, G, N)
    fields = {c: np.zeros((2, G, G)) for c in CS}
    stats = {}
    kap = {c: c * math.log(J) / J for c in CS}
    for j in range(J):
        for c in CS:
            sr.level_step(fields[c], cells, j, J, G, False, stats)
            if c > 0:
                drift_step(fields[c], sig, j, G, kap[c])
    dy = fields[0.0]
    scale = float(dy.std())
    out = {'J': J, 'seed': seed, 'positions': int(G * G)}
    out['control_global_average_diff'] = max(abs(float(fields[c][k].mean() - dy[k].mean())) / scale
                                             for c in CS for k in range(2))
    zd = dy / sig
    out['counts'] = {str(c): counts(fields[c] / sig) for c in CS}
    out['counts']['planted'] = counts(np.sign(zd) * np.abs(zd) ** 0.8)
    out['variance_ratio'] = {str(c): [float(fields[c][k].var() / dy[k].var()) for k in range(2)] for c in CS}
    return out


def main():
    p = argparse.ArgumentParser(description=__doc__.split('\n\n')[0])
    p.add_argument('--levels', type=int, nargs='+', default=[6, 7])
    p.add_argument('--per-cell', type=int, default=16)
    p.add_argument('--seeds', type=int, default=64)
    p.add_argument('--out', required=True)
    a = p.parse_args()
    # Control: c = 0 must give the dyadic field; checked directly on one seed by building it with drift_step at
    # kappa = 0, which must change nothing.
    J0 = a.levels[0]
    rng = np.random.default_rng(12345)
    cells = rng.multinomial(a.per_cell * 4 ** J0, np.full(4 ** J0, 4.0 ** -J0)).reshape(1 << J0, 1 << J0)
    G0 = 1 << (J0 + 1)
    sig0 = sr.dyadic_sigma(J0, G0, a.per_cell * 4 ** J0)
    f_a, f_b = np.zeros((2, G0, G0)), np.zeros((2, G0, G0))
    for j in range(J0):
        sr.level_step(f_a, cells, j, J0, G0, False, {})
        sr.level_step(f_b, cells, j, J0, G0, False, {})
        drift_step(f_b, sig0, j, G0, 0.0)
    c0 = float(np.abs(f_a - f_b).max() / f_a.std())
    print(json.dumps({'control_kappa0_max_rel_diff': c0}), flush=True)
    jobs = [(J, a.per_cell * 4 ** J, s) for J in a.levels for s in range(1, a.seeds + 1)]
    with ProcessPoolExecutor(max_workers=14) as pool:
        runs = list(pool.map(run, jobs))
    gauss = [math.erfc(t / math.sqrt(2)) for t in THRESHOLDS]
    summary = []
    for J in a.levels:
        rs = [r for r in runs if r['J'] == J]
        npos = sum(r['positions'] for r in rs)
        half = len(rs) // 2
        e = {'J': J, 'positions': npos, 'gaussian': gauss,
             'global_average_diff_max': max(r['control_global_average_diff'] for r in rs)}
        keys = [str(c) for c in CS] + ['planted']
        tot = {k: np.sum([r['counts'][k] for r in rs], axis=0) for k in keys}
        e['dyadic_fraction'] = (tot['0.0'] / npos).tolist()
        for k in keys[1:]:
            e[f'ratio_{k}'] = (tot[k] / np.maximum(tot['0.0'], 1)).tolist()
            hs = [np.sum([r['counts'][k] for r in rs[i:i + half]], axis=0) /
                  np.maximum(np.sum([r['counts']['0.0'] for r in rs[i:i + half]], axis=0), 1) for i in (0, half)]
            e[f'ratio_{k}_half_spread'] = (np.abs(hs[0] - hs[1]) / 2).tolist()
        e['variance_ratio_mean'] = {str(c): np.mean([r['variance_ratio'][str(c)] for r in rs], axis=0).tolist()
                                    for c in CS}
        summary.append(e)
        print(json.dumps(e), flush=True)
    verdict = {'prediction': all(
        e['ratio_2.0'][k][2] < 0.3 and e['ratio_2.0'][k][2] < e['ratio_2.0'][k][0] for e in summary for k in range(2)),
        'control_dyadic_gaussian': all(
            1 / 1.5 <= e['dyadic_fraction'][k][i] / gauss[i] <= 1.5 for e in summary for k in range(2)
            for i in range(3)),
        'positive_control': all(e['ratio_planted'][k][2] < e['ratio_planted'][k][0] for e in summary
                                for k in range(2)),
        'control_kappa0': c0 <= 1e-9,
        'control_global_average': all(e['global_average_diff_max'] <= 1e-9 for e in summary)}
    print(json.dumps(verdict), flush=True)
    Path(a.out).write_text(json.dumps({'summary': summary, 'verdict': verdict, 'runs': runs}, indent=1))


if __name__ == '__main__':
    main()
