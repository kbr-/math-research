"""One-row local spanning in degree 4 over F_3 (27 September 2026): exact checks of the finite ingredients.

Z_d(Y) = functions on d-subsets of Y whose sums over the supersets of every (d-1)-subset vanish (the dual of the
one-row quotient F_3[y]/(y_c^2, sum y_c) in degree d). The argument: Z_4(N) = Specht part (all marginals zero,
spanned by products of four 2-column differences) plus a layer seen by 1-set marginals, which products
(e_a - e_b) (x) h with h in Z_3(Y) of nonzero total generate. Checked: dim Z_4(8) = 21; polytabloids span 14; the
smallest |Y| with some h in Z_3(Y) of nonzero total; local products span Z_4(8); dim Z_4(7) = 6 with injective
1-marginals. Matrices have at most a few hundred rows of length 70; plain Python elimination mod 3.
Usage: one_row_spanning.py
"""
from itertools import combinations

P = 3


def rank(rows):
    rows = [list(r) for r in rows]
    rk, col, n = 0, 0, len(rows[0]) if rows else 0
    while rk < len(rows) and col < n:
        piv = next((i for i in range(rk, len(rows)) if rows[i][col] % P), None)
        if piv is None:
            col += 1
            continue
        rows[rk], rows[piv] = rows[piv], rows[rk]
        inv = 1 if rows[rk][col] % P == 1 else 2
        rows[rk] = [(x * inv) % P for x in rows[rk]]
        for i in range(len(rows)):
            if i != rk and rows[i][col] % P:
                f = rows[i][col]
                rows[i] = [(a - f * b) % P for a, b in zip(rows[i], rows[rk])]
        rk += 1
        col += 1
    return rk


def nullspace(cond, n):
    """Basis of {x in F_3^n : cond x = 0}."""
    m = [list(r) for r in cond]
    pivots, r = [], 0
    for c in range(n):
        piv = next((i for i in range(r, len(m)) if m[i][c] % P), None)
        if piv is None:
            continue
        m[r], m[piv] = m[piv], m[r]
        inv = 1 if m[r][c] == 1 else 2
        m[r] = [(x * inv) % P for x in m[r]]
        for i in range(len(m)):
            if i != r and m[i][c]:
                f = m[i][c]
                m[i] = [(a - f * b) % P for a, b in zip(m[i], m[r])]
        pivots.append(c)
        r += 1
    free = [c for c in range(n) if c not in pivots]
    basis = []
    for fc in free:
        v = [0] * n
        v[fc] = 1
        for i, pc in enumerate(pivots):
            v[pc] = (-m[i][fc]) % P
        basis.append(v)
    return basis


def zero_marginal(Y, d):
    sets = list(combinations(Y, d))
    cond = [[1 if set(T) <= set(S) else 0 for S in sets] for T in combinations(Y, d - 1)]
    return sets, nullspace(cond, len(sets))


def main():
    N = 8
    cols = list(range(N))
    sets4, Z4 = zero_marginal(cols, 4)
    index = {S: i for i, S in enumerate(sets4)}
    print('dim Z_4(8) =', len(Z4))
    # polytabloids: products of four disjoint differences (e_a - e_b)
    poly = []
    for pairs in combinations(list(combinations(cols, 2)), 4):
        if len({c for p in pairs for c in p}) < 8:
            continue
        v = [0] * len(sets4)
        for choice in range(16):
            S = tuple(sorted(p[(choice >> k) & 1] for k, p in enumerate(pairs)))
            v[index[S]] = (v[index[S]] + (-1) ** bin(choice).count('1')) % P
        poly.append(v)
    print('polytabloid span =', rank(poly))
    # smallest block Y carrying h in Z_3(Y) with nonzero total
    for y in range(3, 8):
        sets3, Z3 = zero_marginal(list(range(y)), 3)
        totals = [sum(h) % P for h in Z3]
        print(f'|Y|={y}: dim Z_3 = {len(Z3)}, some h with nonzero total: {any(totals)}')
    # local products (e_a - e_b) (x) h, h in Z_3(Y), Y the smallest such block, disjoint from {a, b}
    y0 = next(y for y in range(3, 7) if any(sum(h) % P for h in zero_marginal(list(range(y)), 3)[1]))
    products = []
    for a, b in combinations(cols, 2):
        rest = [c for c in cols if c not in (a, b)]
        for Y in combinations(rest, y0):
            sets3, Z3 = zero_marginal(list(Y), 3)
            for h in Z3:
                v = [0] * len(sets4)
                for T, val in zip(sets3, h):
                    for c, sign in ((a, 1), (b, -1)):
                        S = tuple(sorted(T + (c,)))
                        v[index[S]] = (v[index[S]] + sign * val) % P
                products.append(v)
    print(f'polytabloids plus products with blocks of size {y0}: span =', rank(poly + products))
    sets7, Z47 = zero_marginal(list(range(7)), 4)
    marg = [[sum(val for S, val in zip(sets7, f) if c in S) % P for c in range(7)] for f in Z47]
    print('dim Z_4(7) =', len(Z47), ' rank of its 1-marginals =', rank(marg))


if __name__ == '__main__':
    main()
