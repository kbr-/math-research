"""Degrees of the boundary threshold on the cube, from the maximal minors along a random line.

Statement tested (conj:cube-dimension-three-thresholds, part 1, and its analogue for other n).
By lem:cube-threshold-ideal (Part 2), when Ord_n(d) = {0..N-1} (N = N_{2,n}(d)), the savings reach
h = d+1 at m = N exactly from l_0 = deg Delta_{n,d} - deg g, where g = gcd of the maximal minors
M_c of the N x (N+1) constraint matrix.  For n = 3 the conjecture is g = (y1y2y3)^{d^2}
prod(y_i - y_j)^{d^2}, so l_0 = d^2 - 1.

The compiled kernel bmd_cube_boundary_minors evaluates every M_c on the affine line y = u + t v
(random u, v over F_p, p large) at t = 0..P-1; the kernel interpolates each M_c(t), takes the gcd
over F_p, and reports deg M_N, deg g, l_0, and the multiplicity in g of the roots where the line
meets y_i = 0 and y_i = y_j (with any remaining factor degree).  On a generic line the degree and
factor structure of the restricted gcd equal those of g.
Usage: bmd_cube_boundary_gcd.py KERNEL p n DMIN DMAX SEED OUT
"""
import random, subprocess, sys
from math import comb


def n2(n, d):
    return sum(comb(n, i) * ((d - i) // 2 + 1) for i in range(min(n, d) + 1))


def main():
    kernel, p, n, dmin, dmax, seed, out = sys.argv[1], int(sys.argv[2]), int(sys.argv[3]), int(sys.argv[4]), int(sys.argv[5]), int(sys.argv[6]), sys.argv[7]
    rng = random.Random(seed)
    u = [rng.randrange(1, p) for _ in range(n)]
    v = [rng.randrange(1, p) for _ in range(n)]
    roots = [(-u[i]) * pow(v[i], p - 2, p) % p for i in range(n)]
    roots += [(u[j] - u[i]) * pow(v[i] - v[j], p - 2, p) % p for i in range(n) for j in range(i + 1, n)]
    assert len(set(v)) == n and len(set(roots)) == len(roots), 'collision roots must be distinct'
    with open(out, 'w') as fh:
        fh.write(f'p={p} n={n} line u={u} v={v}\n')
        for d in range(dmin, dmax + 1):
            N = n2(n, d)
            npts = N * (N + 1) // 2 + N + 3  # exceeds the sum of column degrees, hence every deg M_c
            assert npts <= p
            res = subprocess.run([kernel, str(p), str(n), str(d), str(npts)] + [str(x) for x in u + v],
                                 check=True, capture_output=True, text=True)
            f = res.stdout.split()
            dn, dg = int(f[1]), int(f[3])
            line = f'n={n} d={d} N={N}: deg M_N (= deg Delta) = {dn}, deg g = {dg}, l_0 = {dn - dg}; ' + ' '.join(f[4:])
            print(line, flush=True)
            fh.write(line + '\n')
            fh.flush()


if __name__ == '__main__':
    main()
