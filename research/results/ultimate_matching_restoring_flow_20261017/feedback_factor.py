#!/usr/bin/env python3
"""The restoration's feedback factor at gain 1: a unit mean difference on one sibling pair of level i, restored by
restore_step of restoring_flow_test.py, leaves in the field mean differences on the pairs of level i + 1 (both
coordinates); the largest such difference, per unit of the restored one, is the factor by which one level's
restoration seeds the next level's. At gain g the seeded differences scale by g, so restoration that feeds on its
own legs grows from level to level when g times the factor exceeds 1.

No statement tested: it computes the factor the restoring-flow entry's reviewer asked for, to replace an unverified
cause ("the restoration feeds on its own legs") by a number. Both pair orientations are restored by the step, so
the input is a coordinate-1 difference on a vertical pair and, separately, a coordinate-2 difference on a
horizontal pair.
"""
import importlib.util
import json
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
_spec = importlib.util.spec_from_file_location('rft', HERE / 'restoring_flow_test.py')
rft = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(rft)


def pair_differences(F, i, G):
    """Mean differences of the level-i sibling pairs: coordinate 1 on vertical pairs, coordinate 2 on horizontal."""
    n, m = 1 << (i - 1), G >> i
    v = F[0].reshape(n, 2, m, n, 2, m).transpose(0, 3, 4, 1, 2, 5).reshape(-1, 2, m, m)
    h = F[1].reshape(n, 2, m, n, 2, m).transpose(0, 1, 3, 4, 5, 2).reshape(-1, 2, m, m)
    return (v[:, 0].mean(axis=(1, 2)) - v[:, 1].mean(axis=(1, 2)),
            h[:, 0].mean(axis=(1, 2)) - h[:, 1].mean(axis=(1, 2)))


def main():
    out = {}
    G = 1 << 7
    for i in (2, 3, 4):
        for coord in (0, 1):
            F = np.zeros((2, G, G))
            m = G >> i
            # one level-i pair inside the first level-(i-1) parent: +1/2 and -1/2 on its two children
            if coord == 0:
                F[0, :m, :m] = 0.5
                F[0, m:2 * m, :m] = -0.5
            else:
                F[1, :m, :m] = 0.5
                F[1, :m, m:2 * m] = -0.5
            rft.restore_step(F, i, G, 1.0)
            r_now = [float(np.abs(d).max()) for d in pair_differences(F, i, G)]
            r_next = [float(np.abs(d).max()) for d in pair_differences(F, i + 1, G)]
            # every seeded pair, with its sign, and the L2 gain (root sum of squares per unit restored): the
            # largest seed alone is a one-chain model, not the level-to-level map's growth (the reviewer's)
            seeds = [sorted(round(float(x), 6) for x in d if abs(x) > 1e-12) for d in pair_differences(F, i + 1, G)]
            l2 = [float(np.sqrt(np.sum(np.square(d)))) for d in pair_differences(F, i + 1, G)]
            out[f'level {i}, input coordinate {coord + 1}'] = {'left at level i (c1, c2)': r_now,
                                                              'seeded at level i+1 (c1, c2)': r_next,
                                                              'all seeds (c1, c2)': seeds, 'L2 gain (c1, c2)': l2}
            print(f'level {i}, input coordinate {coord + 1}: left at level i {r_now}, largest seed at level i+1 '
                  f'{r_next}, all seeds {seeds}, L2 gain {l2}', flush=True)
    (HERE / 'feedback_factor.json').write_text(json.dumps(out, indent=1))


if __name__ == '__main__':
    main()
