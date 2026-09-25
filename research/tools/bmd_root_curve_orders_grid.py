"""Root-curve orders for an arbitrary finite grid S^n (0 in S) over GF(p^a).

Statement tested (stable law on finite grids).  With L = prod_{t in S}(x - t), r(y) the root of
L(X) = y with r(0) = 0 (a power series since L'(0) != 0), and z_i = r(y_i T), the set Ord(d) of
T-orders of polynomials of degree <= d in z has exactly N_{s,n}(d) elements, and kappa(m) =
min{d : m in Ord(d)} bounds the per-order savings n(s-1) + s(k-1) - delta_S(n,k,l) for every l,
with equality for large l.  The script specializes y at random in GF(p^a), prints |Ord(d)| against
N_{s,n}(d) and a KAPPA line per trial, for comparison with kernel data (bmd_kappa_compare.py).
S is given as field elements encoded base p (digit i = coefficient of the i-th power of the
generator of the primitive polynomial found by search), e.g. S = 0 1 for the cube.
An optional token M=VALUE sets the T-truncation (default s^n (DMAX+2)/2 + 8); with a smaller M,
orders >= M are invisible, so only kappa(m) for m < M is reported reliably.
Usage: bmd_root_curve_orders_grid.py p a n DMAX TRIALS SEED [M=VALUE] S0 S1 ...
   or: bmd_root_curve_orders_grid.py --batch OUTDIR PREFIX 'p a n DMAX TRIALS SEED S0 S1 ...' ...
"""
import itertools, random, sys


def run(args, out):
    p, a, n, dmax, trials, seed = map(int, args[:6])
    Mset = [int(v[2:]) for v in args[6:] if v.startswith('M=')]
    S = [int(v) for v in args[6:] if not v.startswith('M=')]
    assert 0 in S and len(set(S)) == len(S)
    Q = p ** a

    def pmulmod(u, v, f):
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

    for tail in itertools.product(range(p), repeat=a):
        f = list(tail) + [1]
        if f[0] == 0:
            continue
        x = [0, 1] + [0] * (a - 2) if a > 1 else [f[0] and (-f[0]) % p]
        cur, order = x[:], None
        for e in range(1, Q):
            if cur == [1] + [0] * (a - 1):
                order = e
                break
            cur = pmulmod(cur, x, f)
        if order == Q - 1 or a == 1:
            break
    D = [dec(x) for x in range(Q)]
    mul = [[0] * Q for _ in range(Q)]
    for u in range(Q):
        for v in range(u, Q):
            mul[u][v] = mul[v][u] = enc(pmulmod(D[u], D[v], f)) if a > 1 else (u * v) % p
    add = [[enc([(x + y) % p for x, y in zip(D[u], D[v])]) for v in range(Q)] for u in range(Q)]
    neg = [enc([(-x) % p for x in D[u]]) for u in range(Q)]
    inv = [0] * Q
    for u in range(1, Q):
        inv[u] = next(v for v in range(1, Q) if mul[u][v] == 1)
    one = 1
    s = len(S)
    # L = prod (x - t), coefficients low to high
    L = [one]
    for t in S:
        nt = neg[t]
        new = [0] * (len(L) + 1)
        for i, c in enumerate(L):
            new[i + 1] = add[new[i + 1]][c]
            new[i] = add[new[i]][mul[nt][c]]
        L = new
    assert L[0] == 0 and L[1] != 0 and L[s] == one

    def N(d):
        counts = [1]
        for _ in range(n):
            new = [0] * (len(counts) + s - 1)
            for i, cnt in enumerate(counts):
                for j in range(s):
                    new[i + j] += cnt
            counts = new
        return sum(cnt for Qd in range(0, d + 1, s) for i, cnt in enumerate(counts) if i <= d - Qd)

    M = Mset[0] if Mset else s ** n * (dmax + 2) // 2 + 8  # T-truncation; orders >= M are not seen

    def smul(fs, gs):
        h = [0] * M
        for i, x in enumerate(fs):
            if x:
                for j in range(M - i):
                    if gs[j]:
                        h[i + j] = add[h[i + j]][mul[x][gs[j]]]
        return h

    def root_series(yv):
        """r with L(r) = yv*T mod T^M: r = (yv T - (L(r) - L[1] r)) / L[1], iterated."""
        c1inv = inv[L[1]]
        r = [0] * M
        target = [0] * M
        target[1] = yv
        for _ in range(M):
            pw, acc = [one] + [0] * (M - 1), [0] * M
            for i in range(s + 1):
                if i >= 2 and L[i]:
                    acc = [add[u][mul[L[i]][v]] for u, v in zip(acc, pw)]
                pw = smul(pw, r)
            new = [mul[c1inv][add[t][neg[u]]] for t, u in zip(target, acc)]
            if new == r:
                break
            r = new
        return r

    rng = random.Random(seed)
    for trial in range(trials):
        y = [rng.randrange(1, Q) for _ in range(n)]
        z = [root_series(yi) for yi in y]
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
        basis, kappa = {}, {}
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
            for m in basis:
                kappa.setdefault(m, d)
            print(f'subspace S={S} n={n} trial {trial} y={y} d={d}: |Ord|={len(basis)}, N={N(d)}: '
                  + ('count match' if len(basis) == N(d) else 'COUNT DIFFER'), file=out, flush=True)
        print(f'KAPPA trial {trial}: ' + ' '.join(f'{m}:{kappa[m]}' for m in sorted(kappa)), file=out, flush=True)
        print(f'MISSING below M={M}: ' + ' '.join(str(m) for m in range(M) if m not in kappa), file=out, flush=True)


def main():
    if sys.argv[1] == '--batch':
        # --batch OUTDIR PREFIX 'p a n dmax trials seed S...' ... : one file per spec, one process
        outdir, prefix = sys.argv[2], sys.argv[3]
        for spec in sys.argv[4:]:
            args = spec.split()
            path = f'{outdir}/{prefix}-p{args[0]}-a{args[1]}-n{args[2]}.txt'
            with open(path, 'w') as out:
                run(args, out)
            print('wrote', path, flush=True)
    else:
        run(sys.argv[1:], sys.stdout)


if __name__ == '__main__':
    main()
