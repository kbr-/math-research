"""Orders of polynomials in the root curve z_i = x(y_i T), for a four-element subspace S.

Statement tested.  Let S be a four-element F_2-subspace of GF(2^a) with c_1 != 0, x(y) the additive
root of L(x) = prod_{t in S}(x - t) = y, and z_i = x(y_i T) in K[[T]], K = F(y_1, y_2).  Let
Orders(d) be the set of T-orders of nonzero K-linear combinations of z_1^a z_2^b, a + b <= d.  The
root-curve argument predicts Orders(d) = {m : H(m) <= d}, H(m) = 2 floor(m/8) + ceil((m mod 8)/2),
and |Orders(d)| = C(d+2,2) - C(d-2,2).

The check specializes y_1, y_2 to random elements of GF(2^a) (a generic specialization gives the
same orders with high probability; a special one can only lose orders), expands the monomials mod
T^M, and reads the orders off a Gaussian elimination by increasing T-degree.  It also checks the
counting identity #{m : H(m) <= d} = C(d+2,2) - C(d-2,2) for d <= 40.
Usage: bmd_root_curve_orders.py a poly S0 S1 S2 S3 DMAX TRIALS SEED
"""
import random, sys
from math import comb


def main():
    a, poly = int(sys.argv[1]), int(sys.argv[2])
    S = [int(v) for v in sys.argv[3:7]]
    dmax, trials, seed = int(sys.argv[7]), int(sys.argv[8]), int(sys.argv[9])
    Q = 1 << a
    mul = [[0] * Q for _ in range(Q)]
    for u in range(Q):
        for v in range(Q):
            r, x, y = 0, u, v
            while y:
                if y & 1:
                    r ^= x
                y >>= 1
                x <<= 1
                if x & Q:
                    x ^= poly
            mul[u][v] = r
    inv = [0] * Q
    for u in range(1, Q):
        inv[u] = next(v for v in range(1, Q) if mul[u][v] == 1)
    assert sorted({s ^ t for s in S for t in S}) == sorted(S) and len(set(S)) == 4
    L = [1]
    for t in S:
        L = [0] + L
        for i in range(len(L) - 1):
            L[i] ^= mul[t][L[i + 1]]
    c0, c1 = L[1], L[2]
    assert c1 != 0, 'S is a scaled F_4'
    M = 4 * dmax + 12
    # additive root coefficients a_u: c0 a_u = c1 a_(u-1)^2 + a_(u-2)^4
    A = [inv[c0]]
    while (1 << len(A)) < M:
        u = len(A)
        acc = mul[c1][mul[A[u - 1]][A[u - 1]]]
        if u >= 2:
            sq = mul[A[u - 2]][A[u - 2]]
            acc ^= mul[sq][sq]
        A.append(mul[inv[c0]][acc])

    def smul(f, g):
        h = [0] * M
        for i, fi in enumerate(f):
            if fi:
                for j in range(M - i):
                    if g[j]:
                        h[i + j] ^= mul[fi][g[j]]
        return h

    for c in range(41):
        H_count = sum(1 for m in range(8 * c + 8) if 2 * (m // 8) + (m % 8 + 1) // 2 <= c)
        assert H_count == comb(c + 2, 2) - (comb(c - 2, 2) if c >= 4 else 0), c
    rng = random.Random(seed)
    for trial in range(trials):
        y = [rng.randrange(1, Q) for _ in range(2)]
        z = []
        for yi in y:
            s, p = [0] * M, yi
            for u, au in enumerate(A):
                if (1 << u) < M:
                    s[1 << u] = mul[au][p]
                p = mul[p][p]
            z.append(s)
        pw = [[[1] + [0] * (M - 1)], [[1] + [0] * (M - 1)]]
        for i in range(2):
            for _ in range(dmax):
                pw[i].append(smul(pw[i][-1], z[i]))
        rowsets = {}
        for d in range(dmax + 1):
            vecs = [smul(pw[0][e], pw[1][d - e]) for e in range(d + 1)]
            rowsets[d] = rowsets.get(d - 1, []) + vecs
            basis = {}
            for v in rowsets[d]:
                v = list(v)
                while True:
                    lead = next((i for i, x in enumerate(v) if x), None)
                    if lead is None or lead not in basis:
                        break
                    f = v[lead]
                    v = [x ^ mul[f][b] for x, b in zip(v, basis[lead])]
                if lead is not None:
                    iv = inv[v[lead]]
                    basis[lead] = [mul[iv][x] for x in v]
            orders = sorted(basis)
            predicted = sorted(m for m in range(M) if 2 * (m // 8) + (m % 8 + 1) // 2 <= d)
            count = comb(d + 2, 2) - (comb(d - 2, 2) if d >= 4 else 0)
            status = 'match' if orders == predicted and len(orders) == count else 'DIFFER'
            print(f'trial {trial} y={y} d={d}: {len(orders)} orders, predicted {count}: {status}'
                  + ('' if status == 'match' else f' got {orders} predicted {predicted}'), flush=True)


if __name__ == '__main__':
    main()
