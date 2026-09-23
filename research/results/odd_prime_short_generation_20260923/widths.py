"""Widths of the forms used by short_generation.py and second_degree_lift.py (same seeds and generator).
Width: minimum over nonzero u in F_3^r, up to scalar, of the number of rows where sum_j u_j f^(j)_i is
not constant.  Usage: python3 widths.py OUT.json"""
import itertools, json, random, sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from short_generation import make_forms
def width(F, R, N, r):
    best = None
    for u in itertools.product(range(3), repeat=r):
        if not any(u) or next(x for x in u if x) != 1: continue
        act = sum(1 for i in range(R) if len({sum(u[j] * F[j][i][w] for j in range(r)) % 3 for w in range(N)}) > 1)
        best = act if best is None else min(best, act)
    return best
out = {'second_degree_lift': [], 'short_generation': []}
for kind in ('generic', 'rowdep'):
    for R in (5, 6, 7, 8):
        out['second_degree_lift'].append(dict(kind=kind, rows=R, labels=7, seed=1, width=width(make_forms(kind, R, 7, 3, random.Random(1)), R, 7, 3)))
    for (R, N) in ((8, 7), (10, 7), (8, 9)):
        for s in (1, 2):
            out['short_generation'].append(dict(kind=kind, rows=R, labels=N, forms=3, seed=s, width=width(make_forms(kind, R, N, 3, random.Random(s)), R, N, 3)))
for r in (2, 4):
    out['short_generation'].append(dict(kind='generic', rows=9, labels=7, forms=r, seed=1, width=width(make_forms('generic', 9, 7, r, random.Random(1)), 9, 7, r)))
json.dump(out, open(sys.argv[1], 'w'), indent=1); print(out)
