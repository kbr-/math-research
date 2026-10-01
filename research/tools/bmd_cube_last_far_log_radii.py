"""Scale law of the four far-root circle radii at the last even-peeling step (3 October 2026; cycle bmd-20261003-zzq).

Tested statement (conj:cube-last-far-log-radii): the long-edge slopes -u_i (i = 0..3) of
P(t) = (1-t)^d W_(b-1)(t/(1-t)) satisfy N u_i = c_i log N + d_i + o(1), N = R_e + 7/2, so the circles lie at
distance Theta(log N / N) from |t| = 1; the competing scale law u_i = C_i / e (e u_i constant) is the falsifier.
Input: the e*u values of research/results/bmd-20261003-zzp/block-logderiv-2.txt (e = 4..11, exact hulls).
Output: least-squares fits of N u_i against (log N, 1), (log e, 1), and the e u_i drift.
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
out = [f"e range {es[0]}..{es[-1]}; e*u_i per e:"]
for e in es:
    out.append(f"  e={e}: e*u = {[round(x, 3) for x in rows[e]]}, N*u/log N = {[round(x / e * Nf(e) / math.log(Nf(e)), 3) for x in rows[e]]}")
for i in range(4):
    y = np.array([rows[e][i] / e * Nf(e) for e in es])
    for name, f in [("log N", lambda e: math.log(Nf(e))), ("log e", lambda e: math.log(e))]:
        X = np.array([[f(e), 1.0] for e in es])
        c = np.linalg.lstsq(X, y, rcond=None)[0]
        r = y - X @ c
        out.append(f"circle {i}: N u = {c[0]:.4f} {name} + {c[1]:.4f}, max residual {abs(r).max():.4f}")
    for name, X, yy in [
        ("e u = C + D/e", np.array([[1.0, 1.0 / e] for e in es]), np.array([rows[e][i] for e in es])),
        ("N u = a sqrt(e) + b", np.array([[math.sqrt(e), 1.0] for e in es]), y),
        ("N u = a N^(1/4) + b", np.array([[Nf(e) ** 0.25, 1.0] for e in es]), y),
        ("N u = c log N + d + f/e", np.array([[math.log(Nf(e)), 1.0, 1.0 / e] for e in es]), y),
    ]:
        c = np.linalg.lstsq(X, yy, rcond=None)[0]
        r = yy - X @ c
        out.append(f"circle {i}: alternative {name}: coefficients {[round(v, 4) for v in c]}, max residual {abs(r).max():.4f}")
    eu = [rows[e][i] for e in es]
    out.append(f"circle {i}: e*u from {eu[0]:.3f} (e={es[0]}) to {eu[-1]:.3f} (e={es[-1]}), ratio {eu[-1] / eu[0]:.3f}")
open(a.out, "w").write("\n".join(out) + "\n")
print("\n".join(out))
