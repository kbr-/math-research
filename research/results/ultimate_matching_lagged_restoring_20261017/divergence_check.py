#!/usr/bin/env python3
"""A control the lagged restoring flow's test lacked (the reviewer of 17 October 2026): that the correction
w = lagged field - dyadic field is divergence-free with zero normal flux on the unit square's boundary, tested in its
weak form: for every smooth g, int w . grad g = 0. With the fields sampled at the positions' centres, the sum
sum_positions (w_1 dg/dx + w_2 dg/dy) / G^2 is compared with sum |w| |grad g| / G^2; a misoriented leg or a leg on
the wrong axis leaves a ratio of order one, a correct one a ratio of the order of the sampling error.

No statement tested: a control of lagged_test.py's construction, imported unchanged.
Control: the ratio for the lagged correction is below 0.05 for each g, at J = 6, seeds 1, 2.
Refuted by: a ratio at or above 0.05 for some g and seed with the correction as built.
Possible because: the reshapes or the legs' orientation could be wrong in a way the global average does not see.
Positive control: the same correction with its coordinate-2 leg sign flipped gives a ratio above 0.2 for some g.
Refuted by: every ratio below 0.2 with the leg's sign flipped, so that the check could not see a misoriented leg.
Forced by counts: nothing in the sizes forces either ratio; the quadrature error is of order the profiles' kinks.
"""
import importlib.util
import json
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve()
_spec = importlib.util.spec_from_file_location('lagged_test', HERE.parent / 'lagged_test.py')
lt = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(lt)

GS = {'x^2': (lambda x, y: 2 * x, lambda x, y: 0 * y),
      'xy': (lambda x, y: y, lambda x, y: x),
      'y^3': (lambda x, y: 0 * x, lambda x, y: 3 * y ** 2),
      'sin3x cos2y': (lambda x, y: 3 * np.cos(3 * x) * np.cos(2 * y), lambda x, y: -2 * np.sin(3 * x) * np.sin(2 * y)),
      'x^2 y^2': (lambda x, y: 2 * x * y ** 2, lambda x, y: 2 * x ** 2 * y)}


def ratios(w, G):
    c = (np.arange(G) + 0.5) / G
    X, Y = np.meshgrid(c, c)                     # F[k][y, x]
    out = {}
    for name, (gx, gy) in GS.items():
        a, b = gx(X, Y), gy(X, Y)
        num = float((w[0] * a + w[1] * b).sum())
        den = float((np.abs(w[0] * a) + np.abs(w[1] * b)).sum())
        out[name] = abs(num) / max(den, 1e-300)
    return out


def main():
    J = 6
    N = 16 * 4 ** J
    G = 1 << (J + 1)
    res = {}
    for seed in (1, 2):
        dy, lg, _ = lt.fields(J, N, seed)
        res[f'seed {seed}'] = ratios(lg - dy, G)
    # positive control: rebuild with the coordinate-2 leg of every coordinate-1 exchange negated
    orig = lt.unit_shapes
    lt.unit_shapes = lambda m: (orig(m)[0], -orig(m)[1])
    dy, lg, _ = lt.fields(J, N, 1)
    lt.unit_shapes = orig
    res['flipped leg, seed 1'] = ratios(lg - dy, G)
    for k, v in res.items():
        print(k, json.dumps({g: round(x, 5) for g, x in v.items()}))
    ok = all(x < 0.05 for k, v in res.items() if k.startswith('seed') for x in v.values())
    pos = any(x > 0.2 for x in res['flipped leg, seed 1'].values())
    print(json.dumps({'control': ok, 'positive_control': pos}))


if __name__ == '__main__':
    main()
