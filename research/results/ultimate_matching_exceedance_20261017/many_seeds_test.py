#!/usr/bin/env python3
"""The exceedance test of research/results/ultimate_matching_exceedance_20261017/exceedance_test.py with many
independent seeds, so that per-point tails are read across seeds rather than across the positions of a few.

Why: in that run (results.json beside this script) the dyadic flow's pooled exceedances, over the positions of
eight seeds, were far from Gaussian (0.0002-0.001 at 3.3 standard deviations against 0.00097), although
thm:dyadic-flow-obstruction proves its per-point values Gaussian in the limit: the positions of one seed share
its coarse counts, and eight seeds sample those coarse levels only eight times. Here each position's value is
standardized by its own standard deviation across S independent seeds, for each flow (an empirical per-position
sigma, which also checks the dyadic flow's analytic one), and exceedances are pooled over seeds and positions.

Statement tested (the simultaneous rule entry's Prediction, as there): at the fixed threshold t = 3.3, with each
flow standardized by its own per-position sigma, the ratio of the rule's exceedance fraction to the dyadic
flow's stays constant from J = 6 to J = 7; refuted if it falls by more than its half-sample spread.

Expectations, written before any run.
- Control 1 (the estimator reads Gaussian tails where they are Gaussian): the dyadic flow's fraction at t = 2.2
  lies within 0.15 of erfc(2.2/sqrt 2) = 0.0278 in relative terms, and at t = 3.3 within 0.3 of 0.00097, in each
  coordinate and at each size.
  Refuted by: a printed dyadic fraction outside those ranges at some size.
  Possible because: positions remain correlated within a seed, and finite J leaves the dyadic per-point law a
  finite sum of level terms whose own tails may be lighter or heavier than Gaussian.
- Control 2 (the empirical sigma matches the analytic one for the dyadic flow): the mean over positions of the
  ratio of the empirical per-position variance across seeds to the analytic one is within 0.1 of 1.
  Refuted by: a printed mean variance ratio outside [0.9, 1.1].
  Possible because: an error in the imported flow or in its sigma would show here.
- Positive control (the statistic can see a lighter tail): a planted law, the dyadic flow's values replaced by
  sign times |value|^0.8 rescaled to unit variance per position (lighter tails), must give a fraction at 3.3
  below 0.7 of the dyadic flow's.
  Refuted by: a printed planted-to-dyadic ratio at 3.3 of at least 0.7 in some coordinate.
  Possible because: the planted law's tails may not be light enough at 3.3 for the counts reached.
- Prediction: the rule's own-sigma fraction at 3.3 over the dyadic flow's, at J = 7, differs from that at
  J = 6 by at most the larger half-sample spread, in each coordinate.
  Refuted by: a fall from J = 6 to J = 7 larger than that spread.
  Possible because: the rule is nonlinear in the counts and its pooled kurtosis was below the dyadic flow's.
Baseline: Gaussian fractions erfc(t/sqrt 2): 0.0278 at 2.2 and 0.00097 at 3.3; with S = 512 seeds and G^2
positions the expected count at 3.3 is 0.00097 S G^2, 8100 at J = 6 and 32500 at J = 7, though positions in a
seed are correlated, so the half-sample spread is what decides.
Record checked: these were read for whether they decide the rule's per-point tails, and none does:
ex:simultaneous-rule-tails, thm:dyadic-flow-obstruction, lem:equalized-flow-separable and ex:greedy-circulation-tails.
Decisive at these sizes: only for a change larger than the printed half-sample spread; two sizes cannot show a
trend in J, only a difference.
Parallel use: the seeds run in separate processes, 14 at a time, one thread each.
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
rule = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(rule)


def run_job(job):
    """The imported rule's run, returning both flows divided by the dyadic flow's analytic sigma (float32)."""
    _, dz, sz = rule.run(job)
    return dz.astype(np.float32), sz.astype(np.float32)


def stats(stack, thresholds):
    """stack: (S, 2, G, G) values over the analytic sigma; standardize per position by the empirical sigma."""
    sd = stack.std(axis=0)
    z = np.abs(stack / sd[None])
    out = []
    for k in range(2):
        out.append({'fraction': [float(np.mean(z[:, k] > t)) for t in thresholds],
                    'mean_variance_ratio_to_analytic': float(np.mean(sd[k] ** 2))})
    return out, z


def main():
    p = argparse.ArgumentParser(description=__doc__.split('\n\n')[0])
    p.add_argument('--levels', type=int, nargs='+', default=[6, 7])
    p.add_argument('--per-cell', type=int, default=16)
    p.add_argument('--seeds', type=int, default=512)
    p.add_argument('--out', required=True)
    a = p.parse_args()
    thr = [2.2, 3.3]
    rows = []
    for J in a.levels:
        jobs = [(J, a.per_cell * 4 ** J, s) for s in range(1, a.seeds + 1)]
        with ProcessPoolExecutor(max_workers=14) as pool:
            res = list(pool.map(run_job, jobs, chunksize=4))
        D = np.stack([d for d, _ in res])
        R = np.stack([r for _, r in res])
        del res
        dstat, dz = stats(D, thr)
        rstat, rz = stats(R, thr)
        planted = np.sign(D) * np.abs(D) ** 0.8
        pstat, _ = stats(planted, thr)
        h = a.seeds // 2
        row = {'J': J, 'seeds': a.seeds, 'gaussian': [math.erfc(t / math.sqrt(2)) for t in thr]}
        for k in range(2):
            halves = []
            for part in (slice(0, h), slice(h, None)):
                dd = float(np.mean(dz[part, k] > 3.3))
                rr = float(np.mean(rz[part, k] > 3.3))
                halves.append(rr / dd if dd > 0 else float('nan'))
            row[f'coord{k + 1}'] = {
                'dyadic': dstat[k], 'rule': rstat[k], 'planted': pstat[k],
                'ratio_rule_at_3.3': rstat[k]['fraction'][1] / dstat[k]['fraction'][1],
                'ratio_planted_at_3.3': pstat[k]['fraction'][1] / dstat[k]['fraction'][1],
                'ratio_rule_halves': halves, 'half_spread': abs(halves[0] - halves[1])}
        rows.append(row)
        print(json.dumps(row), flush=True)
        del D, R, dz, rz, planted
    lo, hi = rows[0], rows[-1]
    verdict = {}
    for c in ('coord1', 'coord2'):
        fall = lo[c]['ratio_rule_at_3.3'] - hi[c]['ratio_rule_at_3.3']
        spread = max(lo[c]['half_spread'], hi[c]['half_spread'])
        verdict[c] = {'fall': fall, 'spread': spread, 'refuted': fall > spread}
    print(json.dumps(verdict), flush=True)
    with open(a.out, 'w') as fh:
        json.dump({'per_cell': a.per_cell, 'rows': rows, 'verdict': verdict}, fh, indent=1)


if __name__ == '__main__':
    main()
