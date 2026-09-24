"""Boolean-cube form of the canonical family's locality defect.

For the canonical family (hyperplanes y_i = 0, i < s, and y_1+...+y_s = c in F_3^s), the defect of
I_e(n U_b) = sum_b I_e(U_b) equals, on C = {0,1}^s (y = 1 + x) and W_r = {x : |x| = r mod 3}, r = c - s mod 3:
  def(s, r, e) = dim{f in F_e(C) : supp f in W_r} - dim chi_W F_{e-2}(C),   chi_W = 1_{W_r}.
Computed over F_3 with multilinear monomials.  Usage: python3 weight_class.py OUT.json smin smax"""
import itertools, json, sys, time
import numpy as np
exec(open(__file__.replace('weight_class.py', 'form_locality.py')).read().split('def indep_t')[0])
out, smin, smax = sys.argv[1], int(sys.argv[2]), int(sys.argv[3]); res = []
for s in range(smin, smax + 1):
    pts = list(itertools.product((0, 1), repeat=s)); t0 = time.time()
    for r in range(3):
        W = np.array([int(sum(x) % 3 == r) for x in pts], dtype=np.int64); off = [x for x in pts if sum(x) % 3 != r]
        defects = []
        for e in range(1, s + 1):
            mons = [T for d in range(e + 1) for T in itertools.combinations(range(s), d)]
            ev = lambda X, ms: np.array([[int(all(x[j] for j in T)) for x in X] for T in ms], dtype=np.int64)
            sup = len(null_left(ev(off, mons))) if off else len(mons)
            low = [T for T in mons if len(T) <= e - 2]
            img = rank((ev(pts, low) * W) % 3) if low else 0
            defects.append(sup - img)
        row = dict(s=s, r=r, c=(r + s) % 3, defects=defects, seconds=round(time.time() - t0, 1))
        res.append(row); print(json.dumps(row), flush=True); json.dump(res, open(out, 'w'), indent=1)
