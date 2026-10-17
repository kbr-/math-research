#!/usr/bin/env python3
"""The restoring flow of the ultimate-matching notebook, built as an existence check (user, 17 October 2026: "Build
it. What if you are wrong....."): the dyadic flow corrected, after the step of each level j, by exchanges that fully
restore the running field's means between sibling squares of level i = j - r0 (shift r0), and its per-point tails.

Construction. The dyadic flow is built by level_step of
research/results/ultimate_matching_simultaneous_rule_20261017/simultaneous_rule_test.py (rule off), imported
unchanged. After the step of level j, for i = j - r0 >= 1, the level-i squares are paired inside their level-(i-1)
parents as in research/results/ultimate_matching_lagged_restoring_20261017/lagged_test.py (coordinate 1: the two
vertically stacked squares of each column of a parent; coordinate 2: the two horizontally adjacent squares of each
row) and each pair gets that file's unit circulation (unit_shapes: mean +1 on one square, -1 on the other, its leg
in the other coordinate) times a = -gain * R / 2, R the difference of the pair's running means in the exchanged
coordinate, so the difference becomes (1 - gain) R: gain 1 is full restoration, the drift d(R) = R of
lem:restoring-drift-tail's form. Coordinate 1's pairs first, then coordinate 2's on the corrected field. The
amplitudes read only the running field, which is measurable with respect to the counts of levels at most j + 1.

Statement tested (Prediction), the oscillation entry's heuristic (#entry-2026-10-17-oscillation-chain: restorations
that read square means cannot see the diagonal oscillations, which in this split order enter coordinate 1): at
J = 6, 7, 8, r0 = 1, 2 and gains 0.25 and 0.1 (gain 1 is unstable: the correction grows by a factor 2 to 3 per
level, gain_growth.txt and smoke_gain1.txt, seen before this prediction was written; the smoke run's tails were
at gain 1 and J = 6 only), in coordinate 1, the restored flow's exceedance fraction at the largest threshold of
each normalization is at least 0.7 times the dyadic flow's (self: 3.8; analytic: 4.0), and the ratio at J = 8 is not
below the ratio at J = 6 by more than twice the bootstrap spread.
Refuted by: a coordinate-1 ratio below 0.7 at the largest threshold, or a coordinate-1 ratio falling from J = 6 to
J = 8 by more than twice the bootstrap spread, at some r0 and normalization.
Possible because: the exchanges move flux across the shared side of two squares, which changes the field at points
inside them, and their legs could cancel the diagonal oscillations where the means are large; the heuristic is
unproved.
Reported, not predicted: coordinate 2, the variance ratio, and kurtosis.

Control: gain 0 gives the dyadic field exactly (largest relative difference printed).
Refuted by: a relative difference above 1e-12 of the field's scale with gain 0.
Possible because: the reshapes could change the field even at a zero amplitude.
Control: the correction w = restored - dyadic is divergence-free with zero normal flux, in weak form: for five
smooth g, |sum w . grad g| / sum |w| |grad g| below 1e-6 (the recorded lagged check gave exactly 0).
Refuted by: a weak-form ratio at or above 1e-6 for some g at J = 6, seed 1, r0 = 1.
Possible because: a leg on the wrong axis or with the wrong sign leaves a net divergence.
Positive control: the same correction with every exchange's leg negated gives a ratio above 1e-2 for some g (the
recorded flipped-leg ratios reached 0.10031).
Refuted by: every flipped-leg ratio at or below 1e-2.
Control: restoration works: the mean differences R of the pairs restored after the last step, recomputed on the
final field before the next step's noise, are at most 1e-9 of their scale for gain 1 (printed).
Refuted by: a recomputed difference above 1e-9 of the scale.
Possible because: the second coordinate's legs change the first coordinate's means if the shapes overlap wrongly.
Positive control: the planted field sign(D)|D|^0.8 of the dyadic values over their analytic spread, a fixed lighter
law, has analytic ratios below 1 and decreasing in t.
Refuted by: a planted ratio at 4.0 not below its ratio at 2.5.
Forced by counts: the gain-0 and restoration controls are forced by formulas and test the code; the divergence
control's value is fixed by the shapes, not the counts; nothing forces the Prediction's ratios.

Baseline: Gaussian two-sided fractions 0.0278 at 2.2, 0.000967 at 3.3, 0.000145 at 3.8, 0.0124 at 2.5, 0.00270 at
3.0, 0.000465 at 3.5, 0.0000633 at 4.0; ex:lagged-restoring-tails gave the lagged flow ratios below 1 at J = 6, 7 up
to 3.5 standard deviations, and cor:lagged-flow-obstruction proves that design fails in the limit, so lighter tails
at these sizes do not by themselves decide the limit.
Record checked: thm:linear-flow-obstruction (linear rules; this rule is nonlinear through R), cor:lagged-flow-
obstruction and cor:coarse-mean-growing-shift (fields that keep coarse means at fixed shifts; this one changes them),
lem:conditional-push-obstruction, ex:lagged-restoring-tails, ex:paired-restoring-drift-tails: none decides the
fractions at these sizes.
Decisive at these sizes: only for ratios up to 4 standard deviations at J = 6, 7, 8 against the bootstrap spread
printed; not for tails at sqrt(log N) standard deviations or for the cost's limit in N; the tenth review's Decision
says no computation at reachable sizes bears on the shift threshold, so the run is an existence check of the
construction and a test of the heuristic's coordinate-1 prediction at these sizes only.
Parallel use: seeds run in 14 processes, one thread each; two passes (spreads, then counts per seed).
"""
import argparse
import importlib.util
import json
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve()
_spec = importlib.util.spec_from_file_location(
    'lagged_test', HERE.parents[1] / 'ultimate_matching_lagged_restoring_20261017' / 'lagged_test.py')
