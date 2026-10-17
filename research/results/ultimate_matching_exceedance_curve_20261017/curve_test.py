#!/usr/bin/env python3
"""The fixed-estimator exceedance curve, the next attempt of the ultimate-matching notebook's simultaneous rule
exceedances entry (item two-choice-routing): does the simultaneous rule's lighter per-point tail keep its shape
as J grows, or drift back toward the dyadic flow's Gaussian tail?

The flows are those of research/results/ultimate_matching_simultaneous_rule_20261017/simultaneous_rule_test.py,
through research/results/ultimate_matching_exceedance_20261017/many_seeds_test.py's run_job, imported unchanged.
For each size J in 5, 6, 7, S = 512 independent seeds, each flow and coordinate: each position's value is
centred by its mean across the seeds and divided by its standard deviation across the seeds; the exceedance
fraction at t, pooled over seeds and positions, is computed at t = 2.6, 3.0, 3.3, 3.6; the log-ratio
r(t) = log(rule fraction / dyadic fraction) is fitted by least squares as a line in t, its slope the curve's
shape. The same estimator is used at every J and for both flows, so its self-inclusion bias (about -3.4% of the
Gaussian fraction at 3.3 for 512 seeds) enters the rule and the dyadic flow alike and largely cancels in r(t).
Spread: 200 random splits of the seeds into halves, the slope computed on each half; the spread of a slope is
the standard deviation over splits of the half-slope difference, divided by 2 (the full-sample slope's spread).

Statement tested (the exceedances entry's Prediction, committed there): in each coordinate the slope at J = 7
equals the slope at J = 5 within twice the combined spread sqrt(spread_5^2 + spread_7^2) (a fixed-shape lighter
law); refuted if at J = 7 it is flatter (nearer 0) by more than that.

Expectations, written before any run.
- Control 1 (the estimator reads Gaussian tails where they are Gaussian): the dyadic flow's fraction at each t
  lies within a factor 1.5 of erfc(t / sqrt 2) at every J, in each coordinate.
  Refuted by: a printed dyadic fraction outside a factor 1.5 of the Gaussian value at some t and J.
  Possible because: positions of one seed share coarse counts, and the per-position estimate has a negative
  self-inclusion bias that grows with t, so the pooled fraction can fall below the Gaussian value.
- Positive control (the curve sees a fixed lighter shape): the planted flow sign(D)|D|^0.8 (the dyadic values
  raised to the power 0.8, a fixed lighter law) has a negative log-ratio slope against the dyadic flow at every
  J, equal at J = 5 and J = 7 within twice the combined spread.
  Refuted by: a planted slope that is not negative at some J, or differs between J = 5 and 7 by more than that.
  Possible because: the per-position standardization re-scales the planted values, and a power below 1 of a
  standardized Gaussian is still lighter-tailed only if the standardization keeps the shape.
- Prediction: as stated above, for the simultaneous rule.
  Refuted by: a rule slope at J = 7 nearer 0 than at J = 5 by more than twice the combined spread.
  Possible because: the rule is nonlinear in the counts and could approach the dyadic flow's law as the number
  of levels grows, which the item asks about.
Baseline: for Gaussian per-point values the fractions are erfc(t/sqrt 2): 0.00933 at 2.6, 0.00270 at 3.0,
0.00097 at 3.3, 0.00032 at 3.6; a fixed-shape law has a slope independent of J; the recorded two-threshold
slopes (research/results/ultimate_matching_exceedance_20261017/recorded_slopes.txt) are -0.979 and -0.757 at
J = 6, 7 in coordinate 1 and -0.608 and -0.694 in coordinate 2, from one split.
Record checked: these were read for whether they decide the slopes at J = 5, 6, 7, and none does:
ex:simultaneous-rule-exceedances, ex:simultaneous-rule-tails, thm:dyadic-flow-obstruction, lem:sequential-rules-dyadic.
Decisive at these sizes: only for a slope change larger than twice the combined spread; the exceedances entry
estimated a slope standard error near 0.096 per unit of t at J = 5 from Poisson counts with independent
positions, so a drift of order 1/J (about 0.29 on coordinate 1) can be seen and one of order 1/sqrt J (0.12 to
0.15) cannot; a change below twice the spread is reported as not decided.
Parallel use: the seeds of one size run in 14 separate processes, one thread each.
"""
import argparse
import importlib.util
import json
import math
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve()
MANY = HERE.parents[1] / 'ultimate_matching_exceedance_20261017' / 'many_seeds_test.py'
_spec = importlib.util.spec_from_file_location('many_seeds_test', MANY)
many = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(many)

THRESHOLDS = [2.6, 3.0, 3.3, 3.6]


