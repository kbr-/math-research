"""Arora-Ge bridge test (DAG review, 26 Sept 2026): compare the measured Hilbert function HF(Z,k) of a line's
falsifying set Z = {L_i != 0} (slot Hilbert entry data) with two series predictions:
  semi-regular Boolean model (Bardet-Faugere-Salvy): coefficients of (1+t)^v / (1+t^2)^r, cumulated to k,
      as for r generic 'Boolean' quadrics q_i with q_i^2 = -q_i (here q_i = L_i^2 - 1, values 0, -1 on the cube);
  pair-product model: ((1+2t)/(1+t)^2)^r (1+t)^v, cumulated (exact for x_a + x_b on disjoint pairs).
Only regime cases (points >= 2 * full) are compared."""
import json
from math import comb
from pathlib import Path
D = Path(__file__).parent.parent / 'odd_prime_slot_hilbert_20260926'


def series_mul(a, b, n):
    return [sum(a[i] * b[j - i] for i in range(j + 1) if i < len(a) and j - i < len(b)) for j in range(n + 1)]


def cum(c, k):
    return sum(c[: k + 1])


def semireg(v, r, k):
    inv = [0] * (k + 1)                  # 1/(1+t^2)^r = sum_m (-1)^m C(r+m-1, m) t^{2m}
    for m in range(k // 2 + 1):
        inv[2 * m] = (-1) ** m * comb(r + m - 1, m)
    c = series_mul([comb(v, j) for j in range(k + 1)], inv, k)
    out = []                              # truncate at the first nonpositive coefficient
    for x in c:
        if x <= 0:
            break
        out.append(x)
    return sum(out)


def pairprod(v, r, k):
    f = [1, 2]; g = [1]
    for _ in range(r):
        g = series_mul(g, f, k)
    g = series_mul(g, [comb(v - 2 * r, j) for j in range(k + 1)], k)
    return cum(g, k)


rows = {}
for f in ['hf_small.json', 'hf_large.json', 'hf_span.json']:
    for c in json.loads((D / f).read_text()):
        rows[(c['v'], c['k'], c['r'], c['seed'])] = c
print('v k r seed full HF_measured semireg_pred pairprod_pred')
for key in sorted(rows):
    c = rows[key]
    if c['points'] < 2 * c['full']:
        continue
    v, k, r, _ = key
    print(*key, c['full'], c['hf'] if 'hf' in c else c['full'] - c['removed'], semireg(v, r, k), pairprod(v, r, k))
