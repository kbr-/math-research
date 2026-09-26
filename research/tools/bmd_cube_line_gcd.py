#!/usr/bin/env python3
"""Common zeros of the coordinates of a solution along a line (entry-2026-09-26-cube-double-points).

Statement tested.  For the boundary solution W^(n) on {0,1}^3, the set Z_n of points of U (distinct nonzero entries)
where W^(n) vanishes meets the line y = (u, 1, u+1) (the line y3 = y1 + y2 of F_2 = 0) only at the roots of the gcd,
over F_q[u], of the coordinates of W^(n)(u, 1, u+1).  Input: the output of bmd_cube_solution_cones in series mode
with YPTS = the points (u, 1, u+1), u = U0, U0+1, ..., and DUMPVAL=1; each case's value vectors ("VAL i W_0 ... W_m")
follow its header.  Each coordinate is a polynomial in u of degree at most l + m (homogeneous of that degree in y),
so it is interpolated from the dumped points when there are more of them than that degree.  The script prints, per
case, the degree of the gcd and its roots in F_q, and marks which roots are collision points (u in {0, -1, 1} or
u = -1/2, where two entries coincide or one vanishes).

Usage: bmd_cube_line_gcd.py LOG Q U0
"""
import re
import sys


def interp(xs, ys, q):
    """Lagrange interpolation mod q: coefficient list, low degree first."""
    n = len(xs)
    coef = [0] * n
    for i in range(n):
        num = [1]; den = 1
        for j in range(n):
            if j == i:
                continue
            num = [((num[k - 1] if k else 0) - xs[j] * (num[k] if k < len(num) else 0)) % q for k in range(len(num) + 1)]
            den = den * (xs[i] - xs[j]) % q
        f = ys[i] * pow(den, q - 2, q) % q
        for k in range(n):
            coef[k] = (coef[k] + f * num[k]) % q
    while coef and coef[-1] == 0:
        coef.pop()
    return coef


def pmod(a, b, q):
    a = a[:]
    inv = pow(b[-1], q - 2, q)
    while len(a) >= len(b) and a:
        f = a[-1] * inv % q; s = len(a) - len(b)
        for k in range(len(b)):
            a[s + k] = (a[s + k] - f * b[k]) % q
        while a and a[-1] == 0:
            a.pop()
    return a


def pgcd(a, b, q):
    while b:
        a, b = b, pmod(a, b, q)
    if a:
        inv = pow(a[-1], q - 2, q); a = [c * inv % q for c in a]
    return a


def roots(f, q, cands):
    return [u for u in cands if sum(c * pow(u, k, q) for k, c in enumerate(f)) % q == 0]


def main():
    log, q, u0 = sys.argv[1], int(sys.argv[2]), int(sys.argv[3])
    cases, cur = [], None
    for line in open(log):
        m = re.match(r'prime \d+ \(d,rho\)=\((\d+),(\d+)\) m=(\d+)', line)
        if m:
            cur = {'d': int(m[1]), 'rho': int(m[2]), 'm': int(m[3]), 'vals': {}, 'l': None}; cases.append(cur); continue
        m = re.match(r'l=(\d+)', line)
        if m and cur:
            cur['l'] = int(m[1])
        m = re.match(r'VAL (\d+) (.*)', line)
        if m and cur is not None:
            cur['vals'].setdefault(int(m[1]), []).append([int(x) for x in m[2].split()])
    special = {0 % q, (-1) % q, 1, (-pow(2, q - 2, q)) % q}
    for c in cases:
        pts = sorted(c['vals'])
        # every coordinate is homogeneous of degree <= l + m in y, hence of degree <= l + m in u on the line
        assert c['l'] + c['m'] < len(pts), 'too few points for the degree bound l + m'
        vecs = [c['vals'][i][0] for i in pts]  # first witness (the space is one-dimensional)
        xs = [(u0 + i) % q for i in pts]
        g = []
        for col in range(len(vecs[0])):
            f = interp(xs, [v[col] for v in vecs], q)
            if f:
                g = pgcd(g, f, q) if g else f
        deg = len(g) - 1
        # roots among all special points and all of F_q would be too slow for large q; test the collision points and
        # report whether the gcd splits off anything else
        sp = roots(g, q, sorted(special)) if deg > 0 else []
        print(f"(d,rho)=({c['d']},{c['rho']}) l={c['l']}: points {len(xs)}, gcd degree {deg}, collision roots "
              f"{['u=%d' % (u if u < q // 2 else u - q) for u in sp]}, gcd {g}")


if __name__ == '__main__':
    main()
