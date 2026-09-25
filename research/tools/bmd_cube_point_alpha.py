"""Hilbert function of the saturated ideal I_Z of the 3-cube's zero scheme, from its local stalks.

Statement computed.  By lem:cube-threshold-zero-scheme, for rho >= 2 the threshold ideal I_m lies in
I_Z, the ideal of a zero-dimensional scheme Z at the arrangement's multiple points, and
l_0 >= alpha(Z).  Given the stalk J_{Z,P} modulo m_P^K at the double point P = (1:1:0), as the
echelon rows written by bmd_cube_point_scheme (a form f lies in J_P mod m^K iff every row kills the
jet of f at P), and assuming Z is supported at the three double points (checked separately by the
kernel at the triple points) and m_P^K lies in J_P (the colength has stabilized below K), this
prints dim (I_Z)_l for l = 0..LMAX and alpha(Z).  The other double points (1:0:1), (0:1:1) are the
images of P under the coordinate transpositions (2 3) and (1 3), which preserve the problem.
Usage: bmd_cube_point_alpha.py ROWS_FILE LMAX p b1 b2 b3 es1 es2 es3 et1 et2 et3
"""
import itertools, sys
import numpy as np


def rank_mod(A, p):
    A = A.copy() % p
    r = 0
    rows, cols = A.shape
    for c in range(cols):
        nz = np.nonzero(A[r:, c])[0]
        if len(nz) == 0:
            continue
        piv = r + nz[0]
        A[[r, piv]] = A[[piv, r]]
        A[r] = A[r] * pow(int(A[r, c]), p - 2, p) % p
        others = np.nonzero(A[:, c])[0]
        others = others[others != r]
        if len(others):
            A[others] = (A[others] - np.outer(A[others, c], A[r])) % p
        r += 1
        if r == rows:
            break
    return r


def main():
    path, lmax, p = sys.argv[1], int(sys.argv[2]), int(sys.argv[3])
    b, es, et = [list(map(int, sys.argv[4 + 3 * i:7 + 3 * i])) for i in range(3)]
    lines = open(path).read().splitlines()
    K = int(lines[0].split('K=')[1].split(';')[0])
    cols = [tuple(map(int, x.split(','))) for x in lines[0].split(':', 1)[1].split()]
    R = np.array([list(map(int, l.split())) for l in lines[1:] if l.strip()], dtype=np.int64).reshape(-1, len(cols))
    # linear forms y_i = b_i + es_i s + et_i t as K x K coefficient arrays [a][b] for s^a t^b
    def lin(i):
        f = np.zeros((K, K), dtype=np.int64)
        f[0, 0] = b[i] % p
        if K > 1:
            f[1, 0] = es[i] % p
            f[0, 1] = et[i] % p
        return f

    def mul(x, y):
        z = np.zeros((K, K), dtype=np.int64)
        for a in range(K):
            for c in range(K - a):
                if x[a, c]:
                    z[a:, c:] = (z[a:, c:] + x[a, c] * y[:K - a, :K - c]) % p
        # truncate total degree >= K
        for a in range(K):
            z[a, K - a:] = 0
        return z

    ys = [lin(i) for i in range(3)]
    pows = [[None] * (lmax + 1) for _ in range(3)]
    for i in range(3):
        pows[i][0] = np.zeros((K, K), dtype=np.int64)
        pows[i][0][0, 0] = 1
        for j in range(1, lmax + 1):
            pows[i][j] = mul(pows[i][j - 1], ys[i])
    perms = [(0, 1, 2), (0, 2, 1), (2, 1, 0)]  # identity, (2 3), (1 3)
    print(f'rows file {path}: K={K}, {R.shape[0]} conditions per point')
    alpha = None
    for l in range(lmax + 1):
        monos = [e for e in itertools.product(range(l + 1), repeat=3) if sum(e) == l]
        blocks = []
        for sg in perms:
            J = np.zeros((len(cols), len(monos)), dtype=np.int64)
            for k, e in enumerate(monos):
                ee = [e[sg[i]] for i in range(3)]  # monomial of f o sigma
                jet = mul(mul(pows[0][ee[0]], pows[1][ee[1]]), pows[2][ee[2]])
                J[:, k] = [jet[a, c] for (a, c) in cols]
            blocks.append(R.dot(J) % p)
        C = np.concatenate(blocks, axis=0) % p
        dim = len(monos) - rank_mod(C, p)
        if dim and alpha is None:
            alpha = l
        print(f'l={l}: dim (I_Z)_l = {dim}', flush=True)
    print(f'alpha(Z) = {alpha}')


if __name__ == '__main__':
    main()
