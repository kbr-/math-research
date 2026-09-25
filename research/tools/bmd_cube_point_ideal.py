"""Explicit local ideal J_{Z,P} modulo m^K at a point, from the echelon rows of bmd_cube_point_scheme.

Statement computed.  For rho >= 2, lem:cube-threshold-zero-scheme makes J_{Z,P} = {W_m : W a local
solution at P} an ideal of finite colength, and lem:cube-point-scheme-lower-bound shows that the
truncated computation gives a space J_{N,K} containing (J_{Z,P} + m^K)/m^K for every N > K.  The
kernel writes echelon rows whose common kernel is J_{N,K}.  This script prints a basis of J_{N,K} in
reduced echelon form with respect to a graded order (lowest degree first), in the kernel's local
coordinates (s,t) or, with --coords, in the linear coordinates (u,v) = (s + c t, s + c' t) given by
two slopes.  Printed are the lowest-degree forms of the basis (the initial forms of J_{N,K} in the
graded order) and the full truncated elements.  When J_{N,K} has stabilized in N and K it equals
(J_{Z,P} + m^K)/m^K; otherwise it is only an upper bound for it.
Usage: bmd_cube_point_ideal.py ROWS_FILE p [--coords c c']
"""
import sys
import numpy as np


def nullspace_mod(A, p):
    """Basis of {x : A x = 0} over F_p, one vector per free column."""
    A = A.copy() % p
    rows, cols = A.shape
    piv, r = [], 0
    for c in range(cols):
        if r == rows:
            break
        nz = np.nonzero(A[r:, c])[0]
        if len(nz) == 0:
            continue
        k = r + nz[0]
        A[[r, k]] = A[[k, r]]
        A[r] = A[r] * pow(int(A[r, c]), p - 2, p) % p
        oth = np.nonzero(A[:, c])[0]
        oth = oth[oth != r]
        if len(oth):
            A[oth] = (A[oth] - np.outer(A[oth, c], A[r])) % p
        piv.append(c)
        r += 1
    free = [c for c in range(cols) if c not in set(piv)]
    basis = []
    for f in free:
        x = np.zeros(cols, dtype=np.int64)
        x[f] = 1
        for i, c in enumerate(piv):
            x[c] = (-A[i, f]) % p
        basis.append(x)
    return basis


def rref(B, p):
    B = B.copy() % p
    rows, cols = B.shape
    r = 0
    for c in range(cols):
        if r == rows:
            break
        nz = np.nonzero(B[r:, c])[0]
        if len(nz) == 0:
            continue
        k = r + nz[0]
        B[[r, k]] = B[[k, r]]
        B[r] = B[r] * pow(int(B[r, c]), p - 2, p) % p
        oth = np.nonzero(B[:, c])[0]
        oth = oth[oth != r]
        if len(oth):
            B[oth] = (B[oth] - np.outer(B[oth, c], B[r])) % p
        r += 1
    return B[:r]


def signed(x, p):
    x = int(x) % p
    return x - p if x > p // 2 else x


def fmt(vec, monos, p, names):
    terms = []
    for c, (a, b) in zip(vec, monos):
        c = signed(c, p)
        if c:
            mon = (f'{names[0]}^{a}' if a > 1 else names[0] if a == 1 else '') + \
                  (f'{names[1]}^{b}' if b > 1 else names[1] if b == 1 else '')
            terms.append(f'{c}{"*" + mon if mon else ""}')
    return ' + '.join(terms) if terms else '0'


def change(monos, p, c1, c2):
    """Matrix sending coefficients in (s,t) to coefficients in (u,v), u = s + c1 t, v = s + c2 t."""
    # s = (c2 u - c1 v)/(c2 - c1), t = (v - u)/(c2 - c1)
    inv = pow((c2 - c1) % p, p - 2, p)
    s_uv = {(1, 0): c2 * inv % p, (0, 1): (-c1) * inv % p}
    t_uv = {(1, 0): (-inv) % p, (0, 1): inv}
    pos = {m: i for i, m in enumerate(monos)}

    def mul(x, y):
        z = {}
        for (a, b), u in x.items():
            for (e, f), w in y.items():
                z[(a + e, b + f)] = (z.get((a + e, b + f), 0) + u * w) % p
        return z

    M = np.zeros((len(monos), len(monos)), dtype=np.int64)
    for j, (a, b) in enumerate(monos):
        poly = {(0, 0): 1}
        for _ in range(a):
            poly = mul(poly, s_uv)
        for _ in range(b):
            poly = mul(poly, t_uv)
        for m, c in poly.items():
            M[pos[m], j] = c
    return M


def main():
    path, p = sys.argv[1], int(sys.argv[2])
    coords = None
    if '--coords' in sys.argv:
        k = sys.argv.index('--coords')
        coords = (int(sys.argv[k + 1]), int(sys.argv[k + 2]))
    with open(path) as fh:
        head = fh.readline().split(':', 1)[1].split()
        monos = [tuple(map(int, x.split(','))) for x in head]
        rows = [list(map(int, line.split())) for line in fh if line.strip()]
    K = max(a + b for a, b in monos) + 1
    A = np.array(rows, dtype=np.int64).reshape(len(rows), len(monos)) if rows else np.zeros((0, len(monos)), dtype=np.int64)
    J = nullspace_mod(A, p)
    order = sorted(range(len(monos)), key=lambda i: (monos[i][0] + monos[i][1], monos[i][1]))
    graded = [monos[i] for i in order]
    names = ('s', 't')
    Bm = np.array([v[order] for v in J], dtype=np.int64) if J else np.zeros((0, len(monos)), dtype=np.int64)
    if coords is not None:
        M = change(graded, p, *coords)
        Bm = (Bm @ M.T) % p
        names = ('u', 'v')
    R = rref(Bm, p) if len(Bm) else Bm
    print(f'# K={K}, dim J mod m^K = {len(R)}, colength = {len(monos) - len(R)}; coordinates {names}'
          + (f' with u = s + {coords[0]} t, v = s + {coords[1]} t' if coords else ''))
    for vec in R:
        lead = next(i for i, x in enumerate(vec) if x % p)
        deg = sum(graded[lead])
        low = [x if sum(graded[i]) == deg else 0 for i, x in enumerate(vec)]
        print(f'deg {deg}: lowest form {fmt(low, graded, p, names)} | element {fmt(vec, graded, p, names)}')


if __name__ == '__main__':
    main()
