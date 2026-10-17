#!/usr/bin/env python3
"""No statement tested: additivity witnesses for the lagged restoring flow, with lagged_test.py's own functions
(imported unchanged).
(1) One exchange with the script's unit shapes on a pair whose coordinate-1 field is constant on each child and whose
coordinate 2 is zero: amplitudes for child means (2,-2), (1,1) and their sum (3,-1), with the descent's gradient at the
returned amplitude (its stationarity residual). This is a map of the running field, not of the counts.
(2) In the counts: the dyadic flow is linear in the cell counts (its excesses are), so the lagged field L(c) built from
a count array c is tested for additivity, L(c1 + c2) against L(c1) + L(c2), on two random count arrays at J = 3; the
dyadic field's own additivity defect is printed beside it as the control (expected at rounding level)."""
import importlib.util
import json
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve()
_spec = importlib.util.spec_from_file_location('lagged_test', HERE.parent / 'lagged_test.py')
lt = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(lt)
sr = lt.sr

out = {}
m = 8
main, other = lt.unit_shapes(m)
for cb, ct in ((2, -2), (1, 1), (3, -1)):
    A = np.concatenate([np.full((1, m, m), float(cb)), np.full((1, m, m), float(ct))])[None]
    B = np.zeros_like(A)
    a, _ = lt.descend(A, B, main[None], other[None], iters=60)
    x = A + a[0] * main[None]
    y = B + a[0] * other[None]
    grad = float(4 * ((x ** 3) * main).sum() + 4 * ((y ** 3) * other).sum())
    out[f'(1) ({cb},{ct})'] = {'amplitude': round(float(a[0]), 6), 'gradient': grad}


def build(cells, J, lagged):
    G = 1 << (J + 1)
    F = np.zeros((2, G, G))
    for j in range(J):
        sr.level_step(F, cells, j, J, G, False, {})
        if lagged:
            lt.lagged_step(F, j, G, {})
    return F


J = 3
rng = np.random.default_rng(5)
c1 = rng.multinomial(16 * 4 ** J, np.full(4 ** J, 4.0 ** -J)).reshape(1 << J, 1 << J)
c2 = rng.multinomial(16 * 4 ** J, np.full(4 ** J, 4.0 ** -J)).reshape(1 << J, 1 << J)
for name, lagged in (('dyadic', False), ('lagged', True)):
    s, f1, f2 = build(c1 + c2, J, lagged), build(c1, J, lagged), build(c2, J, lagged)
    out[f'(2) {name}: max |L(c1+c2) - L(c1) - L(c2)| / max |L(c1+c2)|'] = float(np.abs(s - f1 - f2).max() / np.abs(s).max())
print(json.dumps(out, indent=1))
