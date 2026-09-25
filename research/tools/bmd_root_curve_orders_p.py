"""Root-curve orders in characteristic p, compared with the q-ary per-order law.

Statement tested.  For S = F_q (q = p^b) inside GF(p^a), L = x^q - x, additive root x(y) with
L(x(y)) = y, and z_i = x(y_i T) (i <= n), the characteristic-p root-curve theory predicts
Ord(d) = {m : H(m) <= d}, H(m) = q floor(m/q^n) + s_q(m mod q^n) (the savings of the q-ary theorem),
and |Ord(d)| = N_{q,n}(d) = #{(Q,r) in N x [0,q-1]^n : qQ + |r| <= d}.  The script builds GF(p^a)
from a primitive polynomial found by search, specializes y at random, and computes Ord(d) by
Gaussian elimination modulo T^M.
Usage: bmd_root_curve_orders_p.py p a b n DMAX TRIALS SEED
"""
import itertools, random, sys


def main():
    p, a, b, n, dmax, trials, seed = map(int, sys.argv[1:8])
    assert a % b == 0
    Q = p ** a

    def pmulmod(u, v, f):  # polynomials over F_p as coefficient lists, reduced mod monic f
        r = [0] * (len(u) + len(v) - 1)
        for i, x in enumerate(u):
            if x:
                for j, y in enumerate(v):
                    r[i + j] = (r[i + j] + x * y) % p
        for i in range(len(r) - 1, a - 1, -1):
            c = r[i]
            if c:
                for j in range(a + 1):
                    r[i - a + j] = (r[i - a + j] - c * f[j]) % p
        return (r + [0] * a)[:a]

    def enc(v):
        return sum(c * p ** i for i, c in enumerate(v))

    def dec(x):
        return [(x // p ** i) % p for i in range(a)]

    # find a primitive polynomial f of degree a: x has multiplicative order p^a - 1
    for tail in itertools.product(range(p), repeat=a):
        f = list(tail) + [1]
        if f[0] == 0:
            continue
        x, e, ok = [0, 1] + [0] * (a - 2), 1, True
        cur = x[:]
        order = None
        for e in range(1, Q):
            if cur == [1] + [0] * (a - 1):
                order = e
                break
            cur = pmulmod(cur, x, f)
        if order == Q - 1:
            break
    mul = [[0] * Q for _ in range(Q)]
    D = [dec(x) for x in range(Q)]
    for u in range(Q):
        for v in range(u, Q):
            mul[u][v] = mul[v][u] = enc(pmulmod(D[u], D[v], f))
    add = [[enc([(x + y) % p for x, y in zip(D[u], D[v])]) for v in range(Q)] for u in range(Q)]
    neg = [enc([(-x) % p for x in D[u]]) for u in range(Q)]
    inv = [0] * Q
    for u in range(1, Q):
        inv[u] = next(v for v in range(1, Q) if mul[u][v] == 1)
    q = p ** b
    # x(y) = -sum_u y^(q^u): root of X^q - X = y
    s = q

    def H(m):
        Qm, r = divmod(m, q ** n)
        dig = 0
        while r:
            dig += r % q
            r //= q
        return q * Qm + dig

    top = max(m for m in range(q ** n * (dmax + 2)) if H(m) <= dmax)
    M = top + 4

    def smul(fs, gs):
        h = [0] * M
        for i, x in enumerate(fs):
            if x:
                for j in range(M - i):
                    if gs[j]:
                        h[i + j] = add[h[i + j]][mul[x][gs[j]]]
        return h

    rng = random.Random(seed)
    one = enc([1] + [0] * (a - 1))
    for trial in range(trials):
        y = [rng.randrange(1, Q) for _ in range(n)]
        z = []
        for yi in y:
            ser, pw, e = [0] * M, yi, 1
            while e < M:
                ser[e] = neg[pw]
                for _ in range(b):  # pw <- pw^p, b times: pw^(q)
                    t = pw
                    for _ in range(p - 1):
                        t = mul[t][pw]
                    pw = t
                e *= q
            z.append(ser)
        layers = [[((0,) * n, [one] + [0] * (M - 1))]]
        for d in range(1, dmax + 1):
            seen, layer = set(), []
            for e_, ser in layers[-1]:
                for i in range(n):
                    e2 = tuple(e_[j] + (j == i) for j in range(n))
                    if e2 not in seen:
                        seen.add(e2)
                        layer.append((e2, smul(ser, z[i])))
            layers.append(layer)
        basis = {}
        for d in range(dmax + 1):
            for _, v in layers[d]:
                v = list(v)
                while True:
                    lead = next((i for i, x in enumerate(v) if x), None)
                    if lead is None or lead not in basis:
                        break
                    c = v[lead]
                    v = [add[x][neg[mul[c][bb]]] for x, bb in zip(v, basis[lead])]
                if lead is not None:
                    iv = inv[v[lead]]
                    basis[lead] = [mul[iv][x] for x in v]
            orders = sorted(basis)
            predicted = sorted(m for m in range(M) if H(m) <= d)
            status = 'match' if orders == predicted else 'DIFFER'
            print(f'p={p} q={q} n={n} trial {trial} d={d}: |Ord|={len(orders)}, #{{H<=d}}={len(predicted)}: {status}',
                  flush=True)


if __name__ == '__main__':
    main()