lt = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(lt)
sr = lt.sr

T_SELF = (2.2, 3.3, 3.8)
T_ANA = (2.5, 3.0, 3.5, 4.0)
# (shift r0, gain): gain 1 grows by a factor 2 to 3 per level (smoke_gain1.txt, gain_growth.txt), so the test
# runs at the stable gains 0.25 and 0.1.
CONFIGS = ((1, 0.25), (2, 0.25), (1, 0.1), (2, 0.1))
LEG_SIGN = [1.0]                     # -1 for the flipped-leg positive control


def restore_step(F, i, G, gain, stats=None):
    """Full (gain 1) restoration of the running means of sibling level-i squares, in place."""
    if i < 1:
        return
    n = 1 << (i - 1)
    m = G >> i
    main, other = lt.unit_shapes(m)
    other = LEG_SIGN[0] * other
    # coordinate 1: pairs [P, yb, yy, xx], main +1 on yb = 0
    F1 = F[0].reshape(n, 2, m, n, 2, m).transpose(0, 3, 4, 1, 2, 5).reshape(-1, 2, m, m)
    F2 = F[1].reshape(n, 2, m, n, 2, m).transpose(0, 3, 4, 1, 2, 5).reshape(-1, 2, m, m)
    R = F1[:, 0].mean(axis=(1, 2)) - F1[:, 1].mean(axis=(1, 2))
    a = -gain * R / 2
    F1 = F1 + a[:, None, None, None] * main[None]
    F2 = F2 + a[:, None, None, None] * other[None]
    F[0] = F1.reshape(n, n, 2, 2, m, m).transpose(0, 3, 4, 1, 2, 5).reshape(G, G)
    F[1] = F2.reshape(n, n, 2, 2, m, m).transpose(0, 3, 4, 1, 2, 5).reshape(G, G)
    # coordinate 2: pairs [P, xa, xx, yy], main +1 on xa = 0
    G2 = F[1].reshape(n, 2, m, n, 2, m).transpose(0, 1, 3, 4, 5, 2).reshape(-1, 2, m, m)
    G1 = F[0].reshape(n, 2, m, n, 2, m).transpose(0, 1, 3, 4, 5, 2).reshape(-1, 2, m, m)
    R2 = G2[:, 0].mean(axis=(1, 2)) - G2[:, 1].mean(axis=(1, 2))
    a = -gain * R2 / 2
    G2 = G2 + a[:, None, None, None] * main[None]
    G1 = G1 + a[:, None, None, None] * other[None]
    F[1] = G2.reshape(n, 2, n, 2, m, m).transpose(0, 1, 5, 2, 3, 4).reshape(G, G)
    F[0] = G1.reshape(n, 2, n, 2, m, m).transpose(0, 1, 5, 2, 3, 4).reshape(G, G)
    if stats is not None:
        # recompute both coordinates' pair differences on the corrected field
        H1 = F[0].reshape(n, 2, m, n, 2, m).transpose(0, 3, 4, 1, 2, 5).reshape(-1, 2, m, m)
        H2 = F[1].reshape(n, 2, m, n, 2, m).transpose(0, 1, 3, 4, 5, 2).reshape(-1, 2, m, m)
        r1 = np.abs(H1[:, 0].mean(axis=(1, 2)) - H1[:, 1].mean(axis=(1, 2))).max()
        r2 = np.abs(H2[:, 0].mean(axis=(1, 2)) - H2[:, 1].mean(axis=(1, 2))).max()
        scale = max(float(np.abs(R).max()), float(np.abs(R2).max()), 1e-300)
        stats['restore_residual'] = max(stats.get('restore_residual', 0.0), float(max(r1, r2)) / scale)


