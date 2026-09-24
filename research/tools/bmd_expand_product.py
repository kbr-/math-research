"""Expand P = prod_i (1+x_i) * Q over F_2 in n variables, Q given as monomial symmetric functions.

Writes one monomial per line (n exponents) for `bmd_min_degree verify`.  Expansion is small for the
verified sizes (n <= 7); this is orchestration, and the multiplicity check runs in the C++ kernel.
Usage: bmd_expand_product.py QJSON K N OUT
"""
import itertools, json, sys
from collections import Counter


def m_lambda(lam, n):
    """Distinct exponent vectors in the orbit of lam padded with zeros to length n."""
    if len(lam) > n:
        return []
    return set(itertools.permutations(list(lam) + [0] * (n - len(lam))))


def main():
    qfile, k, n, out = sys.argv[1], int(sys.argv[2]), int(sys.argv[3]), sys.argv[4]
    rec = next(r for r in json.load(open(qfile)) if r['k'] == k)
    Q = Counter()
    for lam in rec['Q']:
        for a in m_lambda(tuple(lam), n):
            Q[a] ^= 1
    P = Counter()
    for sub in itertools.product((0, 1), repeat=n):          # monomials of prod(1+x_i)
        for a, c in Q.items():
            if c:
                P[tuple(x + y for x, y in zip(a, sub))] ^= 1
    with open(out, 'w') as f:
        for a, c in P.items():
            if c:
                f.write(' '.join(map(str, a)) + '\n')
    print(f'k={k} n={n}: |Q|={sum(Q.values())} |P|={sum(P.values())}')


if __name__ == '__main__':
    main()
