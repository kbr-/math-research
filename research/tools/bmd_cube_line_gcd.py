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

Mode "minors" (usage: bmd_cube_line_gcd.py minors LOG Q) reads the output of bmd_cube_line_minors ("MIN u M_0 ...
M_4d" lines after a "d=..." header), interpolates two random combinations of the minors in u (Newton form), takes
their gcd (the gcd of all minors with high probability), and reports its multiplicities at u = 0, -1, 1 and its
remaining degree.  The line-gcd property with g_{3,d} = (y1 y2 y3)^{d^2} prod (y_i - y_j)^{d^2} predicts
u^{2d^2 + psi(d)} (u+1)^{d^2} (u-1)^{d^2} and nothing else.

Mode "orders" (usage: bmd_cube_line_gcd.py orders LOG Q U0) reads the same value dumps as the default mode and
prints, per case, the order at u = 0 of each coordinate W_c separately (None for a zero coordinate).

Usage: bmd_cube_line_gcd.py LOG Q U0
       bmd_cube_line_gcd.py minors LOG Q
       bmd_cube_line_gcd.py orders LOG Q U0
"""
import random
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


def newton(xs, ys, q):
    """Interpolating polynomial mod q (coefficients low degree first), O(n^2)."""
    n = len(xs); c = list(ys)
    for j in range(1, n):
        for i in range(n - 1, j - 1, -1):
            c[i] = (c[i] - c[i - 1]) * pow((xs[i] - xs[i - j]) % q, q - 2, q) % q
    poly = [c[n - 1]]
    for i in range(n - 2, -1, -1):
        # poly = poly * (x - xs[i]) + c[i]
        new = [0] * (len(poly) + 1)
        for k, a in enumerate(poly):
            new[k + 1] = (new[k + 1] + a) % q
            new[k] = (new[k] - a * xs[i]) % q
        new[0] = (new[0] + c[i]) % q
        poly = new
    while poly and poly[-1] == 0:
        poly.pop()
    return poly


def mult_at(f, r, q):
    """Multiplicity of the root r of f mod q, and the quotient."""
    k = 0
    while f:
        # synthetic division by (x - r)
        n = len(f); quo = [0] * (n - 1); acc = 0
        for i in range(n - 1, -1, -1):
            acc = (acc * r + f[i]) % q
            if i:
                quo[i - 1] = acc
        if acc:
            break
        f = quo; k += 1
    return k, f


def minors_mode(log, q):
    cases, cur = [], None
    for line in open(log):
        m = re.match(r'd=(\d+) m=(\d+)', line)
        if m:
            cur = {'d': int(m[1]), 'pts': []}; cases.append(cur); continue
        if line.startswith('MIN') and cur:
            v = [int(x) for x in line.split()[1:]]; cur['pts'].append((v[0], v[1:]))
    rng = random.Random(1)
    for c in cases:
        d = c['d']; xs = [u % q for u, _ in c['pts']]
        polys = []
        for _ in range(2):
            coef = [rng.randrange(1, q) for _ in c['pts'][0][1]]
            polys.append(newton(xs, [sum(a * b for a, b in zip(coef, v)) % q for _, v in c['pts']], q))
        assert max(len(p) for p in polys) < len(xs), 'too few points'
        g = pgcd(polys[0], polys[1], q)
        mults = {}
        for r in (0, 1, q - 1):
            k, g = mult_at(g, r, q); mults[r if r < q // 2 else r - q] = k
        psi = d * d // 2
        pred = {0: 2 * d * d + psi, 1: d * d, -1: d * d}
        print(f"d={d}: points {len(xs)}, gcd multiplicities at u=0,1,-1: {mults[0]},{mults[1]},{mults[-1]} "
              f"(predicted {pred[0]},{pred[1]},{pred[-1]}), remaining degree {len(g) - 1}")


def main():
    if sys.argv[1] == 'minors':
        return minors_mode(sys.argv[2], int(sys.argv[3]))
    per_coordinate = sys.argv[1] == 'orders'
    if per_coordinate:
        sys.argv.pop(1)
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
        if per_coordinate:
            orders = []
            for col in range(len(vecs[0])):
                f = interp(xs, [v[col] for v in vecs], q)
                orders.append(mult_at(f, 0, q)[0] if f else None)
            print(f"(d,rho)=({c['d']},{c['rho']}) l={c['l']}: psi={c['d'] ** 2 // 2}, order at u=0 of W_c, c=0..: {orders}")
            continue
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