def fields(J, N, seed, gain=None, stats=None):
    """The dyadic field and the restored field of each configuration, for one seed (gain, when given, overrides
    every configuration's gain)."""
    rng = np.random.default_rng(seed)
    cells = rng.multinomial(N, np.full(4 ** J, 4.0 ** -J)).reshape(1 << J, 1 << J)
    G = 1 << (J + 1)
    dy = np.zeros((2, G, G))
    rs = [np.zeros((2, G, G)) for _ in CONFIGS]
    st = {}
    for j in range(J):
        sr.level_step(dy, cells, j, J, G, False, st)
        for F, (r0, g) in zip(rs, CONFIGS):
            sr.level_step(F, cells, j, J, G, False, st)
            restore_step(F, j - r0, G, g if gain is None else gain, stats if j == J - 1 else None)
    return dy, rs


def exceed(z, ts):
    return (np.abs(z)[..., None, :, :] > np.asarray(ts)[:, None, None]).sum(axis=(-2, -1))


def pass1(job):
    J, N, seeds = job
    G = 1 << (J + 1)
    nf = 1 + len(CONFIGS)
    S = np.zeros((nf, 2, G, G))
    Q = np.zeros((nf, 2, G, G))
    for seed in seeds:
        dy, rs = fields(J, N, seed)
        for f, x in enumerate([dy] + rs):
            S[f] += x
            Q[f] += x * x
    return S, Q


def pass2(job):
    J, N, seeds, mean, sd = job
    G = 1 << (J + 1)
    sig = sr.dyadic_sigma(J, G, N)
    out = {}
    for seed in seeds:
        dy, rs = fields(J, N, seed)
        arr = np.stack([dy] + rs)                                     # [flow, coord, y, x]
        zd = dy / sig
        planted = np.sign(zd) * np.abs(zd) ** 0.8
        z4 = ((arr - mean) / sd)
        out[seed] = {'self': exceed(z4, T_SELF),                      # [flow, coord, t]
                     'ana': exceed(np.concatenate([arr / sig, planted[None]]), T_ANA),
                     'm4': (z4 ** 4).mean(axis=(-2, -1))}             # [flow, coord]
    return out


def boot_ratio(cnt, f, rng, B=400):
    """Ratio of flow f's counts to the dyadic flow's, for every coordinate and threshold, with its bootstrap spread
    over seeds: a list [coord][t] of [ratio, spread]."""
    a = cnt[:, f].astype(float)                                       # [seed, coord, t]
    b = cnt[:, 0].astype(float)
    ratio = a.sum(axis=0) / np.maximum(b.sum(axis=0), 1.0)
    idx = rng.integers(0, len(a), size=(B, len(a)))
    rb = a[idx].sum(axis=1) / np.maximum(b[idx].sum(axis=1), 1.0)     # [B, coord, t]
    return np.stack([ratio, rb.std(axis=0)], axis=-1).tolist()


def summarize_level(J, N, nseeds, per, sd, rng):
    """One level's fractions, ratios with bootstrap spreads, variance ratios and fourth moments."""
    order = sorted(per)
    self_c = np.stack([per[s]['self'] for s in order])               # [seed, flow, coord, t]
    ana_c = np.stack([per[s]['ana'] for s in order])
    m4 = np.mean(np.stack([per[s]['m4'] for s in order]), axis=0)
    npos = nseeds * (1 << (J + 1)) ** 2
    var = (sd ** 2).mean(axis=(-2, -1))                              # [flow, coord]
    e = {'J': J, 'N': N, 'positions': npos,
         'dyadic_self_fraction': (self_c[:, 0].sum(axis=0) / npos).tolist(),
         'dyadic_ana_fraction': (ana_c[:, 0].sum(axis=0) / npos).tolist(),
         'variance_ratio': (var[1:] / var[0]).tolist(), 'fourth_moment': m4.tolist(), 'shifts': {}}
    for f, (r0, g) in enumerate(CONFIGS, start=1):
        e['shifts'][f'{r0},{g}'] = {'self_ratio': boot_ratio(self_c, f, rng), 'ana_ratio': boot_ratio(ana_c, f, rng)}
    e['planted_ana_ratio'] = boot_ratio(ana_c, len(CONFIGS) + 1, rng)
    return e