def run_job(job):
    """many_seeds_test's run_job, wrapped here so that the worker processes can pickle it by this module's name."""
    return many.run_job(job)


def fractions(stack):
    """stack: (S, 2, G, G). Per-position centring and standardization across seeds; returns z = |standardized|."""
    centred = stack - stack.mean(axis=0, keepdims=True)
    sd = centred.std(axis=0, keepdims=True)
    return np.abs(centred / sd)


def counts(z, seeds):
    """Exceedance fractions of z restricted to the given seed indices: (2 coords, len(THRESHOLDS))."""
    part = z[seeds]
    return np.array([[float(np.mean(part[:, k] > t)) for t in THRESHOLDS] for k in range(2)])


def slope(f_num, f_den):
    """Least-squares slope in t of log(f_num / f_den); nan where a fraction is zero."""
    if np.any(f_num <= 0) or np.any(f_den <= 0):
        return float('nan')
    r = np.log(f_num / f_den)
    t = np.array(THRESHOLDS)
    return float(np.polyfit(t, r, 1)[0])


def main():
    p = argparse.ArgumentParser(description=__doc__.split('\n\n')[0])
    p.add_argument('--levels', type=int, nargs='+', default=[5, 6, 7])
    p.add_argument('--per-cell', type=int, default=16)
    p.add_argument('--seeds', type=int, default=512)
    p.add_argument('--splits', type=int, default=200)
    p.add_argument('--out', required=True)
    a = p.parse_args()
    rng = np.random.default_rng(20261017)
    gaussian = [math.erfc(t / math.sqrt(2)) for t in THRESHOLDS]
    rows = []
    for J in a.levels:
        jobs = [(J, a.per_cell * 4 ** J, s) for s in range(1, a.seeds + 1)]
        with ProcessPoolExecutor(max_workers=14) as pool:
            res = list(pool.map(run_job, jobs, chunksize=4))
        D = np.stack([d for d, _ in res])
        R = np.stack([r for _, r in res])
        del res
        P = np.sign(D) * np.abs(D) ** 0.8
        zd, zr, zp = fractions(D), fractions(R), fractions(P)
        del D, R, P
        every = np.arange(a.seeds)
        fd, fr, fp = counts(zd, every), counts(zr, every), counts(zp, every)
        row = {'J': J, 'seeds': a.seeds, 'thresholds': THRESHOLDS, 'gaussian': gaussian}
        for k in range(2):
            diffs_r, diffs_p = [], []
            for _ in range(a.splits):
                perm = rng.permutation(a.seeds)
                h1, h2 = perm[:a.seeds // 2], perm[a.seeds // 2:]
                d1, d2 = counts(zd, h1)[k], counts(zd, h2)[k]
                diffs_r.append(slope(counts(zr, h1)[k], d1) - slope(counts(zr, h2)[k], d2))
                diffs_p.append(slope(counts(zp, h1)[k], d1) - slope(counts(zp, h2)[k], d2))
            row[f'coord{k + 1}'] = {
                'dyadic': fd[k].tolist(), 'rule': fr[k].tolist(), 'planted': fp[k].tolist(),
                'slope_rule': slope(fr[k], fd[k]), 'slope_planted': slope(fp[k], fd[k]),
                'spread_rule': float(np.nanstd(diffs_r) / 2), 'spread_planted': float(np.nanstd(diffs_p) / 2),
                'control1_max_factor': float(max(max(f / g, g / f) for f, g in zip(fd[k], gaussian)))}
        rows.append(row)
        print(json.dumps(row), flush=True)
        del zd, zr, zp
    lo, hi = rows[0], rows[-1]
    verdict = {}
    for c in ('coord1', 'coord2'):
        for flow in ('rule', 'planted'):
            change = hi[c][f'slope_{flow}'] - lo[c][f'slope_{flow}']
            bound = 2 * math.hypot(lo[c][f'spread_{flow}'], hi[c][f'spread_{flow}'])
            verdict[f'{c}_{flow}'] = {'slope_lo': lo[c][f'slope_{flow}'], 'slope_hi': hi[c][f'slope_{flow}'],
                                      'change': change, 'twice_combined_spread': bound,
                                      'decided': not (math.isnan(change) or math.isnan(bound)),
                                      'flatter_beyond_bound': change > bound,
                                      'differs_beyond_bound': abs(change) > bound}
        verdict[f'{c}_control1_max_factor'] = max(r[c]['control1_max_factor'] for r in rows)
    print(json.dumps(verdict), flush=True)
    with open(a.out, 'w') as fh:
        json.dump({'per_cell': a.per_cell, 'rows': rows, 'verdict': verdict}, fh, indent=1)


if __name__ == '__main__':
    main()
