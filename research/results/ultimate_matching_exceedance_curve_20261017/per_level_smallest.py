#!/usr/bin/env python3
"""The smallest case of the exceedance slopes entry's next attempt (item two-choice-routing): the per-level
increments of the dyadic flow and the simultaneous rule at J = 2, N = 16 * 4^2 = 256, over many seeds.

The flows are built by level_step of research/results/ultimate_matching_simultaneous_rule_20261017/
simultaneous_rule_test.py, imported unchanged, called as its run() calls it (one call per level j = 0, ..., J-1,
each adding that level's increment to the field in place); here a copy of the field is kept after each call, so
the increment of level j is the difference of consecutive copies. For each flow, coordinate and level, each
position's increment is standardized across the seeds and the excess kurtosis (fourth moment minus 3) is pooled
over positions; so is that of the full field, and the correlation across seeds of the two levels' increments at
each position, averaged over positions; and, per position, the full excess against the independent-levels
value, their gap averaged over positions with its spread over 20 random half-splits of the seeds.

No statement tested: a hand-sized step that reads what the per-level decomposition looks like at its smallest
size, before any statement on it is posed.

Parallel use: the seeds run in 14 separate processes, one thread each.
"""
import argparse
from concurrent.futures import ProcessPoolExecutor
import importlib.util
import json
from pathlib import Path

import numpy as np

RULE = Path(__file__).resolve().parents[1] / 'ultimate_matching_simultaneous_rule_20261017' / 'simultaneous_rule_test.py'
_spec = importlib.util.spec_from_file_location('simultaneous_rule_test', RULE)
rule = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(rule)


def levels_job(job):
    return levels(*job)


def levels(J, N, seed):
    """Per-level increments (J, 2 flows, 2 coords, G, G) for one seed, built as run() builds the fields."""
    rng = np.random.default_rng(seed)
    cells = rng.multinomial(N, np.full(4 ** J, 4.0 ** -J)).reshape(1 << J, 1 << J)
    G = 1 << (J + 1)
    dy, sr = np.zeros((2, G, G)), np.zeros((2, G, G))
    out = np.zeros((J, 2, 2, G, G))
    stats = {}
    for j in range(J):
        before = dy.copy(), sr.copy()
        rule.level_step(dy, cells, j, J, G, False, stats)
        rule.level_step(sr, cells, j, J, G, True, stats)
        out[j, 0], out[j, 1] = dy - before[0], sr - before[1]
    return out


def excess(x):
    """x: (S, ...) values across seeds; per-position standardization, pooled excess kurtosis."""
    z = (x - x.mean(axis=0)) / x.std(axis=0)
    return float(np.nanmean(z ** 4) - 3.0)


def per_position_gap(x):
    """x: (S, J, G, G) per-level increments across seeds. At each position, the full field's excess kurtosis and
    the value independent levels would give, sum_j kappa_j v_j^2 / (sum_j v_j)^2 with kappa_j, v_j that
    position's level excess and variance; both averaged over the positions where every level varies. The
    pooled form (pooled excesses with position-averaged variances) mixes positions of unequal variance and is
    biased (17 October 2026, the reviewer's third pass)."""
    v = x.var(axis=0)                                                   # (J, G, G)
    c = x - x.mean(axis=0)
    kap = (c ** 4).mean(axis=0) / v ** 2 - 3.0
    full = x.sum(axis=1)
    fc = full - full.mean(axis=0)
    kfull = (fc ** 4).mean(axis=0) / fc.var(axis=0) ** 2 - 3.0
    ok = np.all(v > 0, axis=0)
    ind = (kap * v ** 2).sum(axis=0) / v.sum(axis=0) ** 2
    return {'full_per_position': float(kfull[ok].mean()), 'independent_per_position': float(ind[ok].mean()),
            'gap': float((kfull - ind)[ok].mean()), 'positions_used': int(ok.sum())}


def main():
    p = argparse.ArgumentParser(description=__doc__.split('\n\n')[0])
    p.add_argument('--J', type=int, default=2)
    p.add_argument('--seeds', type=int, default=4000)
    p.add_argument('--out', required=True)
    a = p.parse_args()
    N = 16 * 4 ** a.J
    rng = np.random.default_rng(20261017)
    with ProcessPoolExecutor(max_workers=14) as pool:
        inc = np.stack(list(pool.map(levels_job, [(a.J, N, s) for s in range(1, a.seeds + 1)], chunksize=16)))
    # inc: (S, J, flow, coord, G, G)
    res = {'J': a.J, 'N': N, 'seeds': a.seeds}
    for f, name in enumerate(('dyadic', 'rule')):
        for k in range(2):
            key = f'{name}_coord{k + 1}'
            per = [excess(inc[:, j, f, k]) for j in range(a.J)]
            full = excess(inc[:, :, f, k].sum(axis=1))
            a0, a1 = inc[:, 0, f, k], inc[:, 1, f, k]
            c0, c1 = a0 - a0.mean(axis=0), a1 - a1.mean(axis=0)
            corr = float(np.nanmean((c0 * c1).mean(axis=0) / (c0.std(axis=0) * c1.std(axis=0))))
            var = [float(np.mean(inc[:, j, f, k].var(axis=0))) for j in range(a.J)]
            gap, halves = per_position_gap(inc[:, :, f, k]), []
            for _ in range(20):
                perm = rng.permutation(a.seeds)
                halves.append(per_position_gap(inc[perm[:a.seeds // 2], :, f, k])['gap']
                              - per_position_gap(inc[perm[a.seeds // 2:], :, f, k])['gap'])
            res[key] = {'excess_per_level': per, 'excess_full': full, 'corr_levels_0_1': corr,
                        'mean_variance_per_level': var, **gap,
                        'gap_spread': float(np.std(halves) / 2)}
            print(key, json.dumps(res[key]), flush=True)
    Path(a.out).write_text(json.dumps(res, indent=1) + '\n')


if __name__ == '__main__':
    main()
