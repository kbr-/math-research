"""Degreewise locality for the canonical family of s+1 hyperplanes in general position in F_3^s:
B_i = {y_i = v_i} (i < s), B_s = {y_1 + ... + y_s = c}; every s of the linear parts are independent (t = s).
Tested statement: I_e(n U_b) = sum_b I_e(U_b) for all e (form-space core of conj:t-wise-locality, k = 1).
By the symmetry y_i -> y_i - v_i the family depends only on c' = c - sum v_i; both c' values classes are scanned.
Usage: python3 canonical_family.py OUT.json smax"""
import itertools, json, sys
import numpy as np
exec(open(__file__.replace('canonical_family.py', 'form_locality.py')).read().split('out = sys.argv[1]')[0])
out, smax = sys.argv[1], int(sys.argv[2]); res = []
for s in range(2, smax + 1):
    pts = list(itertools.product(range(p), repeat=s)); mons_all = sorted(itertools.product(range(p), repeat=s), key=sum)
    for c in range(p):
        forb = lambda y, b: (y[b] == 0) if b < s else (sum(y) % p == c)
        Z = [y for y in pts if not any(forb(y, b) for b in range(s + 1))]; defects = []
        for e in range(1, (p - 1) * s + 1):
            mons = [m for m in mons_all if sum(m) <= e]
            ev = lambda X: np.array([[int(np.prod([pow(y[i], m[i], p) for i in range(s)]) % p) for y in X] for m in mons], dtype=np.int64)
            IZ = null_left(ev(Z)) if Z else np.eye(len(mons), dtype=np.int64)
            sm = rank(np.vstack([null_left(ev([y for y in pts if not forb(y, b)])) for b in range(s + 1)]))
            defects.append(len(IZ) - sm)
        row = dict(s=s, c=c, allowed=len(Z), defects=defects); res.append(row); print(json.dumps(row), flush=True)
        json.dump(res, open(out, 'w'), indent=1)
