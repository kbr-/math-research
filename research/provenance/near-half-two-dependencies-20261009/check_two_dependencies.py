#!/usr/bin/env python3
"""Direct check of the two-dependency series (prop:two-dependency-series-exactness) for small M.

Statement checked: Q = tensor product over i = 1..M of span{1, u_i, v_i} with u_i^2 = v_i^2 = u_i v_i = 0
over F_2, graded by the number of non-unit factors; omega = (sum u_i)(sum v_i) = sum_{i != j} u_i v_j.
For each degree j the rank of multiplication by omega from Q_{j-2} to Q_j equals the coefficient of
z^(j-2) in F_M(z) = ((1+2z)^M - M z^(M-1) - (M+1) z^M)/(1+z)^2.  Also checked: the kernel of omega on
Q_{j-2} has the dimension of ((lambda, mu) Q)_{j-2} wherever the quotient series is the product
series, by computing the rank of [lambda, mu] into Q_{j-2}.
Monomials are tuples in {0,1,2}^M (0 unit, 1 = u, 2 = v); vectors are Python integers (bit sets).
Argument: largest M.  Small sizes only (3^M monomials).
"""
import itertools
import sys


def rank(vectors):
    basis = {}
    for vec in vectors:
        while vec:
            p = vec.bit_length() - 1
            if p not in basis:
                basis[p] = vec
                break
            vec ^= basis[p]
    return len(basis)


def series(M):
    # coefficients of ((1+2z)^M - M z^(M-1) - (M+1) z^M) / (1+z)^2
    from math import comb
    num = [comb(M, j) * 2 ** j for j in range(M + 1)]
    if M >= 1:
        num[M - 1] -= M
    num[M] -= M + 1
    out = []
    for _ in range(2):
        q, carry = [], 0
        for c in num:
            carry = c - carry
            q.append(carry)
        assert q[-1] == 0, 'not divisible by 1+z'
        num = q[:-1]
    return num


bad = 0
for M in range(1, int(sys.argv[1]) + 1):
    monos = list(itertools.product((0, 1, 2), repeat=M))
    index = {m: i for i, m in enumerate(monos)}
    by_deg = {}
    for m in monos:
        by_deg.setdefault(sum(1 for x in m if x), []).append(m)

    def insert(m, letters):
        """Sum over placements of the given letters into distinct unit slots, as a bit set."""
        out = 0
        slots = [i for i, x in enumerate(m) if x == 0]
        for pos in itertools.permutations(slots, len(letters)):
            new = list(m)
            for p, letter in zip(pos, letters):
                new[p] = letter
            out ^= 1 << index[tuple(new)]
        return out

    F = series(M)
    line = []
    for j in range(2, M + 1):
        r = rank([insert(m, (1, 2)) for m in by_deg.get(j - 2, [])])
        want = F[j - 2] if j - 2 < len(F) else 0
        line.append((j, r, want))
        bad += r != want
    # kernel of omega on Q_d against (lambda, mu) Q in degree d
    kern = []
    for d in range(0, M - 1):
        src = by_deg.get(d, [])
        r = rank([insert(m, (1, 2)) for m in src])
        lm = rank([insert(m, (1,)) for m in by_deg.get(d - 1, [])] + [insert(m, (2,)) for m in by_deg.get(d - 1, [])]) if d >= 1 else 0
        kern.append((d, len(src) - r, lm))
    print('M', M, 'F', F, 'rank omega by target degree (j, rank, predicted):', line,
          'kernel vs (lambda,mu)Q by source degree (d, ker, dim):', kern)
print('mismatches', bad)
sys.exit(1 if bad else 0)
