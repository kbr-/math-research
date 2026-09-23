"""Writes Macaulay2 systems (for weak_hf.py) for the pencil classes at n = 9 with c_min >= 4, split into batches, plus the
model HF and c_min per class.  Usage: python3 make_n9_systems.py --batches 3 --prefix OUTPREFIX"""
import json, os, sys
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); RES = os.path.join(HERE, '..')
a = dict(zip(sys.argv[1::2], sys.argv[2::2])); nb = int(a['--batches']); pre = a['--prefix']
p = os.path.join(RES, 'odd_prime_pencil_freeness_20260924', 'pencil_exhaustive.py'); src = open(p).read()
parts = src.split("DIRS = [(1, 0)")[0].split("a = dict(zip(sys.argv[1::2], sys.argv[2::2]))")
ns_ = {'__file__': p}; exec(parts[0] + "T = 3\n" + parts[1].split("\n", 1)[1], ns_)
DIRS = [(1, 0), (0, 1), (1, 1), (1, 2)]; n = 9; sel = []
for v in ns_['classes'](n):
    holes = [q for q, m in zip(ns_['PTS'], v) for _ in range(m)]
    vals = [[(u[0] * x + u[1] * y) % 3 for x, y in holes] for u in DIRS]
    if any(len(set(vv)) == 1 for vv in vals): continue
    cmin = min(n - max(vv.count(z) for z in range(3)) for vv in vals)
    if cmin < 4: continue
    phi1 = [x for x, y in holes]; phi2 = [y for x, y in holes]
    sel.append(dict(counts=v, c_min=cmin, phi1=phi1, phi2=phi2, model_H=ns_['hf'](n, [[1] * n, phi1, phi2])))
print('selected classes', len(sel))
json.dump(sel, open(pre + '_classes.json', 'w'), indent=1)
for b in range(nb):
    chunk = sel[b::nb]; sysm = {'A': []} if b == 0 else {}
    for k, c in enumerate(sel):
        if k % nb != b: continue
        sysm[f'c{k}'] = [[c['phi1']] * (n + 1), [c['phi2']] * (n + 1)]
    json.dump(sysm, open(pre + f'_batch{b}.json', 'w'))
