"""Check of the degree-2 integral certificate for weak PHP (odd-prime thread, 26 Sept 2026).

Construction (prop:integral-degree-two-certificate): l(1) = 1; l(x_ij) = a_ij with a_i0 = 1 (hole 0), else 0;
l = 0 on same-row pairs and on column collisions; for pigeons i < i', the values B[j, j'] = l(x_ij x_i'j')
(j != j') form an integer matrix with zero diagonal, row sums a_i and column sums a_i', obtained from a
spanning tree of the bipartite graph K_{n,n} minus the perfect matching {(j, j)} (n >= 3).
The script builds l for n = 3..7 and checks exactly (over Z) that l vanishes on every multilinear
degree-<=2 multiple of the weak-base axioms, via the lattice rows of php_lattice_torsion.py.
Usage: degree_two_certificate.py --ns 3,4,5,6,7 --out FILE"""
import argparse, json, os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', 'odd_prime_closed_routes_review_20260926'))
from php_lattice_torsion import lattice_rows


def tree_flow(n, r, c):
    """Integer matrix B, zero diagonal, row sums r, column sums c (sum r = sum c), n >= 3.
    Spanning tree of K_{n,n} minus {(j,j)}: edges (0,j') for j' >= 1 and (j,0) for j >= 1, plus (1,2)."""
    B = [[0] * n for _ in range(n)]
    # unknowns: B[0][j'] (j'>=1), B[j][0] (j>=1), B[1][2]; row 0: sum_{j'>=1} B[0][j'] = r[0];
    # column j' >= 1: B[0][j'] + [j'==2] B[1][2] = c[j']; row j >= 1: B[j][0] + [j==1] B[1][2] = r[j]; column 0: sum B[j][0] = c[0]
    # Solve: choose B[1][2] = t; then B[0][j'] = c[j'] - [j'==2] t, B[j][0] = r[j] - [j==1] t, and row 0 forces
    # sum_{j'>=1} c[j'] - t = r[0], i.e. t = sum_{j'>=1} c[j'] - r[0]; column 0 then holds automatically.
    t = sum(c[1:]) - r[0]
    B[1][2] = t
    for jp in range(1, n):
        B[0][jp] = c[jp] - (t if jp == 2 else 0)
    for j in range(1, n):
        B[j][0] = r[j] - (t if j == 1 else 0)
    assert all(B[j][j] == 0 for j in range(n))
    assert [sum(B[j]) for j in range(n)] == list(r) and [sum(B[j][jp] for j in range(n)) for jp in range(n)] == list(c)
    return B


def functional(n):
    a = [[1 if j == 0 else 0 for j in range(n)] for _ in range(n + 1)]
    var = lambda i, j: i * n + j
    ell = {frozenset(): 1}
    for i in range(n + 1):
        for j in range(n):
            ell[frozenset([var(i, j)])] = a[i][j]
    for i in range(n + 1):
        for ip in range(i + 1, n + 1):
            B = tree_flow(n, a[i], a[ip])
            ell.update({frozenset([var(i, j), var(ip, jp)]): B[j][jp] for j in range(n) for jp in range(n) if jp != j})
    return ell


def main():
    ap = argparse.ArgumentParser(); ap.add_argument('--ns', default='3,4,5,6,7'); ap.add_argument('--out', required=True)
    a = ap.parse_args(); out = []
    for n in map(int, a.ns.split(',')):
        ell = functional(n)
        rows, _ = lattice_rows(n, 2)
        bad = sum(1 for r in rows if sum(c * ell.get(m, 0) for m, c in r.items()) != 0)
        out.append(dict(n=n, pigeons=n + 1, d=2, multiples=len(rows), violated=bad, ell_of_one=ell[frozenset()],
                        max_abs_value=max(abs(v) for v in ell.values())))
        print(out[-1], flush=True)
    json.dump(out, open(a.out, 'w'), indent=1)


if __name__ == '__main__':
    main()
