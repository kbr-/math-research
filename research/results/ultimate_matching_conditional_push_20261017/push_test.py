#!/usr/bin/env python3
"""The conditional push probabilities of the ultimate-matching notebook's conditional push obstruction (item
two-choice-routing): at each level j >= 1 and position x, with R_j(x) the field built by the levels before j,
  same(c)     = P( sign(R_j(x)) Phi_j(x) >= c sd_j(x) ),
  opposite(c) = P( -sign(R_j(x)) Phi_j(x) >= c sd_j(x) ),
sd_j(x) the standard deviation of Phi_j(x) across seeds, for the dyadic flow and the simultaneous rule at J = 2,
3, 4, coordinate by coordinate, averaged over positions, with the minimum over positions of same(c). The
obstruction needs same(c) >= p at the fine levels of most points (for both signs; the running sign is the
one that matters); a rule escapes it only where same(c) falls with the level or with J.

The level increments are those of research/results/ultimate_matching_exceedance_curve_20261017/
per_level_smallest.py's levels(), imported unchanged (level_step of the simultaneous rule script, one call per
level, increments as differences of consecutive copies).

Statement tested: the simultaneous rule's conditional same-sign push probability at c = 0.5 is at least half
its opposite-sign one at every level j >= 1 and every J run (it pushes along the running field nearly as often
as against it, so the obstruction's hypothesis is not escaped at these sizes).
Expectations, written before any run.
- Positive control (the measurement sees symmetric pushes where they are symmetric): for the dyadic flow, whose
  level-j increment is a function of the level's fresh child counts with coefficients fixed by the position,
  same(0.5) and opposite(0.5) agree within 0.02 at every level and J, near P(Z >= 0.5) = 0.31.
  Refuted by: a printed dyadic same and opposite differing by more than 0.02 at some level and J.
  Possible because: the dyadic increment's sign is independent of the coarser field only if the fresh counts
  are independent of it given the square's total, which the multinomial split gives but finite seeds blur.
- Prediction: for the rule, same(0.5) >= opposite(0.5) / 2 at every level j >= 1 and every J in 2, 3, 4.
  Refuted by: a printed rule same(0.5) below half its opposite(0.5) at some level and J.
  Possible because: the rule chooses each square's profiles to lower the quartic load of the running field,
  which steers fresh flux away from points already loaded, the item's two-choice mechanism.
Baseline: for a flow whose increments are independent of the coarser field and symmetric, same = opposite; the
dyadic flow is such a flow at each fixed position (thm:dyadic-flow-obstruction's proof represents its fine
levels as a sum of i.i.d. kernel terms given the coarse counts).
Record checked: these were read for whether they decide the push probabilities, and none does:
thm:dyadic-flow-obstruction, lem:block-lower-tail, ex:simultaneous-rule-tails, ex:exceedance-curve-slopes.
Decisive at these sizes: with S seeds per position the standard error of a fraction near 0.3 is about
0.46/sqrt(S), 0.007 at 4000 seeds, and averaging over positions shrinks it further, so a factor 2 between same
and opposite is far outside the noise; whether a gap grows with J needs the three sizes and is read as a
trend only if monotone at both coordinates.
Parallel use: the seeds run in 14 separate processes, one thread each.
"""
import argparse
import importlib.util
import json
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

import numpy as np

LEVELS = Path(__file__).resolve().parents[1] / 'ultimate_matching_exceedance_curve_20261017' / 'per_level_smallest.py'
_spec = importlib.util.spec_from_file_location('per_level_smallest', LEVELS)
per = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(per)

C = 0.5


def job(args):
    return per.levels(*args).astype(np.float32)


def push(inc):
    """inc: (S, J, G, G) one flow and coordinate. Per level j >= 1: mean over positions of same and opposite
    fractions at C, and the minimum over positions of same."""
    S, J = inc.shape[:2]
    out = []
    for j in range(1, J):
        R = inc[:, :j].sum(axis=1)
        X = inc[:, j]
        sd = X.std(axis=0)
        sg = np.sign(R)
        same = ((sg * X) >= C * sd).mean(axis=0)
        opp = ((-sg * X) >= C * sd).mean(axis=0)
        out.append({'level': j, 'same': float(same.mean()), 'opposite': float(opp.mean()),
                    'same_min_over_positions': float(same.min())})
    return out


def main():
    p = argparse.ArgumentParser(description=__doc__.split('\n\n')[0])
    p.add_argument('--levels', type=int, nargs='+', default=[2, 3, 4])
    p.add_argument('--seeds', type=int, nargs='+', default=[4000, 4000, 1400])
    p.add_argument('--out', required=True)
    a = p.parse_args()
    res = []
    for J, S in zip(a.levels, a.seeds):
        N = 16 * 4 ** J
        with ProcessPoolExecutor(max_workers=14) as pool:
            inc = np.stack(list(pool.map(job, [(J, N, s) for s in range(1, S + 1)], chunksize=8)))
        row = {'J': J, 'N': N, 'seeds': S}
        for f, name in enumerate(('dyadic', 'rule')):
            for k in range(2):
                row[f'{name}_coord{k + 1}'] = push(inc[:, :, f, k])
        res.append(row)
        print(json.dumps(row), flush=True)
        Path(a.out).write_text(json.dumps(res, indent=1) + '\n')
    checks = {'control_max_dyadic_gap': max(abs(l['same'] - l['opposite']) for r in res for k in ('dyadic_coord1', 'dyadic_coord2') for l in r[k]),
              'prediction_holds': all(l['same'] >= l['opposite'] / 2 for r in res for k in ('rule_coord1', 'rule_coord2') for l in r[k])}
    print(json.dumps(checks), flush=True)
    Path(a.out).write_text(json.dumps({'rows': res, 'checks': checks}, indent=1) + '\n')


if __name__ == '__main__':
    main()
