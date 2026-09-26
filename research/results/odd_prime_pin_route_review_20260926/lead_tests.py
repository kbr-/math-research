"""Cheap tests for the pin route review (26 September 2026).

1. Green's hyperplane restriction theorem: for a general linear form l on a standard graded
   algebra A, dim (A/lA)_d <= (dim A_d)_<d> (Macaulay's lower operator). Compare with the
   freeness prediction over F_3[l]/(l^3), HS_A/(1+q+q^2), on the recorded weak top algebra
   series HS_A = (1, 63, 1656, 22929) at n = 8 (many-form freeness entry). Green's bound is an
   upper bound on the quotient, so it can only be met, never contradict freeness from below.
2. Barvinok's interpolation premise under a mod-3 constraint: zeros of
   f_n(z) = sum_{k = 0 mod 3} C(n,k) z^k = ((1+z)^n + (1+wz)^n + (1+w^2 z)^n)/3; report the least
   argument |arg z| of a zero and the least distance of a zero from [0, infinity).
"""
import json, sys
from math import comb
import numpy as np

def macaulay_rep(a, d):
    rep = []
    while a > 0 and d > 0:
        k = d
        while comb(k + 1, d) <= a:
            k += 1
        rep.append((k, d)); a -= comb(k, d); d -= 1
    return rep

def lower(a, d):
    return sum(comb(k - 1, i) for k, i in macaulay_rep(a, d))

hs = [1, 63, 1656, 22929]
pred = []
for d, a in enumerate(hs):
    pred.append(a - (pred[d-1] if d >= 1 else 0) - (pred[d-2] if d >= 2 else 0))
green = [None] + [lower(hs[d], d) for d in range(1, 4)]
out = {'hs': hs, 'freeness_prediction': pred, 'green_bound': green,
       'prediction_within_bound': all(pred[d] <= green[d] for d in range(1, 4))}
zeros = {}
w = np.exp(2j * np.pi / 3)
for n in (30, 60, 90):
    coeffs = [comb(n, k) if k % 3 == 0 else 0 for k in range(n + 1)]
    r = np.roots(coeffs[::-1])
    r = r[np.abs(r) > 1e-12]
    args = np.abs(np.angle(r))
    dist = [abs(z.imag) if z.real >= 0 else abs(z) for z in r]
    zeros[n] = {'least_abs_arg': float(args.min()), 'least_distance_to_positive_axis': float(min(dist)),
                'count': int(len(r))}
out['filtered_zeros'] = zeros
json.dump(out, open(sys.argv[1], 'w'), indent=1)
print(json.dumps(out))
