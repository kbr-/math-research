"""Rewrite symmetric F_2 polynomials from the monomial basis m_lambda into the elementary basis e_mu.

e_mu = sum_lambda M(mu, lambda) m_lambda, where M counts 0-1 matrices with row sums mu and column
sums lambda; over F_2 only its parity matters.  The transition is unitriangular in dominance order,
so the e-expansion is solved by back substitution.  Sizes are tiny (partitions of <= 11).
Usage: bmd_ebasis.py QJSON K [K ...]
"""
import functools, json, sys


def partitions(total, maxpart=None):
    if maxpart is None:
        maxpart = total
    if total == 0:
        yield ()
        return
    for p in range(min(total, maxpart), 0, -1):
        for rest in partitions(total - p, p):
            yield (p,) + rest


@functools.lru_cache(maxsize=None)
def matrices(mu, lam):
    """Parity of 0-1 matrices with row sums mu and column sums lam (columns filled one row at a time)."""
    if not mu:
        return 1 if not any(lam) else 0
    r, rest = mu[0], mu[1:]
    total = 0
    cols = len(lam)
    # choose which columns get a 1 in this row: subsets of size r among columns with remaining sum > 0
    def choose(i, need, cur):
        nonlocal total
        if need == 0:
            total += matrices(rest, tuple(sorted(cur, reverse=True)))
            return
        if i == cols or cols - i < need:
            return
        if cur[i] > 0:
            nxt = list(cur); nxt[i] -= 1
            choose(i + 1, need - 1, nxt)
        choose(i + 1, need, cur)
    choose(0, r, list(lam))
    return total & 1


def to_ebasis(Q):
    """Q: set of partitions (m-basis, coefficients 1). Returns set of mu with Q = sum e_mu."""
    Q = {tuple(l) for l in Q}
    out = set()
    while Q:
        d = max(sum(l) for l in Q)
        # leading term in reverse-lexicographic order among top degree: e_{lam'} has leading m_lam
        lam = max(l for l in Q if sum(l) == d)
        mu = tuple(sum(1 for p in lam if p > i) for i in range(lam[0])) if lam else ()   # conjugate
        out ^= {mu}
        for s in range(d + 1):
            for l in partitions(s):
                if s == d and matrices(mu, l):
                    Q ^= {l}
        Q = {l for l in Q}
    return out


def main():
    data = {r['k']: r for r in json.load(open(sys.argv[1]))}
    for k in map(int, sys.argv[2:]):
        E = to_ebasis(data[k]['Q'])
        print(k, sorted(E, key=lambda m: (sum(m), m)))


if __name__ == '__main__':
    main()
