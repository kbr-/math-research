"""Which systems of r column-type forms at n = 8 have every nonzero F_3-combination of column count >= 5 (max value
multiplicity <= 3)?  The holes give a multiset of 8 points of F_3^r; a functional's value classes are three parallel
hyperplanes.  r = 2: all multisets of 8 points of F_3^2.  r = 3: all 8-subsets of F_3^3 (a repeated point is excluded
by counting, see the entry).  Usage: python3 classify_configs.py --out JSON"""
import itertools, json, sys
import numpy as np
out = {}
for r in (2, 3):
    pts = np.array(list(itertools.product(range(3), repeat=r)))
    funcs = [np.array(f) for f in itertools.product(range(3), repeat=r) if any(f) and next(x for x in f if x) == 1]
    V = np.stack([(pts @ f) % 3 for f in funcs])            # (functionals, points)
    ok = []
    combos = itertools.combinations_with_replacement(range(len(pts)), 8) if r == 2 else itertools.combinations(range(len(pts)), 8)
    batch = []
    def flush(batch):
        B = np.array(batch); vals = V[:, B]                  # (funcs, batch, 8)
        cnt = np.stack([(vals == v).sum(axis=2) for v in range(3)], axis=-1).max(axis=-1)   # (funcs, batch)
        good = (cnt <= 3).all(axis=0)
        return [tuple(int(x) for x in b) for b, gd in zip(B, good) if gd]
    total = 0
    for S in combos:
        batch.append(S); total += 1
        if len(batch) == 200000: ok += flush(batch); batch = []
    if batch: ok += flush(batch)
    out[r] = dict(candidates=total, good=len(ok), examples=[[pts[i].tolist() for i in S] for S in ok[:3]],
                  all_distinct_missing_one=all(len(set(S)) == 8 for S in ok) if r == 2 else None)
    print(r, out[r]['candidates'], out[r]['good'], out[r]['all_distinct_missing_one'], flush=True)
json.dump(out, open(sys.argv[sys.argv.index('--out') + 1], 'w'), indent=1)
