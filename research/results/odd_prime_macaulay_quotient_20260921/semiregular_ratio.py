"""Heuristic orientation for the degree-k Macaulay quotient of h quadrics in s Boolean variables.

Computes exactly, by truncated series convolution, the coefficients of
  model B: (1+t)^s (1+t^2)^(-h)   (Boolean semi-regular model used in earlier entries)
  model F: (1+t)^s (1-t^2)^h      (maximal-rank model in F[x]/(x_u^2), no trivial syzygies)
and reports (i) coefficient/C(s,k) against exp(-h k^2/s^2), (ii) the first degree with a
nonpositive coefficient, and x_reg = h*dreg^2/s^2. These are models, not facts about any block.
Usage: python3 semiregular_ratio.py --out PATH
"""
import argparse, json, math

def series(s, h, K, model):
    a = [math.comb(s, n) for n in range(K + 1)]
    if model == 'B':
        g = [0] * (K + 1)
        for j in range(K // 2 + 1):
            g[2 * j] = (-1) ** j * math.comb(h + j - 1, j)
    else:
        g = [0] * (K + 1)
        for j in range(min(h, K // 2) + 1):
            g[2 * j] = (-1) ** j * math.comb(h, j)
    return [sum(a[n - m] * g[m] for m in range(0, n + 1, 2)) for n in range(K + 1)]

def first_nonpos(c):
    for n, v in enumerate(c):
        if v <= 0:
            return n
    return None

ap = argparse.ArgumentParser(); ap.add_argument('--out', required=True); args = ap.parse_args()
s, K = 3000, 400
out = dict(s=s, K=K, ratio_rows=[], regularity_rows=[])
for k in (40, 80):
    for x in (0.25, 0.5, 1.0, 1.5, 2.0, 3.0):
        h = round(x * s * s / (k * k))
        row = dict(k=k, h=h, x=h * k * k / s**2, exp_minus_x=math.exp(-h * k * k / s**2))
        for m in ('B', 'F'):
            c = series(s, h, k, m)[k]
            row['ratio_' + m] = (c / math.comb(s, k)) if c > 0 else 0.0
        out['ratio_rows'].append(row); print(row)
for h in (200, 800, 3200, 12800):
    row = dict(h=h, s_over_sqrt_h=s / math.sqrt(h))
    for m in ('B', 'F'):
        d = first_nonpos(series(s, h, K, m))
        row['dreg_' + m] = d
        row['x_reg_' + m] = h * d * d / s**2 if d is not None else None
    out['regularity_rows'].append(row); print(row)
open(args.out, 'w').write(json.dumps(out, indent=1))
