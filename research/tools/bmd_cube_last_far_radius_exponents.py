"""Predicted radius exponents of the four last-step far circles (3 October 2026; cycle bmd-20261003-zzr).

Tested statement (conj:cube-last-far-radius-step): N u_i = (4i - 13/2) log N + d_i + o(1), i = 0..3, N = R_e + 7/2,
for the long-edge slopes -u_i of P(t) = (1-t)^d W_(b-1)(t/(1-t)), as the leading-order count of the multilinear
expansion predicts; in particular the steps N(u_(i+1) - u_i) = 4 log N + O(1). With the slope fixed,
z_i = N u_i - c_i log N must converge; we fit z_i = d_i + f_i/e and report residuals, against the same fits with the
slopes replaced by c_i +- 1/2, and the steps against 3.5 and 4.5 (controls: a wrong slope leaves a log N drift that the
1/e term cannot absorb).
Input: e*u values of research/results/bmd-20261003-zzp/block-logderiv-2.txt (e = 4..11, exact hulls).
"""
import argparse
import math
import re

import numpy as np

ap = argparse.ArgumentParser()
ap.add_argument("--src", default="research/results/bmd-20261003-zzp/block-logderiv-2.txt")
ap.add_argument("--out", required=True)
a = ap.parse_args()

rows, cur = {}, None
for line in open(a.src):
    m = re.match(r"e=(\d+)", line)
    if m:
        cur = int(m.group(1))
        rows[cur] = []
        continue
    rows[cur].append(float(re.search(r"e\*u = (-?[0-9.]+)", line).group(1)))
es = sorted(rows)
assert all(len(rows[e]) == 4 for e in es)
Nf = lambda e: e * (2 * e - 1) + 3.5
out = []
for i in range(4):
    y = np.array([rows[e][i] / e * Nf(e) for e in es])
    L = np.array([math.log(Nf(e)) for e in es])
    for dc in (0.0, -0.5, 0.5):
        c = 4 * i - 6.5 + dc
        z = y - c * L
        X = np.array([[1.0, 1.0 / e] for e in es])
        coef = np.linalg.lstsq(X, z, rcond=None)[0]
        r = z - X @ coef
        tag = "predicted" if dc == 0 else "control"
        out.append(f"circle {i}: slope {c:+.1f} ({tag}): z = N u - c log N = {[round(v, 3) for v in z]}; "
                   f"fit z = {coef[0]:.3f} + {coef[1]:.3f}/e, max residual {abs(r).max():.4f}")
for i in range(3):
    y = np.array([(rows[e][i + 1] - rows[e][i]) / e * Nf(e) for e in es])
    L = np.array([math.log(Nf(e)) for e in es])
    for c in (4.0, 3.5, 4.5):
        z = y - c * L
        X = np.array([[1.0, 1.0 / e] for e in es])
        coef = np.linalg.lstsq(X, z, rcond=None)[0]
        r = z - X @ coef
        tag = "predicted" if c == 4.0 else "control"
        out.append(f"step {i}->{i + 1}: N (u_(i+1) - u_i) - {c} log N ({tag}) = {[round(float(v), 3) for v in z]}; "
                   f"fit {coef[0]:.3f} + {coef[1]:.3f}/e, max residual {abs(r).max():.4f}")
open(a.out, "w").write("\n".join(out) + "\n")
print("\n".join(out))
