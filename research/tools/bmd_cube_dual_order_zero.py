"""Least m for which the dual order-zero problem has a solution, for a family of test spaces.

Statement tested.  By lem:cube-dual-polynomial-form (at l = 0), savings >= h = d+1 at (k, 0) on
{0,1}^n with k = m+1 hold iff some polynomial Phi(u_1..u_n) with Phi(0) = 1 and deg Phi <= m has
[Phi * prod_{a_i=1} r_0(u_i)]_{m-Q} = 0 for every test element T^Q z^a of V_{n,d}
(2Q + |a| <= d).  A restriction to the collision divisor y_1 = 0 (collision lifts) turns an l = 0
solution for V_{3,d} into one in two variables for U_d = span{T^Q z^a : Q + |a| <= d}.  This script
finds, for each d, the least m with a solution for either test family, so that the two
thresholds can be compared (the V_{3,d} threshold should be 5d - 1).

Mode "V n": test space V_{n,d}; mode "U n": test space {T^Q z^a : Q + |a| <= d}.  Linear algebra
over F_p (p large) with numpy; Phi_0 = 1 is the inhomogeneous part.
Usage: bmd_cube_dual_order_zero.py MODE n DMAX MMAX p
       bmd_cube_dual_order_zero.py LOWEST n d m l p   (test space V_{n,d}: the space of possible
       lowest parts Phi_l of dual solutions at order l, i.e. the degree-l part of the threshold ideal
       I^{(d+1)}_m, printed as a basis of polynomials)
"""
import itertools, sys
import numpy as np


def rank_mod(A, p):
    A = A.copy() % p
    r = 0
    rows, cols = A.shape
    for c in range(cols):
        piv = None
        for i in range(r, rows):
            if A[i, c]:
                piv = i
                break
        if piv is None:
            continue
        A[[r, piv]] = A[[piv, r]]
        A[r] = A[r] * pow(int(A[r, c]), p - 2, p) % p
        nz = np.nonzero(A[:, c])[0]
        nz = nz[nz != r]
        if len(nz):
            A[nz] = (A[nz] - np.outer(A[nz, c], A[r])) % p
        r += 1
        if r == rows:
            break
    return r


def solvable(mode, n, d, m, p, kappa):
    # monomials of total degree <= m in n variables
    monos = [e for tot in range(m + 1) for e in itertools.product(range(tot + 1), repeat=n) if sum(e) == tot]
    idx = {e: i for i, e in enumerate(monos)}
    tests = []
    for a in itertools.product([0, 1], repeat=n):
        for Q in range(d + 1):
            ok = (2 * Q + sum(a) <= d) if mode == 'V' else (Q + sum(a) <= d)
            if ok:
                tests.append((Q, a))
    rows = []
    for Q, a in tests:
        target = m - Q
        if target < 0:
            continue
        # coefficient of monomial x in Phi * z^a, for |x| = target: sum over mu <= x of Phi_mu * coef_{z^a}(x - mu)
        for x in (e for e in monos if sum(e) == target):
            row = np.zeros(len(monos), dtype=np.int64)
            for mu in itertools.product(*[range(xi + 1) for xi in x]):
                diff = tuple(xi - mi for xi, mi in zip(x, mu))
                c = 1
                for i in range(n):
                    if a[i]:
                        c = c * (kappa[diff[i]] if diff[i] >= 1 else 0) % p
                    elif diff[i]:
                        c = 0
                if c:
                    row[idx[mu]] = (row[idx[mu]] + c) % p
            rows.append(row)
    if not rows:
        return True
    A = np.array(rows, dtype=np.int64)
    # unknown Phi_mu for mu != 0; Phi_0 = 1 moves to the right-hand side
    M = A[:, 1:]
    b = (-A[:, 0]) % p
    return rank_mod(M, p) == rank_mod(np.column_stack([M, b]), p)


