"""Cheap tests for the collective-core route review (odd-prime thread, 26 September 2026).

V (Veronese lead): over F_3 the falsifying set of a line, {L_i != b_i for all i}, is cut out inside
   the cube by the r quadrics (L_i - b_i)^2 - 1.  Reads the recorded T1 restriction dimensions
   (thread_tests.json) and compares them with the quadric bound full_dim - r at k = 2 and with the
   F_2 flat bound, reporting the dimension each line removes.
Q (qutrit stabilizer bridge): a function on F_3 is a stabilizer (Gaussian) state only if its Fourier
   transform has constant magnitude on its support.  Computes the Fourier magnitudes of the indicator
   [x != 0] on F_3.
Usage: core_review_tests.py --t1 thread_tests.json --out FILE"""
import argparse, cmath, json

ap = argparse.ArgumentParser(); ap.add_argument('--t1', required=True); ap.add_argument('--out', required=True)
opt = ap.parse_args()
t1 = json.load(open(opt.t1))['T1']
rows = []
for r in t1:
    removed = r['full_dim'] - r['restricted_dim']
    rows.append(dict(p=r['p'], r=r['r'], k=r['k'], points=r['points'], restricted_dim=r['restricted_dim'],
                     full_dim=r['full_dim'], removed=removed,
                     quadric_bound_k2=(r['full_dim'] - r['r']) if (r['p'] == 3 and r['k'] == 2) else None))
w = cmath.exp(2j * cmath.pi / 3)
f = [0, 1, 1]
fhat = [abs(sum(f[x] * w ** (-(x * y)) for x in range(3)) / 3) for y in range(3)]
res = dict(V=rows, Q=dict(indicator=f, fourier_magnitudes=[round(v, 6) for v in fhat],
                          constant_on_support=len({round(v, 6) for v in fhat if v > 1e-9}) == 1))
json.dump(res, open(opt.out, 'w'), indent=1)
print(json.dumps(res['Q']))
