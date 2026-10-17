"""The weak-form divergence ratio of research/results/ultimate_matching_lagged_restoring_20261017/divergence_check.py,
for a correction w sampled at the positions' centres: |sum w . grad g| / sum |w| |grad g| for five smooth g.

No statement tested: a helper of restoring_flow_test.py's divergence control.
"""
import numpy as np

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