def run_level(pool, J, N, nseeds):
    """The two passes at one level: per-position spreads, then each seed's counts."""
    seeds = list(range(1, nseeds + 1))
    chunks = [seeds[c::14] for c in range(14)]
    r1 = list(pool.map(pass1, [(J, N, c) for c in chunks]))
    S = sum(r[0] for r in r1)
    Q = sum(r[1] for r in r1)
    mean = S / nseeds
    sd = np.sqrt(np.maximum(Q / nseeds - mean ** 2, 1e-300))
    per = {}
    for r in pool.map(pass2, [(J, N, c, mean, sd) for c in chunks]):
        per.update(r)
    return per, sd


def judge(res):
    """The Prediction's verdict per configuration and normalization, and the planted positive control."""
    pred = []
    for f, (r0, g) in enumerate(CONFIGS):
        for norm in ('self_ratio', 'ana_ratio'):
            vals = [e['shifts'][f'{r0},{g}'][norm][0][-1] for e in res]    # coordinate 1, largest threshold
            floor_ok = min(v[0] for v in vals) >= 0.7
            trend_ok = vals[-1][0] >= vals[0][0] - 2 * max(vals[0][1], vals[-1][1])
            pred.append({'r0': r0, 'gain': g, 'norm': norm, 'coord1_last': vals,
                         'floor_ok': floor_ok, 'trend_ok': trend_ok})
    planted = np.array([np.array(e['planted_ana_ratio'])[:, :, 0] for e in res])     # [level, coord, t]
    return {'prediction': all(p['floor_ok'] and p['trend_ok'] for p in pred), 'details': pred,
            'positive_control_planted': bool((planted[:, :, -1] < planted[:, :, 0]).all())}


def controls(out):
    """Gain 0, the weak-form divergence check with and without flipped legs, and the restoration residual."""
    J, N = 6, 16 * 4 ** 6
    G = 1 << (J + 1)
    dy, rs = fields(J, N, 777, gain=0.0)
    c0 = max(float(np.abs(x - dy).max()) for x in rs) / float(dy.std())
    st = {}
    dy, rs = fields(J, N, 1, gain=1.0, stats=st)
    import divergence_weak as dw                                      # noqa: E402 (local helper below)
    div = dw.ratios(rs[0] - dy, G)
    LEG_SIGN[0] = -1.0
    dyf, rsf = fields(J, N, 1)
    LEG_SIGN[0] = 1.0
    divf = dw.ratios(rsf[0] - dyf, G)
    res = {'gain0_max_rel_diff': c0, 'divergence': div, 'divergence_flipped_leg': divf,
           'restore_residual': st.get('restore_residual')}
    res['ok'] = {'gain0': c0 <= 1e-12, 'divergence': max(div.values()) < 1e-6,
                 'positive_divergence': max(divf.values()) > 1e-2,
                 'restoration': st.get('restore_residual', 1.0) <= 1e-9}
    print(json.dumps(res), flush=True)
    out['controls'] = res


def main():
    p = argparse.ArgumentParser(description=__doc__.split('\n\n')[0])
    p.add_argument('--levels', type=int, nargs='+', default=[6, 7, 8])
    p.add_argument('--per-cell', type=int, default=16)
    p.add_argument('--seeds', type=int, default=512)
    p.add_argument('--out', required=True)
    a = p.parse_args()
    out = {'levels': a.levels, 'seeds': a.seeds, 'per_cell': a.per_cell, 'configs': CONFIGS,
           'T_SELF': T_SELF, 'T_ANA': T_ANA, 'results': []}
    import sys
    sys.path.insert(0, str(HERE.parent))
    controls(out)
    rng = np.random.default_rng(20261017)
    with ProcessPoolExecutor(max_workers=14) as pool:
        for J in a.levels:
            N = a.per_cell * 4 ** J
            per, sd = run_level(pool, J, N, a.seeds)
            e = summarize_level(J, N, a.seeds, per, sd, rng)
            out['results'].append(e)
            print(json.dumps(e), flush=True)
            Path(a.out).write_text(json.dumps(out, indent=1))
    verdict = judge(out['results'])
    verdict['controls'] = out['controls']['ok']
    out['verdict'] = verdict
    print(json.dumps(verdict), flush=True)
    Path(a.out).write_text(json.dumps(out, indent=1))


if __name__ == '__main__':
    main()
