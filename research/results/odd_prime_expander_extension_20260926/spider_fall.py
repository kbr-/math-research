#!/usr/bin/env python3
"""Degree fall of functional graph PHP at a spider (prop:spider-fall test).

Board: the spider (centre row r with holes h_1..h_d, leg n_i with hole h_i and d-1 private holes). Axioms: linear
rows (sum over the row's holes minus 1), hole collisions, functionality, with Booleanity by multilinear reduction.
T* = {(n_i, h_i)}. The product y_{T*} (degree d) lies in the degree-(d+1) span (y_{T*} times r's row). Test: is it
in the NS span at degree d, i.e. of axioms times monomials with total degree <= d? Exact F_3 ranks (FLINT)."""
import itertools, json, sys
sys.path.insert(0, __file__.rsplit('/', 1)[0])
import matching_complex as mc
from spider_check import spider

def run(d):
    nb = spider(d)
    cells = [(i, t) for i, row in enumerate(nb) for t in sorted(row)]
    cid = {c: k for k, c in enumerate(cells)}
    def mono_ok(m):
        rows = [cells[k][0] for k in m]; holes = [cells[k][1] for k in m]
        return len(set(rows)) == len(rows) and len(set(holes)) == len(holes)   # kills by functionality/collision anyway
    axioms = []
    for i, row in enumerate(nb):
        axioms.append(({(cid[(i, t)],): 1 for t in row} | {(): -1}, 1))           # row equation, degree 1
    def span_rank(D, target=None):
        monos = [m for k in range(D + 1) for m in itertools.combinations(range(len(cells)), k)]
        col = {m: j for j, m in enumerate(monos)}
        ent, r = {}, 0
        def add_row(poly):
            nonlocal r
            for m, v in poly.items():
                if m in col and v % 3:
                    ent[(r, col[m])] = (ent.get((r, col[m]), 0) + v) % 3
            r += 1
        # collisions and functionality: pure monomials y_c y_c' of conflicting cells, times any monomial
        for m in monos:
            rows = [cells[k][0] for k in m]; holes = [cells[k][1] for k in m]
            if len(m) >= 2 and not (len(set(rows)) == len(rows) and len(set(holes)) == len(holes)):
                add_row({m: 1})                                                     # in the ideal at degree len(m)
        for poly, deg in axioms:
            for m in monos:
                if len(m) + deg > D:
                    continue
                prod = {}
                for a, v in poly.items():
                    mm = tuple(sorted(set(m) | set(a)))                              # Booleanity: multilinear
                    prod[mm] = (prod.get(mm, 0) + v) % 3
                add_row(prod)
        base = mc.flint_ranks([(r, len(monos), {k: v for k, v in ent.items() if v})])[0]
        if target is None:
            return base
        ent2 = dict(ent); ent2[(r, col[target])] = 1
        withm = mc.flint_ranks([(r + 1, len(monos), {k: v for k, v in ent2.items() if v})])[0]
        return base, withm
    T = tuple(sorted(cid[(i + 1, i)] for i in range(d)))
    out = {}
    for D in (d, d + 1):
        b, w = span_rank(D, T)
        out[f'in_I_{D}'] = (b == w)
    return out

if __name__ == '__main__':
    res = []
    for d in (2, 3):                     # d = 4 exceeds the dense matrix size of this script
        r = {'d': d, **run(d)}; res.append(r); print(r, flush=True)
        if '--out' in sys.argv:          # write each case as it finishes
            json.dump(res, open(sys.argv[sys.argv.index('--out') + 1], 'w'), indent=1)
