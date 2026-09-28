#!/usr/bin/env python3
"""Top-degree lift defect of functional graph PHP on small boards, over F_3.

Tested statement (prop:blocked-centre-lift-failure): on the set of matchings of a bipartite graph G, with the
matching monomials x_U as degree-exact basis, rho_i = sum_{t in N(i)} x_{it} - 1 and N_e spanned by rho_i x_U
(|U| <= e-1, i not a row of U), the lift defect lambda(D) = dim(N_D cap F_{D-1}) - dim N_{D-1} is at least 1
whenever G has a blocked configuration of size D-1: a pigeon r of degree d <= D-1, distinct legs n_i matched to the
holes h_i of N(r) with spare holes p_i, and D-1-d further pigeons v_j with two holes each, all 2(D-1) holes distinct.
Control (lem:graph-matching-extension with chessboard connectivity): the complete board with N >= 2D-1 holes has
lambda(e) = 0 for e <= D.

lambda(D) = rank(Gen_D) - rank(top part of Gen_D) - rank(Gen_{D-1}), exact ranks by FLINT (rank_mod3.c).
"""
import argparse, itertools, json, os, random, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))
RANK_SRC = os.path.join(HERE, '..', 'results', 'odd_prime_expander_extension_20260926', 'rank_mod3.c')


def rank_bin(tmp):
    path = os.path.join(tmp, 'rank_mod3')
    if not os.path.exists(path):
        subprocess.run(['cc', '-O2', '-o', path, RANK_SRC, '-lflint'], check=True)
    return path


def matchings(nbrs, maxsize):
    """All matchings of size <= maxsize as sorted tuples of (row, hole)."""
    out = [()]
    def rec(start, used, face):
        if len(face) == maxsize:
            return
        for r in range(start, len(nbrs)):
            for t in nbrs[r]:
                if t not in used:
                    f = face + ((r, t),)
                    out.append(f)
                    rec(r + 1, used | {t}, f)
    rec(0, frozenset(), ())
    return out


def generators(nbrs, e, index):
    """Rows rho_i x_U, |U| <= e-1, as sparse dicts over the matching basis."""
    gens = []
    for U in index:
        if len(U) > e - 1:
            continue
        rows = {c[0] for c in U}; holes = {c[1] for c in U}
        for i in range(len(nbrs)):
            if i in rows:
                continue
            g = {index[U]: -1}
            for t in nbrs[i]:
                if t not in holes:
                    W = tuple(sorted(U + ((i, t),)))
                    g[index[W]] = g.get(index[W], 0) + 1
            gens.append(g)
    return gens


def lift_defects(nbrs, Dmax, rb):
    basis = matchings(nbrs, Dmax)
    index = {U: k for k, U in enumerate(basis)}
    size = {k: len(U) for U, k in index.items()}
    blocks, out = [], {}
    for D in range(1, Dmax + 1):
        gD = generators(nbrs, D, index)
        gD1 = generators(nbrs, D - 1, index) if D >= 2 else []
        top = [{j: v for j, v in g.items() if size[j] == D} for g in gD]
        for G in (gD, top, gD1):
            ent = {(a, j): v % 3 for a, g in enumerate(G) for j, v in g.items() if v % 3}
            blocks.append((len(G), len(basis), ent))
    lines = []
    for r, c, ent in blocks:
        lines.append(f'{r} {c} {len(ent)}'); lines.extend(f'{i} {j} {v}' for (i, j), v in ent.items())
    ranks = [int(x) for x in subprocess.run([rb], input='\n'.join(lines) + '\n', capture_output=True, text=True,
                                            check=True).stdout.split()]
    for D in range(1, Dmax + 1):
        a, b, c = ranks[3 * (D - 1):3 * D]
        out[D] = {'rank_N_D': a, 'rank_top': b, 'rank_N_D-1': c, 'lambda': a - b - c}
    return out, len(basis)


def blocked_configuration(nbrs, D):
    """A blocked configuration of size D-1 (see docstring), found by exhaustive search, or None."""
    m = len(nbrs)
    for r in range(m):
        d = len(nbrs[r])
        if d > D - 1:
            continue
        H = sorted(nbrs[r]); others = [i for i in range(m) if i != r]
        def legs(k, used_rows, used_holes, acc):
            if k == d:
                yield acc, used_rows, used_holes; return
            for n in others:
                if n in used_rows or H[k] not in nbrs[n]:
                    continue
                for p in nbrs[n]:
                    if p in used_holes or p in H or p == H[k]:
                        continue
                    yield from legs(k + 1, used_rows | {n}, used_holes | {H[k], p}, acc + [(n, H[k], p)])
        def extra(k, start, used_rows, used_holes, acc):
            if k == 0:
                yield acc; return
            for v in range(start, m):
                if v in used_rows or v == r:
                    continue
                free = [t for t in nbrs[v] if t not in used_holes]
                for a, b in itertools.combinations(free, 2):
                    yield from extra(k - 1, v + 1, used_rows | {v}, used_holes | {a, b}, acc + [(v, a, b)])
        for L, ur, uh in legs(0, frozenset({r}), frozenset(H), []):
            for E in extra(D - 1 - d, 0, ur, uh, []):
                return {'centre': r, 'legs': L, 'extra': E}
    return None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--out', required=True)
    ap.add_argument('--tmp', default=os.environ.get('TMPDIR', '/tmp'))
    args = ap.parse_args()
    rb = rank_bin(args.tmp)
    rng = random.Random(20260928)
    cases = []
    # control: complete board, 7 pigeons, 6 holes, D <= 3 (N = 6 >= 2*3-1)
    cases.append(('complete_7x6', [list(range(6))] * 7, 3))
    # spider board, d = 2: centre 0 = {0,1}; legs 1 = {0,2,3}, 2 = {1,4,5}
    cases.append(('spider_d2', [[0, 1], [0, 2, 3], [1, 4, 5]], 3))
    # the same spider inside a random board of pigeon degree 3 (holes 0..6, 7 pigeons), D = 3, 4
    for s in range(3):
        extra = [sorted(rng.sample(range(7), 3)) for _ in range(4)]
        cases.append((f'spider_in_random_{s}', [[0, 1], [0, 2, 3], [1, 4, 5]] + extra, 4))
    # random boards of pigeon degree 3, 7 pigeons, 6 holes
    for s in range(3):
        cases.append((f'random_deg3_{s}', [sorted(rng.sample(range(6), 3)) for _ in range(7)], 4))
    res = []
    for name, nbrs, Dmax in cases:
        defects, nb = lift_defects(nbrs, Dmax, rb)
        conf = {D: blocked_configuration(nbrs, D) for D in range(2, Dmax + 1)}
        for D in range(2, Dmax + 1):
            if conf[D] is not None:
                assert defects[D]['lambda'] >= 1, (name, D, defects[D], conf[D])
        rec = {'case': name, 'nbrs': nbrs, 'basis': nb, 'defects': defects,
               'blocked_configuration': {D: conf[D] for D in conf}}
        res.append(rec)
        print(name, nb, {D: (defects[D]['lambda'], conf.get(D) is not None) for D in defects}, flush=True)
    assert all(r['defects'][D]['lambda'] == 0 for r in res if r['case'] == 'complete_7x6' for D in (1, 2, 3))
    json.dump(res, open(args.out, 'w'), indent=1)


if __name__ == '__main__':
    main()
