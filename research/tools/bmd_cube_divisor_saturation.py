"""Saturate the cube's constraint lattice along a linear divisor and test for a forced vanishing.

Statement tested.  Let W be a polynomial solution of the threshold-ideal system (lem:cube-threshold-ideal)
for savings d+1 at m on {0,1}^n: W_c in F[y], W kills the truncations (T^0..T^m) of V_{n,d}.  Along a
prime divisor D = {y_1 = alpha y_2 + beta y_3} (local parameter s = y_1 - alpha y_2 - beta y_3), W also kills
the saturation of the lattice tau(V) over O = F(y_2,y_3)[[s]].  If the reduction mod s of that
saturation contains the vector e_m (an element congruent to T^m), then W_m vanishes on D for every
solution, so D divides every element of the threshold ideal I^{(d+1)}_m.

The script fixes y_2, y_3 at random values of F_p (generic residue point), writes y_1 = alpha y_2 +
beta y_3 + s, saturates by repeated division of reduced dependencies by s (truncated series in s), and
reports the number of division steps (the s-valuation of the gcd of the maximal minors), the orders
(pivot positions) of the reduced saturated span, and whether e_m lies in it.
Usage: bmd_cube_divisor_saturation.py p n d m ALPHA BETA PREC SEED
"""
import itertools, random, sys
import numpy as np


def main():
    p, n, d, m, alpha, beta, prec, seed = map(int, sys.argv[1:9])
    rng = random.Random(seed)
    y2, y3 = rng.randrange(1, p), rng.randrange(1, p)
    base = [(alpha * y2 + beta * y3) % p, y2, y3][:n] + [rng.randrange(1, p) for _ in range(max(0, n - 3))]
    M = m + 1
    cat = [1]
    for j in range(1, M + 2):
        cat.append(cat[-1] * 2 * (2 * j - 1) // (j + 1))
    # series in s for y_i: y_1 = base_1 + s, others constant; arrays shape (M, prec): [T^c][s^k]
    def zser(i):
        z = np.zeros((M, prec), dtype=np.int64)
        yi = np.zeros(prec, dtype=np.int64)
        yi[0] = base[i] % p
        if i == 0 and prec > 1:
            yi[1] = 1
        pw = np.zeros(prec, dtype=np.int64)
        pw[0] = 1
        for j in range(1, M):
            pw = np.convolve(pw, yi)[:prec] % p
            z[j] = ((-1) ** j * cat[j - 1]) % p * pw % p
        return z

    zs = [zser(i) for i in range(n)]

    def mul(a, b):  # product of T-series with s-series coefficients, truncated
        out = np.zeros((M, prec), dtype=np.int64)
        for i in range(M):
            if a[i].any():
                for j in range(M - i):
                    if b[j].any():
                        out[i + j] = (out[i + j] + np.convolve(a[i], b[j])[:prec]) % p
        return out

    rows = []
    for Q in range(d // 2 + 1):
        for r in itertools.product([0, 1], repeat=n):
            if 2 * Q + sum(r) <= d:
                f = np.zeros((M, prec), dtype=np.int64)
                if Q < M:
                    f[Q, 0] = 1
                for i in range(n):
                    if r[i]:
                        f = mul(f, zs[i])
                rows.append(f)
    N = len(rows)
    steps = 0
    while True:
        R = np.array([f[:, 0] for f in rows], dtype=np.int64) % p  # reduced rows, N x M
        # find a dependency among reduced rows: left kernel of R
        A = np.concatenate([R, np.eye(N, dtype=np.int64)], axis=1) % p
        r_ = 0
        for c in range(M):
            piv = next((i for i in range(r_, N) if A[i, c]), None)
            if piv is None:
                continue
            A[[r_, piv]] = A[[piv, r_]]
            A[r_] = A[r_] * pow(int(A[r_, c]), p - 2, p) % p
            for i in range(N):
                if i != r_ and A[i, c]:
                    A[i] = (A[i] - A[i, c] * A[r_]) % p
            r_ += 1
        if r_ == N:
            break
        coeffs = A[r_, M:]  # a dependency: sum coeffs_i * R_i = 0
        j = int(np.nonzero(coeffs)[0][0])
        comb = np.zeros((M, prec), dtype=np.int64)
        for i in np.nonzero(coeffs)[0]:
            comb = (comb + int(coeffs[i]) * rows[i]) % p
        if comb[:, 0].any():
            raise RuntimeError('dependency not divisible by s')
        new = np.zeros((M, prec), dtype=np.int64)
        new[:, :-1] = comb[:, 1:]
        rows[j] = new
        steps += 1
        if steps > 10 * prec:
            raise RuntimeError('too many steps; raise PREC')
    R = np.array([f[:, 0] for f in rows], dtype=np.int64) % p
    # echelon from the left to read orders; test e_m in span
    A = R.copy()
    orders, r_ = [], 0
    for c in range(M):
        piv = next((i for i in range(r_, N) if A[i, c]), None)
        if piv is None:
            continue
        A[[r_, piv]] = A[[piv, r_]]
        A[r_] = A[r_] * pow(int(A[r_, c]), p - 2, p) % p
        for i in range(N):
            if i != r_ and A[i, c]:
                A[i] = (A[i] - A[i, c] * A[r_]) % p
        orders.append(c)
        r_ += 1
    em_in = m in orders  # the reduced pivot row at the last column is e_m itself
    print(f'n={n} d={d} m={m} divisor y1={alpha}y2+{beta}y3: N={N}, saturation steps (valuation of gcd) = {steps}, '
          f'reduced orders = {orders}, e_m in reduced saturation: {em_in}')


if __name__ == '__main__':
    main()
