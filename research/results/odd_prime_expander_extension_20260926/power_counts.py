#!/usr/bin/env python3
"""Power of the finite checks for conj:expander-matching-filling (reviewer request, rule 1).

Regenerates the degree-5, 3-expanding samples of matching_complex.py (same seed and order) and, for each, records
whether every row of S has a private hole (lem:private-hole-filling applies directly) and whether an elimination
order exists in every branch (the general class of that lemma). Samples outside both classes are the only ones that
test the conjecture beyond the lemma. Also re-finds and saves one explicit failing graph for the 2|U|-1 condition
and one for 3-expansion with degree-3 rows (hall_slack_test.py, expansion_degree_test.py seeds)."""
import itertools, json, sys
from functools import lru_cache
import numpy as np
sys.path.insert(0, __file__.rsplit('/', 1)[0])
import matching_complex as mc

def all_private(nbrs):
    return all(any(all(t not in nbrs[j] for j in range(len(nbrs)) if j != i) for t in nbrs[i]) for i in range(len(nbrs)))

def eliminable(nbrs):
    @lru_cache(maxsize=None)
    def ok(rows):
        rows = list(rows)
        if len(rows) == 0:
            return True
        if len(rows) == 1:
            return len(rows[0]) >= 1
        for a, r in enumerate(rows):
            others = rows[:a] + rows[a + 1:]
            priv = [t for t in r if all(t not in o for o in others)]
            if not priv:
                continue
            t0 = priv[0]
            if all(ok(tuple(sorted((frozenset(o - {t}) for o in others), key=sorted))) for t in r if t != t0):
                return True
        return False
    return ok(tuple(sorted(nbrs, key=sorted)))

rng = np.random.default_rng(20260926)
out = {'by_s': [], 'examples': {}}
for s in (2, 3, 4, 5):
    for h in (3 * s, 3 * s + 2, 4 * s):
        if h < 5:
            continue
        n = allp = elim = 0; tries = 0
        while n < (60 if s < 5 else 30) and tries < 200000:
            tries += 1
            nbrs = [frozenset(rng.choice(h, size=5, replace=False).tolist()) for _ in range(s)]
            if not mc.expands(nbrs):
                continue
            n += 1
            a = all_private(nbrs); e = a or eliminable(nbrs)
            allp += a; elim += e
        row = {'s': s, 'holes_drawn_from': h, 'samples': n, 'all_rows_private': allp, 'eliminable': elim,
               'outside_lemma_class': n - elim}
        out['by_s'].append(row); print(row, flush=True)

# explicit failing graphs
def find(cond, deg_lo, deg_hi, s, hmin, seed):
    g = np.random.default_rng(seed)
    for _ in range(20000):
        h = hmin + int(g.integers(0, 3))
        nbrs = [frozenset(g.choice(h, size=int(g.integers(deg_lo, deg_hi + 1)), replace=False).tolist()) for _ in range(s)]
        if cond(nbrs) and mc.reduced_homology(nbrs, s - 2) != 0:
            return [sorted(x) for x in nbrs]
    return None
slack = lambda nb: all(len(set().union(*[nb[i] for i in U])) >= 2 * len(U) - 1 for u in range(1, len(nb) + 1) for U in itertools.combinations(range(len(nb)), u))
exp3 = lambda nb: all(len(set().union(*[nb[i] for i in U])) >= 3 * len(U) for u in range(1, len(nb) + 1) for U in itertools.combinations(range(len(nb)), u))
out['examples']['hall_slack_2U-1_s3'] = find(slack, 2, 5, 3, 5, 1)
out['examples']['expansion3_deg3to5_s4'] = find(exp3, 3, 5, 4, 12, 2)
for k, v in out['examples'].items():
    if v:
        out['examples'][k] = {'rows': v, 'H_s-2': mc.reduced_homology([frozenset(x) for x in v], len(v) - 2)}
print(json.dumps(out['examples']), flush=True)
if '--out' in sys.argv:
    json.dump(out, open(sys.argv[sys.argv.index('--out') + 1], 'w'), indent=1)
