#!/usr/bin/env python3
"""Sanity check of the three-family odd cover over F_2 (side notebook near-half-pc-degree,
entry-2026-10-09-three-family-cover).

Statement checked on instances: let n = 4s, Omega_1, Omega_2 nondegenerate alternating forms on F_2^n with
Omega_3 = Omega_1 + Omega_2 nondegenerate, and B_j a symplectic basis of Omega_j (pairs (l_i, m_i) of linear
forms with Omega_j = sum l_i ^ m_i).  Then there are points p_1, p_2, p_3 with
    sum_j sum_i (l_i(z) + l_i(p_j)) (m_i(z) + m_i(p_j)) = 1   for every z in F_2^n,
i.e. the 3n/2 planes {l_i = l_i(p_j) + 1, m_i = m_i(p_j) + 1} cover every point an odd number of times.
The script builds random symplectic bases, searches p_1, p_2 at random as the proof prescribes, solves for p_3,
asserts the hypotheses, and verifies the identity at every point; it also reports the largest r such that every
r planes have independent forms (exhaustively for n <= 8).  Vectors are Python ints (bit masks).
"""
import itertools
import json
import random
import sys


def rank(vectors):
    basis = []
    for v in vectors:
        for b in basis:
            v = min(v, v ^ b)
        if v:
            basis.append(v)
    return len(basis)


def omega_matrix(n, pairs):
    """Alternating matrix (list of row masks) of sum l ^ m over the pairs of linear forms."""
    rows = [0] * n
    for l, m in pairs:
        for a in range(n):
            for b in range(n):
                if (l >> a & 1) and (m >> b & 1) and a != b:
                    rows[a] ^= 1 << b
                    rows[b] ^= 1 << a
    return rows


def inverse(n, rows):
    """Inverse over F_2 of the n x n matrix with row masks `rows`."""
    aug = [rows[a] | (1 << (n + a)) for a in range(n)]
    for c in range(n):
        piv = next(a for a in range(c, n) if aug[a] >> c & 1)
        aug[c], aug[piv] = aug[piv], aug[c]
        for a in range(n):
            if a != c and aug[a] >> c & 1:
                aug[a] ^= aug[c]
    return [r >> n for r in aug]


def symplectic_basis(n, omega, rng):
    """Random pairs (l, m) of linear forms on F_2^n with sum (l m^T + m l^T) = omega (nondegenerate):
    a symplectic basis of the dual space for the dual form, whose matrix is the inverse of omega."""
    dual = inverse(n, omega)

    def form(u, v):
        acc = 0
        for a in range(n):
            if u >> a & 1:
                acc ^= dual[a]
        return bin(acc & v).count('1') & 1
    pairs = []
    live = [1 << a for a in range(n)]          # a basis of the orthogonal complement of the pairs so far
    while live:
        span = [0]
        for b in live:
            span += [x ^ b for x in span]
        l = rng.choice(span[1:])
        m = rng.choice([v for v in span[1:] if form(l, v)])
        pairs.append((l, m))
        basis = []
        for v in span[1:]:
            if form(l, v) or form(m, v):
                continue
            w = v
            for b in basis:
                w = min(w, w ^ b)
            if w:
                basis.append(w)
        live = basis
    return pairs


def instance(s, rng):
    n = 4 * s
    # block-diagonal forms on V: Omega_1 = e1^e2 + e3^e4, Omega_2 = e1^e2 + e1^e3 + e2^e4 per block
    def blocks(local):
        rows = [0] * n
        for t in range(s):
            for a, b in local:
                rows[4 * t + a] ^= 1 << (4 * t + b)
                rows[4 * t + b] ^= 1 << (4 * t + a)
        return rows
    o1 = blocks([(0, 1), (2, 3)])
    o2 = blocks([(0, 1), (0, 2), (1, 3)])
    o3 = [a ^ b for a, b in zip(o1, o2)]
    assert rank(o1) == rank(o2) == rank(o3) == n
    fam = [symplectic_basis(n, o, rng) for o in (o1, o2, o3)]
    for o, pairs in zip((o1, o2, o3), fam):
        assert omega_matrix(n, pairs) == o and rank([f for p in pairs for f in p]) == n

    def ev(form, z):
        return bin(form & z).count('1') & 1

    def q(pairs, z, p):
        return sum((ev(l, z) ^ ev(l, p)) & (ev(m, z) ^ ev(m, p)) for l, m in pairs) & 1
    points = range(1 << n)
    for _ in range(200):
        p1, p2 = rng.randrange(1 << n), rng.randrange(1 << n)
        target = [q(fam[0], z, p1) ^ q(fam[1], z, p2) ^ 1 for z in points]
        for p3 in points:
            if all(q(fam[2], z, p3) == target[z] for z in (0, 1, 2, 4, 8, 3, 5)) and \
               all(q(fam[2], z, p3) == target[z] for z in points):
                planes = [(l, m, ev(l, p) ^ 1, ev(m, p) ^ 1) for pairs, p in zip(fam, (p1, p2, p3)) for l, m in pairs]
                odd = all(sum(1 for l, m, a, b in planes if ev(l, z) == a and ev(m, z) == b) & 1 for z in points)
                r = 0
                for size in range(1, len(planes) + 1):
                    if all(rank([f for i in c for f in planes[i][:2]]) == 2 * size
                           for c in itertools.combinations(range(len(planes)), size)):
                        r = size
                    else:
                        break
                return {'n': n, 'planes': len(planes), 'identity_holds': odd, 'independent_through': r}
    return {'n': n, 'failed': True}


if __name__ == '__main__':
    rng = random.Random(int(sys.argv[1]))
    for s in (1, 2):
        for trial in range(int(sys.argv[2])):
            print(json.dumps(instance(s, rng)))
