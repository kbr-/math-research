#!/usr/bin/env python3
"""Checks for cycle 229 (parity constraints at degree two on the functional unary PHP over F_2).

Part A. For random parity constraints a_b = l_b + c_b (uniform forms, or label forms on N = 2^l holes)
compute exactly, in matching normal form:
  fall   : dim(G_2 cap P_{<=1}) > dim G_1, where G_1 = I_1 + span(a_b), G_2 = I_2 + sum_b a_b P_{<=1};
  star   : the criterion (*) of the entry: the restriction of the conflict two-forms K_0 to the
           annihilator U (vectors phi on the cells with zero row sums and l_b(phi) = 0) is injective
           modulo the forms that vanish on all zero-row-sum vectors, i.e. rank = dim Kbar;
  count  : dim G_2 equals the count dim I_2 + sum_b (c_1 - b).
The theorem says star implies no fall; the script reports every violation and the joint statistics.

Part B. Structure lemma for label forms: dim (Kbar cap (Lbar wedge V)) computed as
dim Kbar - rank of Kbar restricted to the annihilator of the label forms.

Usage: two_form_criterion_check.py --holes N [--label] --trials T --seed S [--mmin a --mmax b] | --structure N"""
import argparse, itertools, json, random, sys

def rank_insert(pivots, v):
    while v:
        h = v.bit_length() - 1
        p = pivots.get(h)
        if p is None:
            pivots[h] = v; return True
        v ^= p
    return False

def board(N):
    R = N + 1
    cells = [(i, j) for i in range(R) for j in range(N)]
    cid = {c: k for k, c in enumerate(cells)}
    conflict = lambda a, b: a != b and (a[0] == b[0] or a[1] == b[1])
    return R, cells, cid, conflict

def label_basis(N):
    l = N.bit_length() - 1
    assert 1 << l == N
    R = N + 1
    forms = []
    for i in range(R):
        for t in range(l):
            forms.append([(i, j) for j in range(N) if (j >> t) & 1])
    return forms

def monomial_index(N):
    R, cells, cid, conflict = board(N)
    mons = [()] + [(k,) for k in range(len(cells))]
    for a in range(len(cells)):
        for b in range(a + 1, len(cells)):
            if not conflict(cells[a], cells[b]): mons.append((a, b))
    return {m: k for k, m in enumerate(mons)}, mons

def mul_affine(idx, cells, conflict, f, g):
    """product in normal form of two affine polynomials given as (const, set of cell ids)"""
    out = 0
    def tog(m):
        nonlocal out
        out ^= 1 << idx[m]
    if f[0] and g[0]: tog(())
    if f[0]:
        for b in g[1]: tog((b,))
    if g[0]:
        for a in f[1]: tog((a,))
    for a in f[1]:
        for b in g[1]:
            if a == b: tog((a,))
            elif not conflict(cells[a], cells[b]): tog((min(a, b), max(a, b)))
    return out