def nullspace_mod(A, p):
    """Basis of the right kernel of A over F_p (rows of the returned array)."""
    A = A.copy() % p
    rows, cols = A.shape
    piv_cols, r = [], 0
    for c in range(cols):
        piv = None
        for i in range(r, rows):
            if A[i, c]:
                piv = i
                break
        if piv is None:
            continue
        A[[r, piv]] = A[[piv, r]]
        A[r] = A[r] * pow(int(A[r, c]), p - 2, p) % p
        nz = np.nonzero(A[:, c])[0]
        nz = nz[nz != r]
        if len(nz):
            A[nz] = (A[nz] - np.outer(A[nz, c], A[r])) % p
        piv_cols.append(c)
        r += 1
        if r == rows:
            break
    free = [c for c in range(cols) if c not in set(piv_cols)]
    basis = []
    for f in free:
        v = np.zeros(cols, dtype=np.int64)
        v[f] = 1
        for i, c in enumerate(piv_cols):
            v[c] = (-A[i, f]) % p
        basis.append(v)
    return np.array(basis, dtype=np.int64).reshape(len(basis), cols)


def lowest_parts(n, d, m, l, p, kappa):
    monos = [e for tot in range(l, l + m + 1) for e in itertools.product(range(tot + 1), repeat=n) if sum(e) == tot]
    idx = {e: i for i, e in enumerate(monos)}
    rows = []
    for a in itertools.product([0, 1], repeat=n):
        for Q in range(d + 1):
            if 2 * Q + sum(a) > d:
                continue
            target = l + m - Q
            for x in itertools.product(range(target + 1), repeat=n):
                if sum(x) != target:
                    continue
                row = np.zeros(len(monos), dtype=np.int64)
                for mu in itertools.product(*[range(xi + 1) for xi in x]):
                    if mu not in idx:
                        continue
                    diff = tuple(xi - mi for xi, mi in zip(x, mu))
                    c = 1
                    for i in range(n):
                        if a[i]:
                            c = c * (kappa[diff[i]] if diff[i] >= 1 else 0) % p
                        elif diff[i]:
                            c = 0
                    if c:
                        row[idx[mu]] = (row[idx[mu]] + c) % p
                rows.append(row)
    K = nullspace_mod(np.array(rows, dtype=np.int64), p)
    low = [i for i, e in enumerate(monos) if sum(e) == l]
    P = K[:, low] % p
    r = rank_mod(P, p) if len(P) else 0
    # reduced basis of the projected space
    B = nullspace_mod(nullspace_mod(P, p), p) if r else np.zeros((0, len(low)), dtype=np.int64)
    names = [monos[i] for i in low]
    return r, B, names


def main():
    if sys.argv[1] == 'LOWEST':
        n, d, m, l, p = map(int, sys.argv[2:7])
        cat = [1]
        for j in range(1, l + m + 2):
            cat.append(cat[-1] * 2 * (2 * j - 1) // (j + 1))
        kappa = [0] + [((-1) ** j * cat[j - 1]) % p for j in range(1, l + m + 2)]
        r, B, names = lowest_parts(n, d, m, l, p, kappa)
        print(f'n={n} d={d} m={m} l={l}: dimension of the degree-l part of I = {r}')
        for v in B:
            terms = [f'{(int(c) if c <= p // 2 else int(c) - p)}*u^{e}' for c, e in zip(v, names) if c]
            print('  ' + ' + '.join(terms))
        return
    mode, n, dmax, mmax, p = sys.argv[1], int(sys.argv[2]), int(sys.argv[3]), int(sys.argv[4]), int(sys.argv[5])
    cat = [1]
    for j in range(1, mmax + 2):
        cat.append(cat[-1] * 2 * (2 * j - 1) // (j + 1))
    kappa = [0] + [((-1) ** j * cat[j - 1]) % p for j in range(1, mmax + 2)]
    for d in range(1, dmax + 1):
        mstar = next((m for m in range(mmax + 1) if solvable(mode, n, d, m, p, kappa)), None)
        print(f'mode={mode} n={n} d={d}: least m with an order-zero dual solution = {mstar}', flush=True)


if __name__ == '__main__':
    main()
