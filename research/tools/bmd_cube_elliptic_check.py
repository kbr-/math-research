"""Test the elliptic description of the cube's degree-d orders in dimension 3.

Statement tested (cube elliptic lemma, n = 3).  Over a field of characteristic != 2, at a
specialization y* = a/4 with a_1, a_2, a_3 distinct and nonzero, Ord_3(d) = {0,...,4d-1} fails
exactly when d * 2c_1 = 0 on the genus-one curve C: w_i^2 = 1 + a_i T (origin p0 = (1,1,1),
c_1 = (-1,1,1) above T = 0).  The isogeny (w, T) -> (T, w_1 w_2 w_3) onto
E': Y^2 = (1+a_1T)(1+a_2T)(1+a_3T) sends c_1 to -2P_0 (P_0 = (0,1), origin at infinity) and
has kernel of exponent 2.  So if o = ord(P_0) and o' = ord(4P_0) = o / gcd(o, 4), the least
failing degree d_min is o' or 2o'.

For random a over F_p the script finds d_min <= DMAX by evaluating Delta_{3,d}(y*) (the
determinant of lem:cube-order-determinant, reduced mod p) and computes o on E'(F_p) by
brute force.  It reports each trial and any trial where d_min is not in {o', 2o'} (or no
failure <= DMAX although o' <= DMAX).
Usage: bmd_cube_elliptic_check.py PRIMES(comma-separated) TRIALS DMAX SEED OUT
"""
import itertools, random, sys


def det_nonzero(rows, p):
    A = [r[:] for r in rows]
    size = len(A)
    for c in range(size):
        piv = next((i for i in range(c, size) if A[i][c]), None)
        if piv is None:
            return False
        A[c], A[piv] = A[piv], A[c]
        iv = pow(A[c][c], p - 2, p)
        for i in range(c + 1, size):
            if A[i][c]:
                f = A[i][c] * iv % p
                A[i] = [(x - f * y) % p for x, y in zip(A[i], A[c])]
    return True


def delta_nonzero(ys, d, p, cat):
    n = len(ys)
    basis = [(Q, r) for Q in range(d // 2 + 1) for r in itertools.product([0, 1], repeat=n)
             if 2 * Q + sum(r) <= d and (Q, r) != (0, (0,) * n)]
    M = len(basis) + 1
    z = [[0] + [(-1) ** j * cat[j - 1] * pow(y, j, p) % p for j in range(1, M)] for y in ys]

    def mul(u, v):
        out = [0] * M
        for i, x in enumerate(u):
            if x:
                for j in range(M - i):
                    out[i + j] = (out[i + j] + x * v[j]) % p
        return out

    cols = []
    for Q, r in basis:
        s = [0] * M
        s[Q] = 1
        for i in range(n):
            if r[i]:
                s = mul(s, z[i])
        cols.append(s[1:M])
    size = len(basis)
    return det_nonzero([[cols[j][i] for j in range(size)] for i in range(size)], p)


def point_order(a, p):
    """Order of P_0 = (0,1) on Y^2 = prod(1 + a_i T), via the monic model X = cT, Y' = cY."""
    c = a[0] * a[1] * a[2] % p
    e1 = sum(a) % p
    e2 = (a[0] * a[1] + a[0] * a[2] + a[1] * a[2]) % p
    A2, A4 = e2, e1 * c % p
    P = (0, c)

    def add(U, V):
        if U is None:
            return V
        if V is None:
            return U
        (x1, y1), (x2, y2) = U, V
        if x1 == x2 and (y1 + y2) % p == 0:
            return None
        if U == V:
            lam = (3 * x1 * x1 + 2 * A2 * x1 + A4) * pow(2 * y1, p - 2, p) % p
        else:
            lam = (y2 - y1) * pow(x2 - x1, p - 2, p) % p
        x3 = (lam * lam - A2 - x1 - x2) % p
        return (x3, (-(y1 + lam * (x3 - x1))) % p)

    Q, o = P, 1
    while Q is not None:
        Q, o = add(Q, P), o + 1
    return o


def main():
    primes = [int(x) for x in sys.argv[1].split(',')]
    trials, dmax, seed, out = int(sys.argv[2]), int(sys.argv[3]), int(sys.argv[4]), sys.argv[5]
    rng = random.Random(seed)
    cat = [1]
    for j in range(1, 8 * dmax):
        cat.append(cat[-1] * 2 * (2 * j - 1) // (j + 1))
    bad, tested = [], 0
    with open(out, 'w') as fh:
        for p in primes:
            assert p % 2 == 1 and p >= 5  # three distinct nonzero a_i
            inv4 = pow(4, p - 2, p)
            for _ in range(trials):
                while True:
                    a = [rng.randrange(1, p) for _ in range(3)]
                    if len(set(a)) == 3:
                        break
                ys = [x * inv4 % p for x in a]
                o = point_order(a, p)
                from math import gcd
                op = o // gcd(o, 4)
                dmin = next((d for d in range(1, dmax + 1) if not delta_nonzero(ys, d, p, cat)), None)
                ok = (dmin in (op, 2 * op)) if dmin is not None else (op > dmax)
                tested += 1
                line = f'p={p} a={a} ord(P0)={o} o\'={op} d_min={dmin} {"ok" if ok else "MISMATCH"}'
                print(line, flush=True)
                fh.write(line + '\n')
                fh.flush()
                if not ok:
                    bad.append(line)
        summary = f'tested {tested} specializations; mismatches: {len(bad)}'
        print(summary)
        fh.write(summary + '\n')


if __name__ == '__main__':
    main()
