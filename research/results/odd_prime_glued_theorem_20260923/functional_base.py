"""Nonvacuity check for a degree-4 glued test: is functional PHP^{n+1}_n (weak base plus row collisions) refuted by its
own degree-D PC closure?  Usage: python3 functional_base.py --cases 5:4,6:4 --out OUT.json"""
import argparse, json, os, sys, time
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.join(HERE, '..', 'odd_prime_local_falls_20260923'))
from local_falls import Closure, QSpace, base_rows
ap = argparse.ArgumentParser(); ap.add_argument('--cases', default='5:4,6:4'); ap.add_argument('--out', required=True); a = ap.parse_args(); res = []
for cs in a.cases.split(','):
    n, D = map(int, cs.split(':')); t = time.time(); sp = QSpace(n, D)
    fun = [{(i * n + j, i * n + k): 1} for i in range(n + 1) for j in range(n) for k in range(j + 1, n)]
    C = Closure(sp, 12); C.add(base_rows(n) + fun); s = C.split()
    res.append(dict(n=n, D=D, columns=int(sp.cols), **s, seconds=round(time.time() - t, 1))); print(res[-1], flush=True)
    json.dump(res, open(a.out, 'w'), indent=1)
