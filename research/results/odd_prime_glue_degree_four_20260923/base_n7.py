"""Nonvacuity for the degree-4 glue: is functional PHP^{n+1}_n refuted by its own degree-D closure (FSpace, all-C
closure)?  Usage: python3 base_n7.py --cases 6:4,7:4 --out OUT.json"""
import argparse, json, os, sys, time
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
from fspace import FSpace, base_rows, Closure
ap = argparse.ArgumentParser(); ap.add_argument('--cases', default='6:4,7:4'); ap.add_argument('--out', required=True); a = ap.parse_args(); res = []
for cs in a.cases.split(','):
    n, D = map(int, cs.split(':')); t = time.time(); sp = FSpace(n, D); t1 = time.time() - t
    C = Closure(sp, 14); C.add(base_rows(n)); s = C.split()
    res.append(dict(n=n, D=D, columns=sp.cols, setup_s=round(t1, 1), **s, seconds=round(time.time() - t, 1))); print(res[-1], flush=True)
    json.dump(res, open(a.out, 'w'), indent=1)
