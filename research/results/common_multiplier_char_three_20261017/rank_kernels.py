"""Common kernels of partition errors on the functional pigeonhole system over F_p, by FFPACK ranks.

The spanning set of C/H is basis_kernels.py's (the disjoint-pair entry): x_t times a nonempty product of pigeon axioms,
t dancing, |t| plus the number of factors <= D, reduced modulo H to matching monomials. For errors E_1..E_r and the
matching monomials T_K of size <= K, the common kernel modulo H has dimension |T_K| - (rank S - r rank G), where G is
the generator matrix and S stacks r copies of G block-diagonally above the rows (t E_1 | ... | t E_r) for t in T_K.
W = C cap V_K is the case of the one error 1. Ranks come from research/tools/modp_rank.cpp (FFPACK::Rank).

Statement tested: whether the disjoint pair E_A, E_B with A = {0, 1}, B = {2, 3} at seven pigeons and six holes,
D = 3, K = 2, has J = W over F_3, the case prop:partition-kernels-every-field leaves open (rooms 2, 0, 2, 2 < 4).
Expected: no outcome is predicted over F_3.
Refuted by: nothing is refuted over F_3; the figure is the result.
Possible because: no recorded statement fixes the F_3 common kernel at seven pigeons.
Prediction: over F_5 at seven pigeons, J = W, by prop:partition-common-kernels (d) (|A cup B| = 4 >= 4, D = 3).
Refuted by: an F_5 common kernel modulo H larger than W modulo H at seven pigeons.
Possible because: a wrong route or a false part (d) would give a larger kernel there.
Control: at six pigeons and five holes the route must reproduce basis_kernels.json: W modulo H 141 over F_2 and
F_3; single kernel at A = {0, 1} 197 (F_2) and 155 (F_3); disjoint pair 165 (F_2) and 141 (F_3); the overlapping
pair A = {0, 1}, B = {0, 2} 155 (F_2) and 143 (F_3). The script asserts all eight.
Refuted by: any of the eight six-pigeon figures differing from basis_kernels.json.
Possible because: a wrong rank kernel, stacking or generator set would change them.
Positive control: over F_2 at seven pigeons the disjoint pair has the common surviving killers x_1a x_2b, a in A,
b in B, by prop:partition-kernels-every-field (d), so J modulo H must exceed W modulo H there.
Refuted by: J modulo H equal to W modulo H over F_2 at seven pigeons.
Possible because: a route that lost killers would give equality.
Forced by counts: nothing; |T_2| = 331 at six pigeons exceeds every control figure, and the generator rows
outnumber the ranks, so no count fixes a kernel dimension.
Baseline: W <= J <= the single kernel of E_A; the containment leaves the F_3 figure anywhere in that range.
Record checked: the claims read were prop:partition-kernels-every-field, prop:partition-common-kernels and
check:disjoint-pair-kernels-f3; none gives the F_3 common kernel at seven pigeons.
Decisive at these sizes: exact ranks over finite fields, no seeds; a difference of one dimension decides it.
Parallel use: FFPACK's rank runs on OpenBLAS threads; the driver is one process generating sparse matrices.
"""
import argparse
import importlib.util
import json
import pathlib
import subprocess
import tempfile
import time

HERE = pathlib.Path(__file__).resolve()
SPEC = importlib.util.spec_from_file_location(
    'basis_kernels', HERE.parents[1] / 'common_multiplier_disjoint_pair_20261017' / 'basis_kernels.py')
bk = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(bk)


def rank(entries, rows, cols, p, binary, scratch):
    path = pathlib.Path(scratch) / 'matrix.txt'
    with open(path, 'w') as out:
        out.write(f'{p} {rows} {cols} {len(entries)}\n')
        out.write(''.join(f'{r} {c} {v}\n' for r, c, v in entries))
    return int(subprocess.run([binary, str(path)], check=True, capture_output=True, text=True).stdout)


def generators(m, n, D, index):
    rows = []
    for t in index:
        if not bk.dances(t):
            continue
        free = [i for i in range(m) if i not in dict(t)]
        for z in range(1, D - len(t) + 1):
            for Z in __import__('itertools').combinations(free, z):
                f = {t: 1}
                for i in Z:
                    f = bk.poly_mul(f, bk.q(i))
                rows.append(f)
    return rows


def run(p, m, n, D, K, errors_sets, binary, scratch):
    bk.P, bk.N = p, n
    td = bk.matchings(m, n, D)
    index = {t: i for i, t in enumerate(td)}
    gens = generators(m, n, D, index)
    tk = [t for t in td if len(t) <= K]
    cols = len(td)
    g_entries = [(r, index[mono], c) for r, f in enumerate(gens) for mono, c in f.items()]
    rank_g = rank(g_entries, len(gens), cols, p, binary, scratch)

    def kernel(errors):
        r = len(errors)
        entries = [(b * len(gens) + i, b * cols + j, v) for b in range(r) for i, j, v in g_entries]
        base = r * len(gens)
        for row, t in enumerate(tk):
            for b, E in enumerate(errors):
                for mono, c in bk.poly_mul({t: 1}, E).items():
                    entries.append((base + row, b * cols + index[mono], c))
        return len(tk) - (rank(entries, base + len(tk), r * cols, p, binary, scratch) - r * rank_g)

    out = {'p': p, 'pigeons': m, 'holes': n, 'D': D, 'K': K, 'generators': len(gens), 'columns': cols,
           'rank_G': rank_g, 'T_K': len(tk), 'W_mod_H': kernel([{(): 1}]), 'singles': {}, 'pairs': []}
    for A, B in errors_sets:
        for S in (A, B):
            out['singles'].setdefault(str(S), kernel([bk.error(S)]))
        out['pairs'].append({'A': A, 'B': B, 'J_mod_H': kernel([bk.error(A), bk.error(B)])})
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--out', required=True)
    ap.add_argument('--rank-binary', required=True)
    args = ap.parse_args()
    pairs = [([0, 1], [2, 3]), ([0, 1], [0, 2])]
    series = []
    with tempfile.TemporaryDirectory() as scratch:
        for p, m, n in ((2, 6, 5), (3, 6, 5), (3, 7, 6), (5, 7, 6), (2, 7, 6)):
            t0 = time.time()
            r = run(p, m, n, 3, 2, pairs, args.rank_binary, scratch)
            r['seconds'] = round(time.time() - t0, 1)
            series.append(r)
            print(json.dumps(r), flush=True)
            pathlib.Path(args.out).write_text(json.dumps(series, indent=1) + '\n')
            if n == 5:
                want = {2: (141, 197, 165, 155), 3: (141, 155, 141, 143)}[p]
                got = (r['W_mod_H'], r['singles'][str([0, 1])], r['pairs'][0]['J_mod_H'], r['pairs'][1]['J_mod_H'])
                assert got == want, f'control at six pigeons over F_{p}: {got} against {want}'
    f2 = series[4]
    assert f2['pairs'][0]['J_mod_H'] > f2['W_mod_H'], 'positive control: F_2 disjoint pair at seven pigeons'


if __name__ == '__main__':
    main()