def trial(N, M, rng, label, ctx):
    R, cells, cid, conflict = ctx['board']; idx, mons = ctx['mon']; n1 = 1 + len(cells)
    if label:
        basis = ctx['label']
        forms = []
        for _ in range(M):
            s = set()
            for f in basis:
                if rng.random() < 0.5: s ^= {cid[c] for c in f}
            forms.append((rng.randrange(2), s))
    else:
        forms = [(rng.randrange(2), {k for k in range(len(cells)) if rng.random() < 0.5}) for _ in range(M)]
    rows = [(1, {cid[(i, j)] for j in range(N)}) for i in range(R)]          # 1 + rho_i
    unit = [(1, set())] + [(0, {k}) for k in range(len(cells))]
    deg1mask = (1 << n1) - 1
    # G_1
    p1 = {}
    for a in rows + forms: rank_insert(p1, mul_affine(idx, cells, conflict, a, (1, set())))
    dimG1 = len(p1)
    # G_2, eliminating with top-degree columns highest: pivots with leading monomial of degree <= 1 give G_2 cap P_<=1
    p2 = {}
    for a in rows:
        for u in unit: rank_insert(p2, mul_affine(idx, cells, conflict, a, u))
    dimI2 = len(p2)
    for a in forms:
        for u in unit: rank_insert(p2, mul_affine(idx, cells, conflict, a, u))
    low = sum(1 for h in p2 if h < n1)
    fall = low > dimG1
    c1 = N * N
    count = dimI2 + sum(c1 - b for b in range(1, M + 1))
    # criterion (*): U = {phi: row sums zero, l_b(phi) = 0}
    eqs = [sum(1 << cid[(i, j)] for j in range(N)) for i in range(R)] + [sum(1 << k for k in f[1]) for f in forms]
    piv = {}
    for e in eqs: rank_insert(piv, e)
    indep = len(piv) == R + M
    # nullspace basis by brute linear algebra
    nv = len(cells); red = dict(piv)
    # reduced echelon
    keys = sorted(red)
    for h in keys:
        for h2 in keys:
            if h2 != h and (red[h2] >> h) & 1: red[h2] ^= red[h]
    free = [k for k in range(nv) if k not in red]
    U = []
    for fcol in free:
        v = 1 << fcol
        for h, r in red.items():
            if (r >> fcol) & 1: v |= 1 << h
        U.append(v)
    d = len(U)
    pairs = [(a, b) for a in range(nv) for b in range(a + 1, nv) if conflict(cells[a], cells[b])]
    pk = {}
    for a, b in pairs:
        vec = 0; pos = 0
        for s in range(d):
            ua, ub = (U[s] >> a) & 1, (U[s] >> b) & 1
            for t in range(s + 1, d):
                if (ua & (U[t] >> b)) ^ (ub & (U[t] >> a)) & 1: vec |= 1 << pos
                pos += 1
        rank_insert(pk, vec)
    dimKbar = (N + 1) * (2 * N * N - 3 * N + 2) // 2
    star = len(pk) == dimKbar
    return dict(M=M, d=d, indep=indep, fall=fall, star=star, count_ok=(len(p2) == count), rankK=len(pk), dimKbar=dimKbar)

def structure(N):
    R, cells, cid, conflict = board(N); l = N.bit_length() - 1
    # annihilator of the label forms and row sums: per row, functions of degree <= l-2 of the label
    U = []
    for i in range(R):
        for mono in range(N):
            if bin(mono).count('1') <= l - 2:
                U.append(sum(1 << cid[(i, j)] for j in range(N) if (j & mono) == mono))
    d = len(U); nv = len(cells)
    pk = {}
    for a in range(nv):
        for b in range(a + 1, nv):
            if not conflict(cells[a], cells[b]): continue
            vec = 0; pos = 0
            for s in range(d):
                ua, ub = (U[s] >> a) & 1, (U[s] >> b) & 1
                if not (ua or ub): pos += d - s - 1; continue
                for t in range(s + 1, d):
                    if ((ua & (U[t] >> b)) ^ (ub & (U[t] >> a))) & 1: vec |= 1 << pos
                    pos += 1
            rank_insert(pk, vec)
    dimKbar = (N + 1) * (2 * N * N - 3 * N + 2) // 2
    rows_part = (N + 1) * ((N - 1) * (N - 2) // 2 - (N - 1 - l) * (N - 2 - l) // 2)
    return dict(holes=N, l=l, dim_annihilator=d, dimKbar=dimKbar, rank_restricted=len(pk), dim_intersection=dimKbar - len(pk),
                predicted_same_row_part=rows_part)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--holes', type=int); ap.add_argument('--label', action='store_true')
    ap.add_argument('--trials', type=int, default=20); ap.add_argument('--seed', type=int, default=1)
    ap.add_argument('--mmin', type=int); ap.add_argument('--mmax', type=int); ap.add_argument('--structure', type=int)
    ap.add_argument('--out')
    a = ap.parse_args()
    out = open(a.out, 'w') if a.out else sys.stdout
    if a.structure:
        print(json.dumps(structure(a.structure)), file=out); return
    N = a.holes; rng = random.Random(a.seed)
    ctx = dict(board=board(N), mon=monomial_index(N), label=label_basis(N) if a.label else None)
    for M in range(a.mmin, a.mmax + 1):
        res = [trial(N, M, rng, a.label, ctx) for _ in range(a.trials)]
        viol = [r for r in res if r['indep'] and r['star'] and r['fall']]
        line = dict(holes=N, label=a.label, M=M, d=res[0]['d'], trials=a.trials, independent=sum(r['indep'] for r in res),
                    star=sum(r['star'] for r in res), fall=sum(r['fall'] for r in res),
                    star_and_fall=len(viol), nostar_nofall=sum((not r['star']) and (not r['fall']) for r in res),
                    count_ok=sum(r['count_ok'] for r in res), dimKbar=res[0]['dimKbar'])
        print(json.dumps(line), file=out); out.flush()

if __name__ == '__main__':
    main()
