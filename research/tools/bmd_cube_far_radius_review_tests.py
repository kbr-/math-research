"""Cheap tests of the far-radius review (3 October 2026; cycle bmd-20261003-zzs). Reads saved hull data only.

1. Middle steps (falsification attempt of the step law beyond l = 1): for the l = 2 hulls (middle-hull.txt, e = 3, 4, 5;
   N = R_e + 7/2), the eight slopes u_i give steps N (u_(i+1) - u_i); report them in units of log N, against 4.
2. Pair symmetry (Lee-Yang bridge): the count predicts c_i + c_(3-i) = -1 (log-radii symmetric about -(1/2) log N / N,
   the broken t <-> 1/t symmetry x <-> -1-x). Report N (u_i + u_(3-i)) / log N at the last step, e = 4..11.
3. Kurtz margin (outside lead): a quartic sum a_m T^m with positive a_m and a_m^2 > 4 a_(m-1) a_(m+1) has distinct real
   roots. With a_m read from the hull, log(a_m^2/(a_(m-1) a_(m+1))) = N (u_m - u_(m-1)) (T = t^N); report its minimum
   against log 4. Signs are not tested.
"""
import argparse
import math
import re

ap = argparse.ArgumentParser()
ap.add_argument("--last", default="research/results/bmd-20261003-zzp/block-logderiv-2.txt")
ap.add_argument("--middle", default="research/results/bmd-20261003-zzm/middle-hull.txt")
ap.add_argument("--out", required=True)
a = ap.parse_args()
Nf = lambda e: e * (2 * e - 1) + 3.5
out = []

for line in open(a.middle):
    e = int(re.search(r" e=(\d+)", line).group(1))
    edges = [[float(v) for v in p.split(",")] for p in re.findall(r"\[(\d+, -?[0-9.]+)\]", line.split("e*u]", 1)[1])]
    u = [eu / e for _, eu in edges]
    N = Nf(e)
    steps = [N * (u[i + 1] - u[i]) / math.log(N) for i in range(len(u) - 1)]
    out.append(f"middle l=2 e={e}: {len(u)} long edges, steps N du / log N = {[round(s, 3) for s in steps]}, mean {sum(steps) / len(steps):.3f}")

rows, cur = {}, None
for line in open(a.last):
    m = re.match(r"e=(\d+)", line)
    if m:
        cur = int(m.group(1))
        rows[cur] = []
        continue
    rows[cur].append(float(re.search(r"e\*u = (-?[0-9.]+)", line).group(1)))
for e in sorted(rows):
    N = Nf(e)
    u = [x / e for x in rows[e]]
    pair = [N * (u[i] + u[3 - i]) / math.log(N) for i in (0, 1)]
    kurtz = min(N * (u[i + 1] - u[i]) for i in range(3))
    out.append(f"last e={e}: N(u_i + u_(3-i))/log N = {[round(p, 3) for p in pair]}; min N(u_(m)-u_(m-1)) = {kurtz:.2f} vs log 4 = {math.log(4):.2f}")
open(a.out, "w").write("\n".join(out) + "\n")
print("\n".join(out))
