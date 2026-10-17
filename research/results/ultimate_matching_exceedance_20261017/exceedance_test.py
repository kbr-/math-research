#!/usr/bin/env python3
"""The item two-choice-routing of the ultimate-matching notebook, the next attempt of the simultaneous rule
entry: the tails the item asks about, for the simultaneous rule and the dyadic flow at J = 6, 7, 8.

The flows are those of research/results/ultimate_matching_simultaneous_rule_20261017/simultaneous_rule_test.py,
imported unchanged (its run() returns both flows divided by the dyadic flow's analytic per-position sigma).
For each coordinate the script computes the fraction of the G^2 evaluation positions, pooled over the seeds of
one size, whose value exceeds t in absolute value:
- standardization D: by the dyadic flow's analytic per-position sigma (as returned);
- standardization R: for the rule, additionally divided by the square root of its pooled variance ratio to the
  dyadic flow in that coordinate at that size, a stand-in for the rule's own sigma that removes the variance
  shift (0.58-0.65 and 1.26-1.36) and keeps the per-position profile of the dyadic sigma; the dyadic flow is
  left as in D;
at the fixed thresholds t = 2.2 and 3.3 at every J, and at c sqrt(2 log G^2) for c = 1/2, 3/4.

Statement tested (the simultaneous rule entry's Prediction, committed there before this script): at the fixed
threshold t = 3.3, with standardization R, the ratio of the rule's exceedance fraction to the dyadic flow's
stays constant at J = 6, 7, 8; refuted if it falls with J by more than its seed spread.

Expectations, written before any run.
- Control 1 (the dyadic flow's exceedances are Gaussian): the dyadic flow's fraction at t = 2.2 lies within
  0.2 of erfc(2.2/sqrt 2) = 0.0278 in relative terms at every size, and at t = 3.3 within a factor 2 of
  0.00097, in each coordinate.
  Refuted by: a printed dyadic fraction outside those ranges at some size.
  Possible because: the pooled estimate shares coarse counts across positions (its kurtosis was 2.88-3.11),
  which could move the tail fractions from the Gaussian values.
- Control 2 (standardization R does what it is for): the rule's pooled variance after R equals the dyadic
  flow's in each coordinate, ratio within 1e-9 of 1.
  Refuted by: a printed post-R variance ratio further than 1e-9 from 1.
  Possible because: the ratio may be taken from the wrong coordinate or size.
- Positive control: under D the rule's coordinate-1 fraction at t = 2.2 is below the dyadic flow's at every
  size, since its coordinate-1 variance is 0.58-0.65 of the dyadic flow's.
  Refuted by: a rule fraction at least the dyadic one under D in coordinate 1 at some size.
  Possible because: the variance shift could be concentrated where the dyadic sigma is small.
- Prediction: with R at t = 3.3, the ratio rule/dyadic at J = 8 differs from that at J = 6 by at most the
  larger of the two sizes' half-sample spreads, in each coordinate.
  Refuted by: a ratio falling from J = 6 to J = 8 by more than that spread in some coordinate.
  Possible because: the rule is nonlinear in the counts and its pooled kurtosis was 0.36-0.44 below the dyadic
  flow's, so its tails can differ, and differ more at larger J.
Baseline: for Gaussian per-point values the fractions are erfc(t/sqrt 2): 0.0278 at 2.2 and 0.00097 at 3.3;
thm:dyadic-flow-obstruction proves the dyadic flow's per-point variance and obstruction.
Record checked: these were read for whether they decide the rule's exceedances, and none does:
ex:simultaneous-rule-tails, thm:dyadic-flow-obstruction, lem:equalized-flow-separable and ex:greedy-circulation-tails.
Decisive at these sizes: at t = 3.3 the expected count is about 0.001 G^2 per seed, 127 positions over eight
seeds at J = 6 and 2000 at J = 8, so the J = 6 ratio has a relative spread near 0.1; a fall smaller than the
printed half-sample spread is reported as not decided.
Parallel use: the seeds of one size run in separate processes, up to 8 at a time, one thread each.
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


def fractions(arrs, k, thresholds, scale=1.0):
    z = np.abs(np.concatenate([a[k].ravel() for a in arrs])) / scale
    return [float(np.mean(z > t)) for t in thresholds]


def main():
    p = argparse.ArgumentParser(description=__doc__.split('\n\n')[0])
    p.add_argument('--levels', type=int, nargs='+', default=[6, 7, 8])
    p.add_argument('--per-cell', type=int, default=16)
    p.add_argument('--seeds', type=int, nargs='+', default=[1, 2, 3, 4, 5, 6, 7, 8])
    p.add_argument('--out', required=True)
    a = p.parse_args()
    jobs = [(J, a.per_cell * 4 ** J, s) for J in a.levels for s in a.seeds]
    with ProcessPoolExecutor(max_workers=min(8, len(a.seeds))) as pool:
        results = list(pool.map(rule.run, jobs))
    by = {}
    for r, dz, sz in results:
        by.setdefault(r['J'], []).append((dz, sz))
    out = []
    for J in a.levels:
        dzs = [x for x, _ in by[J]]
        szs = [y for _, y in by[J]]
        G = dzs[0].shape[1]
        fixed = [2.2, 3.3]
        moving = [0.5 * math.sqrt(2 * math.log(G * G)), 0.75 * math.sqrt(2 * math.log(G * G))]
        thr = fixed + moving
        h = len(dzs) // 2
        row = {'J': J, 'G2': G * G, 'thresholds': thr, 'gaussian': [math.erfc(t / math.sqrt(2)) for t in thr]}
        for k in range(2):
            var_ratio = float(np.concatenate([y[k].ravel() for y in szs]).var()
                              / np.concatenate([x[k].ravel() for x in dzs]).var())
            sR = math.sqrt(var_ratio)
            post = float((np.concatenate([y[k].ravel() for y in szs]) / sR).var()
                         / np.concatenate([x[k].ravel() for x in dzs]).var())
            d_all = fractions(dzs, k, thr)
            rD = fractions(szs, k, thr)
            rR = fractions(szs, k, thr, sR)
            halves = []
            for part in (slice(0, h), slice(h, None)):
                dd = fractions(dzs[part], k, [3.3])[0]
                rr = fractions(szs[part], k, [3.3], sR)[0]
                halves.append(rr / dd if dd > 0 else float('nan'))
            row[f'coord{k + 1}'] = {'variance_ratio': var_ratio, 'control2_post_R_ratio': post,
                                    'dyadic': d_all, 'rule_D': rD, 'rule_R': rR,
                                    'ratio_R_at_3.3': rR[1] / d_all[1] if d_all[1] > 0 else float('nan'),
                                    'ratio_R_at_3.3_halves': halves,
                                    'half_spread': abs(halves[0] - halves[1])}
        out.append(row)
        print(json.dumps(row), flush=True)
    verdict = {}
    lo, hi = out[0], out[-1]
    for k in (1, 2):
        c = f'coord{k}'
        fall = lo[c]['ratio_R_at_3.3'] - hi[c]['ratio_R_at_3.3']
        spread = max(lo[c]['half_spread'], hi[c]['half_spread'])
        verdict[c] = {'fall_J6_to_J8': fall, 'spread': spread, 'refuted': fall > spread}
    print(json.dumps(verdict), flush=True)
    with open(a.out, 'w') as fh:
        json.dump({'per_cell': a.per_cell, 'rows': out, 'verdict': verdict,
                   'runs': [r for r, _, _ in results]}, fh, indent=1)


if __name__ == '__main__':
    main()
