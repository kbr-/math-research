"""3-torsion in the degree-d lattice of weak unary PHP (route review, odd-prime thread, 26 Sept 2026).

Tested statement (the 3-integrality lead): a Q-valued dual functional that vanishes on the Q-span of the
degree-<=d axiom multiples, takes 3-integral values and has l(1) = 1 reduces mod 3 to an F_3 dual functional.
Such functionals exist whenever F_3 hardness holds, unless the quotient Z^N / L_d has 3-torsion, where
L_d = Z-span of the multilinearized products m*a, deg(m*a) <= d, for the weak-base axioms a:
row equations sum_j x_ij - 1, column collisions x_ij x_i'j (Booleanity is built into multilinear monomials).
Quantity: rank of the generator matrix of L_d over F_p for p in PRIMES. Z^N / L_d has p-torsion iff
rank_p < rank_Q; rank_Q is estimated as the maximum over the primes (a lower bound, equal to it unless every
listed prime is exceptional). Also recorded: whether 1 lies in the F_p span (NS refutation at degree d).
Ranks by research/tools/rank_modp.py.
Usage: php_lattice_torsion.py --cases 2:2,2:3,3:2,3:3,3:4,4:2,4:3,5:3 --out FILE   (case n:d, pigeons n+1)"""
import argparse, itertools, json, os, sys, time
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..', 'tools'))
from rank_modp import rank_mod_p

PRIMES = [2, 3, 5, 7, 11, 13, 37]


def monomials(nv, d):
    return [frozenset(c) for j in range(d + 1) for c in itertools.combinations(range(nv), j)]


def mul(poly, mono):  # poly: dict frozenset->int ; multilinear product with a monomial
    out = {}
    for m, c in poly.items():
        k = m | mono
        out[k] = out.get(k, 0) + c
    return out


def lattice_rows(n, d):
    m_p, nv = n + 1, (n + 1) * n
    var = lambda i, j: i * n + j
    axioms = [{**{frozenset([var(i, j)]): 1 for j in range(n)}, frozenset(): -1} for i in range(m_p)]
    pairs = itertools.product(range(n), itertools.combinations(range(m_p), 2))
    axioms += [{frozenset([var(i, j), var(k, j)]): 1} for j, (i, k) in pairs]
    rows = []
    for a in axioms:
        da = max(len(m) for m in a)
        rows.extend(mul(a, mono) for mono in monomials(nv, d - da))
    rows = [r for r in rows if max(len(m) for m in r) <= d]
    return rows, monomials(nv, d)


def to_sparse(rows, idx):
    return [[(idx[m], c) for m, c in r.items()] for r in rows]


def reduce_mod(sparse, p):
    return [[(j, c % p) for j, c in r if c % p] for r in sparse]


def main():
    ap = argparse.ArgumentParser(); ap.add_argument('--cases', required=True); ap.add_argument('--out', required=True)
    a = ap.parse_args()
    out = []
    for case in a.cases.split(','):
        n, d = map(int, case.split(':'))
        t0 = time.time()
        rows, cols = lattice_rows(n, d)
        idx = {m: i for i, m in enumerate(cols)}
        sparse = to_sparse(rows, idx)
        one = idx[frozenset()]
        res = dict(n=n, pigeons=n + 1, d=d, rows=len(rows), cols=len(cols), ranks={}, one_in_span={})
        for p in PRIMES:
            rp = reduce_mod(sparse, p)
            rk = rank_mod_p(rp, len(cols), p)
            rk1 = rank_mod_p(rp + [[(one, 1)]], len(cols), p)
            res['ranks'][p] = rk; res['one_in_span'][p] = (rk1 == rk)
        rq = max(res['ranks'].values())
        res['rank_Q_estimate'] = rq
        res['torsion_primes'] = [p for p in PRIMES if res['ranks'][p] < rq]
        res['seconds'] = round(time.time() - t0, 1)
        out.append(res); print(json.dumps(res), flush=True)
        with open(a.out, 'w') as fh:
            json.dump(out, fh, indent=1)


if __name__ == '__main__':
    main()
