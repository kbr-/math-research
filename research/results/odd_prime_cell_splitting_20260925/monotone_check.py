#!/usr/bin/env python3
"""How often the empty fiber's vanishing tops lie in every row fiber's (cor:monotone-fiber-recursion), p = 3.

Part 1, cell forms: the six sets Q of cell_split_check.py (m = 3, N = 5, column j = 0): for d = 1..3,
  is A_d(Q^e) contained in A_d(Q^{(i)}) for every row i?  (also the reverse inclusions)
Part 2, column members at N = 10 (fiber_check.py's members, hole 0, e = 1, 2, links |S| <= 2):
  per link, is a_S(Z^0) contained in a_S(Z^1), or the reverse, or neither; reported by link size.
"""
import itertools, json, sys
import numpy as np
here = __file__.rsplit('/', 1)[0]
sys.path.insert(0, here); sys.path.insert(0, here + '/../odd_prime_closure_route_review_20260925')
from vanishing_tops import rank3
from cell_split_check import tops_space, embed, monomials
import fiber_check

def contained(A, B):
    if len(A) == 0:
        return True
    if len(B) == 0:
        return False
    return rank3(np.vstack([A, B])) == rank3(B)

out = {'cell': [], 'column': {}}
m, N = 3, 5
rng = np.random.default_rng(20260925)
for trial in range(6):
    F = [(rng.integers(0, 3, size=(m, N)), int(rng.integers(0, 3))) for _ in range(3)]
    val = lambda pt, f: (sum(f[0][r][h] for h, r in pt.items()) + f[1]) % 3
    ncl = 2 if trial < 2 else 5
    cls = [(int(a), int(b), int(rng.integers(0, 3)), int(rng.integers(0, 3))) for a, b in [(0, 1), (0, 2), (1, 2), (2, 0), (1, 0)][:ncl]]
    injective = trial % 2 == 1
    allP = [{h: r for h, r in enumerate(st) if r >= 0} for st in itertools.product(range(-1, m), repeat=N)]
    Q = [pt for pt in allP if not any(val(pt, F[i]) == a and val(pt, F[j]) != b for (i, j, a, b) in cls)
         and (not injective or len(set(pt.values())) == len(pt))]
    rest = list(range(1, N))
    cbc = {h: [(r, h) for r in range(m)] for h in rest}
    fib = {'e': [{h: r for h, r in pt.items() if h != 0} for pt in Q if 0 not in pt]}
    for i in range(m):
        fib[i] = [{h: r for h, r in pt.items() if h != 0} for pt in Q if pt.get(0) == i]
    rec = {'clauses': ncl, 'row_injective': injective}
    for d in (1, 2, 3):
        mus = [mu for mu in monomials(cbc, d) if len(mu) == d]
        A = {s: embed(*tops_space(fib[s], cbc, d), mus) for s in fib}
        rec[d] = {'empty_in_all_rows': all(contained(A['e'], A[i]) for i in range(m)),
                  'rows_in_empty': all(contained(A[i], A['e']) for i in range(m)),
                  'dim_empty': int(rank3(A['e'])) if len(A['e']) else 0}
    out['cell'].append(rec)
    print('cell', trial, rec, flush=True)
for name, allowed in fiber_check.members.items():
    pts = np.array([c for c in itertools.product((0, 1), repeat=10) if sum(c) % 3 == 11 % 3 and allowed(c)])
    holes = list(range(1, 10))
    Z0 = pts[pts[:, 0] == 0][:, holes]; Z1 = pts[pts[:, 0] == 1][:, holes]
    stats = {}
    for e in (1, 2):
        for ysz in (0, 1, 2):
            c = {'0_in_1': 0, '1_in_0': 0, 'equal': 0, 'neither': 0, 'links': 0}
            for S in itertools.combinations(holes, ysz):
                rest = [h for h in holes if h not in S]
                def t(Zf):
                    sel = Zf[np.all(Zf[:, [holes.index(h) for h in S]] == 1, axis=1)] if S else Zf
                    return fiber_check.tops(sel[:, [holes.index(h) for h in rest]], rest, e)[1]
                a0, a1 = t(Z0), t(Z1)
                i01, i10 = contained(a0, a1), contained(a1, a0)
                c['links'] += 1
                c['equal' if (i01 and i10) else '0_in_1' if i01 else '1_in_0' if i10 else 'neither'] += 1
            stats[f'e={e} |S|={ysz}'] = c
    out['column'][name] = stats
    print('column', name, stats, flush=True)
if '--out' in sys.argv:
    json.dump(out, open(sys.argv[sys.argv.index('--out') + 1], 'w'), indent=1)
