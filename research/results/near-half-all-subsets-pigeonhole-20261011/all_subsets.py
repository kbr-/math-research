"""Exact refutation degree over F_2 of the pigeonhole principle on all d-subsets of m bits to a hole.

System G(m, d, n) (Razborov 1998, Definition 4.1), variables x_ij, i in [m] bits, j in [n] holes,
t_Ij = prod_{i in I} x_ij:  Q_I = 1 + sum_j t_Ij for every d-subset I of [m];  t_Ij for every (d+1)-subset I;
t_Ij1 t_Ij2 for every d-subset I and j1 != j2.  Unsatisfiable exactly when C(m, d) > n.  For d = 1 it is the
plain principle P(M, n) with M = m pigeons.

Statement tested (queue check entry-2026-10-10-full-ideal-relaxation:s1, the source's question): is the best
refutation of G(m, d, n) the one induced from the plain principle with M = C(m, d) pigeons, that is,
H:  deg G(m, d, n) = max(d * deg P(C(m, d), n), 2d),
the right side being an upper bound by prop:generic-principle-substitution-ceiling and 2d the largest axiom
degree; or is the degree lower, of the order of n + d, as the source's derivation of one term suggests may be
possible?

Written before the run.  I do not know which holds.  If H holds, every row prints gap = 0.  If H fails, some
row with d * deg P > 2d prints gap > 0.  Rows with d * deg P <= 2d cannot distinguish and are marked "blind":
there the degree is 2d under either answer, a control of the encoding only.
Controls: (1) every unsatisfiable instance on at most 16 variables is checked by brute force to have no common
zero, and one satisfiable instance, G(3, 2, 3), is checked to have one and must print degree null; (2) the
plain degrees must be at least n/2 + 1, the imported bound; (3) the upper bound: deg G <= max(d deg P, 2d) must
hold in every row, or the encoding is wrong.
Degrees by tools/f2_closure_degree.cpp, compiled into a scratch directory.  One-off job of 11 October 2026.

Usage: python3 all_subsets.py KERNEL_BINARY SCRATCH_DIR OUT.json M,D,N [M,D,N ...]
"""
import itertools
import json
import math
import subprocess
import sys


def term(bits, hole, m):
    mask = 0
    for i in bits:
        mask |= 1 << (hole * m + i)
    return mask


def system(m, d, n):
    rows = []
    for I in itertools.combinations(range(m), d):
        rows.append([0] + [term(I, j, m) for j in range(n)])
        for j1 in range(n):
            for j2 in range(j1 + 1, n):
                rows.append([term(I, j1, m) | term(I, j2, m)])
    for I in itertools.combinations(range(m), d + 1):
        for j in range(n):
            rows.append([term(I, j, m)])
    return rows


def has_zero(rows, variables):
    for point in range(1 << variables):
        if all(sum(1 for mono in row if mono & point == mono) % 2 == 0 for row in rows):
            return True
    return False


def degree(binary, scratch, name, rows, variables, dmax):
    path = f'{scratch}/{name}.txt'
    with open(path, 'w') as out:
        out.write(f'{variables} {len(rows)}\n')
        for row in rows:
            out.write(' '.join(str(v) for v in [len(row)] + row) + '\n')
    done = subprocess.run([binary, path, str(dmax)], check=True, capture_output=True, text=True).stdout
    return json.loads(done)['degree']


def main(argv):
    binary, scratch, target = argv[1:4]
    results, plain = [], {}
    for spec in argv[4:]:
        m, d, n = (int(v) for v in spec.split(','))
        pigeons, variables = math.comb(m, d), m * n
        rows = system(m, d, n)
        satisfiable = pigeons <= n
        if variables <= 16:
            assert has_zero(rows, variables) == satisfiable, spec
        if (pigeons, n) not in plain:
            prows = system(pigeons, 1, n)
            assert pigeons * n > 16 or has_zero(prows, pigeons * n) == satisfiable, spec
            plain[pigeons, n] = degree(binary, scratch, f'p{pigeons}_{n}', prows, pigeons * n, n + 1)
        base = plain[pigeons, n]
        found = degree(binary, scratch, f'g{m}_{d}_{n}', rows, variables, variables)
        row = {'m': m, 'd': d, 'n': n, 'pigeons': pigeons, 'variables': variables, 'satisfiable': satisfiable,
               'plain_degree': base, 'degree': found}
        if not satisfiable:
            assert base is not None and base >= n / 2 + 1, spec          # the imported lower bound
            bound = max(d * base, 2 * d)
            assert found is not None and found <= bound, spec            # the substitution ceiling
            row.update(induced=bound, gap=bound - found, blind=d * base <= 2 * d)
        else:
            assert found is None and base is None, spec
        results.append(row)
        print(json.dumps(row), flush=True)
    with open(target, 'w') as out:
        json.dump(results, out, indent=1)
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv))
