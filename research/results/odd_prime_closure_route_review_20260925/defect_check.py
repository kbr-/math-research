#!/usr/bin/env python3
"""Where the fibers' lattice fails to be distributive, for the two-block pair (one row, p = 3, seconds).

Member: Z = slice minus the forbidden sets of C = chi_0(l0) l1 and C' = chi_1(l0)(l1 - 1) on column
forms l0, l1 (fiber_check.py's phi). At holes j1 = 0, j2 = 1, for each link S and e in {1,2} and each
triple (A, B, C) of the four fibers' vanishing-top subspaces with a distributivity failure, report
  dim A cap (B + C) - dim(A cap B + A cap C)   (the defect, also for the other two orders)
and whether adding the top of the pair's fall, restricted to the link, closes the gap: the fall
C - C' is chi_0(l0) l1 - chi_1(l0)(l1 - 1), a product of degree 2 in the forms by thm:cell-resolvents,
whose degree-2 top in the occupancies (restricted by deleting the link's holes) is computed here.
"""
import itertools, json, sys
import numpy as np
sys.path.insert(0, __file__.rsplit('/', 1)[0])
from vanishing_tops import rref3, nullspace3, rank3
from fiber_check import members, tops, N, m, phi
from distributivity_check import inter, dimsum

name = "two-block pair, k=1, i=i'"
allowed = members[name]
pts = np.array([c for c in itertools.product((0, 1), repeat=N) if sum(c) % 3 == m % 3 and allowed(c)])
j1, j2 = 0, 1
holes = [h for h in range(N) if h not in (j1, j2)]
fib = {(a, b): pts[(pts[:, j1] == a) & (pts[:, j2] == b)][:, holes] for a in (0, 1) for b in (0, 1)}


def fall_top(rest):
    """Degree-2 top of chi_0(l0) l1 - chi_1(l0)(l1 - 1) = -(l0^2 l1) + ... : compute the function on all
    0/1 patterns of the rest holes (other holes set to 0), then its degree-2 top by interpolation."""
    mons = [mu for k in range(3) for mu in itertools.combinations(rest, k)]
    grid = np.array(list(itertools.product((0, 1), repeat=len(rest))))
    full = np.zeros((len(grid), N), dtype=np.int64)
    full[:, rest] = grid
    l0 = (full @ phi[0]) % 3
    l1 = (full @ phi[1]) % 3
    chi = lambda v, a: (1 - (v - a) ** 2) % 3
    f = (chi(l0, 0) * l1 - chi(l0, 1) * (l1 - 1)) % 3
    E = np.array([[int(all(g[rest.index(h)] for h in mu)) for mu in mons] for g in grid], dtype=np.int64)
    # solve E coef = f exactly (multilinear interpolation of degree <= 2 if it exists)
    aug = np.hstack([E, f.reshape(-1, 1)])
    R, piv = rref3(aug)
    if len(mons) in piv:
        return None
    coef = np.zeros(len(mons), dtype=np.int64)
    for i, c in enumerate(piv):
        coef[c] = R[i, -1]
    ti = [i for i, mu in enumerate(mons) if len(mu) == 2]
    return coef[ti].reshape(1, -1)


report = {'failing': 0, 'closed_by_fall_top': 0, 'fall_top_degree_ok': True, 'cases': []}
for e in (2,):
    for ysz in (0, 1, 2):
        for S in itertools.combinations(holes, ysz):
            rest = [h for h in holes if h not in S]
            sub = {}
            for k, Zf in fib.items():
                sel = Zf[np.all(Zf[:, [holes.index(h) for h in S]] == 1, axis=1)] if S else Zf
                sub[k] = tops(sel[:, [holes.index(h) for h in rest]], rest, e)[1]
            ft = fall_top(rest)
            if ft is None:
                report['fall_top_degree_ok'] = False
            for (a, b, c) in itertools.permutations(list(sub), 3):
                if b > c:
                    continue
                A, B, C = sub[a], sub[b], sub[c]
                lhs = rank3(inter(A, np.vstack([B, C]))) if len(A) and (len(B) or len(C)) else 0
                AB, AC = inter(A, B), inter(A, C)
                rhs = dimsum([AB, AC])
                if lhs != rhs:
                    report['failing'] += 1
                    closed = ft is not None and dimsum([AB, AC, ft]) >= lhs and \
                        rank3(np.vstack([inter(A, np.vstack([B, C])), ft])) == dimsum([AB, AC, ft])
                    report['closed_by_fall_top'] += int(closed)
                    report['cases'].append({'S': list(S), 'e': e, 'A': list(a), 'B': list(b), 'C': list(c),
                                            'defect': int(lhs - rhs), 'closed_by_fall_top': bool(closed)})
print(json.dumps({k: v for k, v in report.items() if k != 'cases'}), flush=True)
if '--out' in sys.argv:
    json.dump(report, open(sys.argv[sys.argv.index('--out') + 1], 'w'), indent=1)
