"""Certify the cube's order determinant Delta_{n,d} modulo p by evaluation at random points.

Statement tested (refined initial-segment law).  For every odd prime p, n >= 1 and d >= 2,
Delta_{n,d} is not identically 0 modulo p.  The script evaluates the mod-p reduction of the integer
matrix defining Delta_{n,d}, so a single point y* in GF(p^a)^n with Delta_{n,d}(y*) != 0 certifies
this exactly, and with it (lem:cube-order-determinant, part 1) the law at (n, d) over every field
of characteristic p and of characteristic 0.  Points are sampled with nonzero coordinates.  The script evaluates the
matrix of coefficients of T^1..T^(N-1) in the basis T^Q z^r (r in {0,1}^n, 2Q + |r| <= d,
(Q,r) != 0), z_i = sum_j (-1)^j C_(j-1) (y_i T)^j, at up to TRIALS random points of GF(p^a),
p^a >= QMIN, and reports the first nonzero determinant or failure.
With --with-2 it first runs p = 2 as a negative control (the computed contents are powers of 2).
Cases with N_{2,n}(d) > 50 are skipped.
Usage: bmd_cube_det_certify.py NMAX DMAX PMAX TRIALS QMIN SEED [--with-2]
"""
import itertools, random, sys


NMAXSIZE = 50  # skip (n, d) with N_{2,n}(d) above this (matrix size N-1)


def primes_upto(n):
    return [q for q in range(3, n + 1) if all(q % r for r in range(2, int(q ** 0.5) + 1))]


class GF:
    def __init__(self, p, qmin):
        a = 1
        while p ** a < qmin:
            a += 1
        self.p, self.a, self.Q = p, a, p ** a
        # find a primitive polynomial by brute force and build exp/log tables
        for tail in itertools.product(range(p), repeat=a):
            f = list(tail) + [1]
            if f[0] == 0:
                continue
            exp, cur, seen = [], [1] + [0] * (a - 1), set()
            ok = True
            for _ in range(self.Q - 1):
                code = self.enc(cur)
                if code in seen:
                    ok = False
                    break
                seen.add(code)
                exp.append(code)
                cur = self.times_x(cur, f)
            if ok and len(seen) == self.Q - 1:
                break
        self.exp = exp
        self.log = {c: i for i, c in enumerate(exp)}
        # addition and negation tables (Q <= a few thousand); multiplication through a product table
        digits = [self.dec(x) for x in range(self.Q)]
        self.addt = [[self.enc([(x + y) % p for x, y in zip(digits[u], digits[v])]) for v in range(self.Q)]
                     for u in range(self.Q)]
        self.negt = [self.enc([(-x) % p for x in digits[u]]) for u in range(self.Q)]
        L, E, M1 = self.log, self.exp, self.Q - 1
        self.mult = [[0] * self.Q] + [[0] + [E[(L[u] + L[v]) % M1] for v in range(1, self.Q)]
                                      for u in range(1, self.Q)]

    def enc(self, v):
        return sum(c * self.p ** i for i, c in enumerate(v))

    def dec(self, x):
        return [(x // self.p ** i) % self.p for i in range(self.a)]

    def times_x(self, v, f):
        a, p = self.a, self.p
        top = v[-1]
        w = [0] + v[:-1]
        return [(w[i] - top * f[i]) % p for i in range(a)]

    def add(self, u, v):
        return self.addt[u][v]

    def neg(self, u):
        return self.negt[u]

    def mul(self, u, v):
        return self.mult[u][v]

    def inv(self, u):
        return self.exp[(-self.log[u]) % (self.Q - 1)]

    def from_int(self, c):
        return self.enc([c % self.p] + [0] * (self.a - 1))


def N2(n, d):
    counts = [1]
    for _ in range(n):
        new = [0] * (len(counts) + 1)
        for i, c in enumerate(counts):
            new[i] += c
            new[i + 1] += c
        counts = new
    return sum(c for Qd in range(0, d + 1, 2) for i, c in enumerate(counts) if i <= d - Qd)


def det_at(F, n, d, ys, cat):
    basis = [(Q, r) for Q in range(d // 2 + 1) for r in itertools.product([0, 1], repeat=n)
             if 2 * Q + sum(r) <= d and (Q, r) != (0, (0,) * n)]
    M = len(basis) + 1
    z = []
    for y in ys:
        s, pw = [0] * M, 1
        for j in range(1, M):
            pw = F.mul(pw, y)
            c = F.from_int((-1) ** j * cat[j - 1])
            s[j] = F.mul(c, pw)
        z.append(s)

    def smul(a, b):
        out = [0] * M
        for i, x in enumerate(a):
            if x:
                for j in range(M - i):
                    if b[j]:
                        out[i + j] = F.add(out[i + j], F.mul(x, b[j]))
        return out

    cols = []
    for Q, r in basis:
        s = [0] * M
        s[Q] = 1
        for i in range(n):
            if r[i]:
                s = smul(s, z[i])
        cols.append(s[1:M])
    size = len(basis)
    A = [[cols[j][i] for j in range(size)] for i in range(size)]
    for c in range(size):
        piv = next((i for i in range(c, size) if A[i][c]), None)
        if piv is None:
            return 0
        A[c], A[piv] = A[piv], A[c]
        iv = F.inv(A[c][c])
        for i in range(c + 1, size):
            if A[i][c]:
                nf = F.negt[F.mul(A[i][c], iv)]
                add, mrow = F.addt, F.mult[nf]
                A[i] = [add[x][mrow[y]] for x, y in zip(A[i], A[c])]
    return 1


def main():
    nmax, dmax, pmax, trials, qmin, seed = map(int, sys.argv[1:7])
    control = '--with-2' in sys.argv  # negative control: p = 2, where the contents vanish
    rng = random.Random(seed)
    cat = [1]
    for j in range(1, 200):
        cat.append(cat[-1] * 2 * (2 * j - 1) // (j + 1))
    fails = []
    for p in ([2] if control else []) + primes_upto(pmax):
        F = GF(p, qmin)
        for n in range(2, nmax + 1):
            for d in range(2, dmax + 1):
                if N2(n, d) > NMAXSIZE:
                    continue
                ok_trial = None
                for t in range(trials):
                    ys = [rng.randrange(1, F.Q) for _ in range(n)]
                    if det_at(F, n, d, ys, cat):
                        ok_trial = t
                        break
                print(f'p={p} (GF({p}^{F.a})) n={n} d={d} N={N2(n, d)}: '
                      + (f'certified at trial {ok_trial}' if ok_trial is not None else 'NO CERTIFICATE'), flush=True)
                if ok_trial is None:
                    fails.append((p, n, d))
    print(f'uncertified (p, n, d): {fails}')


if __name__ == '__main__':
    main()
