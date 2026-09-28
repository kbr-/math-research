#!/usr/bin/env python3
"""Fall tables: how far elements of the Nullstellensatz span fall below their NS level.

For a finite point set with a degree filtration F_a and row functions rho_i, N_b = sum_i rho_i F_{b-1}.  Take a basis
adapted to both flags (F_a) and (N_b).  e(a, b) is the number of its elements of degree exactly a and NS level exactly
b (a <= b), from t(a, b) = dim(N_b cap F_a) by two-dimensional differencing.  The depth of such an element is b - a.
Tested statements (prop:lagged-lift-criterion and its fall-table form):
  top lift at D                 <=> sum_{a < D} e(a, D) = 0;
  lagged lift at (D, D')        <=> sum_{a <= D-1} e(a, D') = 0;
  blocked configurations of prop:blocked-centre-lift-failure give entries of depth exactly 1.
Point sets: matching sets of small boards (matching-monomial basis, exact FLINT ranks via rank_mod3.c), and the
coupled-pair value spaces Y of prop:single-row-lift-transfer (plain elimination, at most 16 points).
"""
import argparse, json, os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from blocked_centre_lift import rank_bin, matchings, generators, blocked_configuration
from value_space_lift import evalrows, rank_cols
import subprocess


def table_from_t(t, B):
    """e(a, b) for 0 <= a <= b <= B from t(a, b) = dim(N_b cap F_a) (t(a, b) = t(b, b) for a >= b)."""
    T = lambda a, b: 0 if a < 0 or b <= 0 else t[(min(a, b), b)]
    return {f'{a},{b}': T(a, b) - T(a - 1, b) - T(a, b - 1) + T(a - 1, b - 1)
            for b in range(1, B + 1) for a in range(0, b + 1)
            if T(a, b) - T(a - 1, b) - T(a, b - 1) + T(a - 1, b - 1)}


def board_table(nbrs, B, rb):
    basis = matchings(nbrs, B)
    index = {U: k for k, U in enumerate(basis)}
    size = [len(U) for U in basis]
    jobs, keys = [], []
    for b in range(1, B + 1):
        g = generators(nbrs, b, index)
        for a in range(0, b + 1):
            # dim(N_b cap F_a) = rank N_b - rank(N_b projected to coordinates of degree > a)
            G = g if a == b else [{j: v for j, v in r.items() if size[j] > a} for r in g]
            ent = {(i, j): v % 3 for i, r in enumerate(G) for j, v in r.items() if v % 3}
            jobs.append((len(G), len(basis), ent)); keys.append((a, b))
    lines = []
    for r, c, ent in jobs:
        lines.append(f'{r} {c} {len(ent)}'); lines.extend(f'{i} {j} {v}' for (i, j), v in ent.items())
    ranks = [int(x) for x in subprocess.run([rb], input='\n'.join(lines) + '\n', capture_output=True, text=True,
                                            check=True).stdout.split()]
    R = dict(zip(keys, ranks))
    t = {(a, b): R[(b, b)] - (R[(a, b)] if a < b else 0) for (a, b) in keys}
    return table_from_t(t, B), len(basis)


def value_space_table(Y, m, c0, B):
    rho = lambda p: (c0 + (1 if p[2] == 1 else 0) - p[0] - p[1] - 1) % 3
    t = {}
    for b in range(1, B + 1):
        Nb = evalrows(Y, m, b - 1, rho)
        for a in range(0, b + 1):
            Fa = evalrows(Y, m, a)
            both = [x + y for x, y in zip(Nb, Fa)]
            t[(a, b)] = rank_cols(Nb) + rank_cols(Fa) - rank_cols(both)
    return table_from_t(t, B)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--boards', required=True, help='blocked_centre_lift.json (boards reused)')
    ap.add_argument('--out', required=True)
    ap.add_argument('--tmp', default=os.environ.get('TMPDIR', '/tmp'))
    args = ap.parse_args()
    rb = rank_bin(args.tmp)
    out = {'boards': [], 'value_spaces': []}
    for rec in json.load(open(args.boards)):
        nbrs = rec['nbrs']
        B = 3 if rec['case'].startswith('complete') else 4  # the complete 7 x 6 board has ~17k matchings of size <= 4
        tab, nb = board_table(nbrs, B, rb)
        conf = {D: blocked_configuration(nbrs, D) is not None for D in range(2, B + 1)}
        # blocked configurations give a depth-1 entry at level D
        for D, has in conf.items():
            if has:
                assert tab.get(f'{D - 1},{D}', 0) >= 1, (rec['case'], D, tab)
        # consistency with the lift defects of blocked_centre_lift.json
        for D, d in rec['defects'].items():
            if int(D) <= B:
                assert sum(v for k, v in tab.items() if int(k.split(',')[1]) == int(D) and int(k.split(',')[0]) < int(D)) \
                    == d['lambda'], (rec['case'], D)
        out['boards'].append({'case': rec['case'], 'basis': nb, 'table': tab, 'blocked': conf})
        print(rec['case'], tab, flush=True)
    F3 = [0, 1, 2]
    for m in (2, 3):
        for name, (V1, V2) in {'coupled {y!=0} x {y\'!=0}': ([1, 2], [1, 2]),
                               'one unbalanced {y!=0} x F3': ([1, 2], F3)}.items():
            for c0 in range(3):
                Y = [(y, yp, pi) for y in V1 for yp in V2 for pi in range(m + 1)]
                tab = value_space_table(Y, m, c0, 8)
                out['value_spaces'].append({'m': m, 'case': name, 'c0': c0, 'table': tab})
                print(f'm={m}; {name}; c0={c0}', tab, flush=True)
    json.dump(out, open(args.out, 'w'), indent=1)


if __name__ == '__main__':
    main()
