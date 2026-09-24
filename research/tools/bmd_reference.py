"""Brute-force reference for bmd_min_degree on tiny cases (validation only, seconds).

Enumerates every F_2 polynomial of total degree <= dcap in n variables, computes Hasse
multiplicities directly from P(a+z) expanded with exact binomials, and returns the least degree for
each origin order l < k among polynomials with multiplicity >= k at all nonzero points.
Usage: bmd_reference.py n k dcap
"""
import itertools, math, sys


def monomials(n, d):
    return [m for m in itertools.product(range(d + 1), repeat=n) if sum(m) <= d]


def mult(P, a, n, cap):
    """Least |beta| with nonzero coefficient of z^beta in P(a+z), capped at cap."""
    for t in range(cap):
        for beta in monomials(n, t):
            if sum(beta) != t:
                continue
            c = 0
            for al in P:
                if all(b <= x for b, x in zip(beta, al)):
                    term = 1
                    for i in range(n):
                        term *= math.comb(al[i], beta[i]) * (a[i] ** (al[i] - beta[i]))
                    c ^= term & 1
            if c:
                return t
    return cap


def main():
    n, k, dcap = map(int, sys.argv[1:4])
    mons = monomials(n, dcap)
    assert len(mons) <= 20, 'reference enumeration only for tiny cases'
    best = {}
    pts = [p for p in itertools.product((0, 1), repeat=n) if any(p)]
    for mask in range(1, 1 << len(mons)):
        P = [mons[i] for i in range(len(mons)) if mask >> i & 1]
        d = max(sum(m) for m in P)
        l = mult(P, (0,) * n, n, k)
        if l >= k or best.get(l, 99) <= d:
            continue
        if all(mult(P, a, n, k) >= k for a in pts):
            best[l] = d
    print({l: best.get(l) for l in range(k)})


if __name__ == '__main__':
    main()
