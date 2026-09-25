"""Orders on the root curve in n variables, compared with a proved per-order law.

Statement tested.  For an F_2-subspace S of GF(2^a) with L = prod_{t in S}(x - t) and additive root
x(y), put z_i = x(y_i T), i = 1..n.  Let Ord(d) be the set of T-orders of combinations of the
monomials z^e with |e| <= d over K = F(y_1..y_n).  The n-variable form of the root-curve lemma says
that savings h at m force m notin Ord(h-1).  A law with savings H(m) that is attained therefore
gives Ord(d) inside {m : H(m) <= d}, and the lower bound follows by counting exactly when
|Ord(d)| = #{m : H(m) <= d}.  This script computes |Ord(d)| (and the set) at random y in GF(2^a)
and compares with the law named on the command line:
  binary: S = {0,1},        H(m) = 2 floor(m/2^n) + s_2(m mod 2^n)   (all-dimension theorem)
  qary4:  S = F_4 in GF(4^j), H(m) = 4 floor(m/4^n) + s_4(m mod 4^n) (q-ary theorem, q = 4)
Field arithmetic is carry-less multiplication modulo poly, so a may be large (generic y).
  subspace: S given after SEED; prints |Ord(d)| against N_{s,n}(d) and kappa(m) = min{d : m in Ord(d)}
Usage: bmd_root_curve_orders_n.py LAW a poly n DMAX TRIALS SEED [S0 S1 ...]
"""
import random, sys


def main():
    law, a, poly, n, dmax, trials, seed = sys.argv[1], *map(int, sys.argv[2:8])
    Q = 1 << a

    def mul(u, v):
        r = 0
        while v:
            if v & 1:
                r ^= u
            v >>= 1
            u <<= 1
            if u & Q:
                u ^= poly
        return r

    def inv(u):
        r, e = 1, Q - 2
        while e:
            if e & 1:
                r = mul(r, u)
            u = mul(u, u)
            e >>= 1
        return r

    if law == 'binary':
        S, base = [0, 1], 2
    elif law == 'qary4':
        assert a % 2 == 0
        w = 1
        e = (Q - 1) // 3
        g = 2
        while True:  # find an element of order 3: omega = g^((Q-1)/3) with omega != 1
            r, b, x = 1, e, g
            while b:
                if b & 1:
                    r = mul(r, x)
                x = mul(x, x)
                b >>= 1
            if r != 1:
                w = r
                break
            g += 1
        S, base = [0, 1, w, w ^ 1], 4
    elif law == 'subspace':
        S, base = [int(v) for v in sys.argv[8:]], None
        assert len({u ^ v for u in S for v in S} | set(S)) == len(S), 'S is not an additive subgroup'
    else:
        raise SystemExit('law must be binary, qary4 or subspace')
    L = [1]
    for t in S:
        L = [0] + L
        for i in range(len(L) - 1):
            L[i] ^= mul(t, L[i + 1])
    s = len(S)
    dd = s.bit_length() - 1
    c = [L[1 << i] for i in range(dd + 1)]

    def N(d):  # #{(Q, r) in N x [0, s-1]^n : sQ + |r| <= d}
        counts = [1]
        for _ in range(n):
            new = [0] * (len(counts) + s - 1)
            for i, cnt in enumerate(counts):
                for j in range(s):
                    new[i + j] += cnt
            counts = new
        return sum(cnt for Qd in range(0, d + 1, s) for i, cnt in enumerate(counts) if i <= d - Qd)

    def H(m):
        if base is None:
            return None
        q, r = divmod(m, base ** n)
        digits = 0
        while r:
            digits += r % base
            r //= base
        return base * q + digits

    if base is None:
        M = s ** n * (dmax + 2) // 2 + 8
    else:
        top = max(m for m in range(base ** n * (dmax + 2)) if H(m) <= dmax)
        M = top + 4
    A = [inv(c[0])]
    while (1 << len(A)) < M:
        u = len(A)
        acc = 0
        for i in range(1, dd + 1):
            if u - i >= 0:
                p = A[u - i]
                for _ in range(i):
                    p = mul(p, p)
                acc ^= mul(c[i], p)
        A.append(mul(A[0], acc))

    def smul(f, g):
        h = [0] * M
        for i, fi in enumerate(f):
            if fi:
                for j in range(M - i):
                    if g[j]:
                        h[i + j] ^= mul(fi, g[j])
        return h

    rng = random.Random(seed)
    for trial in range(trials):
        y = [rng.randrange(1, Q) for _ in range(n)]
        z = []
        for yi in y:
            ser, p = [0] * M, yi
            for u, au in enumerate(A):
                if (1 << u) < M:
                    ser[1 << u] = mul(au, p)
                p = mul(p, p)
            z.append(ser)
        # monomials of total degree <= d, built degree by degree
        layers = [[((0,) * n, [1] + [0] * (M - 1))]]
        for d in range(1, dmax + 1):
            seen, layer = set(), []
            for e, ser in layers[-1]:
                for i in range(n):
                    e2 = tuple(e[j] + (j == i) for j in range(n))
                    if e2 not in seen:
                        seen.add(e2)
                        layer.append((e2, smul(ser, z[i])))
            layers.append(layer)
        basis, kappa = {}, {}
        for d in range(dmax + 1):
            for _, v in layers[d]:
                v = list(v)
                while True:
                    lead = next((i for i, x in enumerate(v) if x), None)
                    if lead is None or lead not in basis:
                        break
                    f = v[lead]
                    v = [x ^ mul(f, b) for x, b in zip(v, basis[lead])]
                if lead is not None:
                    iv = inv(v[lead])
                    basis[lead] = [mul(iv, x) for x in v]
            orders = sorted(basis)
            for m in orders:
                kappa.setdefault(m, d)
            if base is None:
                print(f'subspace S={S} n={n} trial {trial} y={y} d={d}: |Ord|={len(orders)}, N={N(d)}: '
                      + ('count match' if len(orders) == N(d) else 'COUNT DIFFER'), flush=True)
                continue
            predicted = sorted(m for m in range(M) if H(m) <= d)
            status = 'match' if orders == predicted else 'DIFFER'
            print(f'{law} n={n} trial {trial} d={d}: |Ord|={len(orders)}, #{{H<=d}}={len(predicted)}: {status}'
                  + ('' if status == 'match' else f' got {orders} predicted {predicted}'), flush=True)
        if base is None:
            print(f'KAPPA trial {trial}: ' + ' '.join(f'{m}:{kappa[m]}' for m in sorted(kappa)), flush=True)


if __name__ == '__main__':
    main()
