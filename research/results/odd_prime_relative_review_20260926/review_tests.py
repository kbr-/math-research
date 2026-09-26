#!/usr/bin/env python3
"""Cheap tests for the relative-criterion route review (26 September 2026).

1. Zero-sum transversals: can one matching make the restricted constants of every block's chosen
   form zero? Each condition cuts the permutations by about a factor 3 (swap decay), so at most
   log_3(N!) independent conditions can hold at once. Compare log_3(n!) with n^K for n = 10^3..10^6.
2. Greedy versus random hitting prefixes: for a block of h random affine forms over F_3 on the
   functional states of b pigeons with 5 states each (all 5^b state tuples; injectivity ignored),
   compute the zero sets Z(sigma) and the greedy hitting-set size (repeatedly take the form
   vanishing on most unhit states). Compare with the random-prefix union bound
   k > b ln 5 / ln(3/2) (every nonempty zero set has about h/3 elements).
Usage: review_tests.py --out PATH [--seed S]
"""
import argparse, itertools, json, math
import numpy as np


def greedy_hitting(Z):
    # Z: boolean matrix states x forms, rows with at least one True
    alive = Z.any(axis=1)
    Z = Z[alive]
    chosen = []
    unhit = np.ones(Z.shape[0], dtype=bool)
    while unhit.any():
        j = int(Z[unhit].sum(axis=0).argmax())
        chosen.append(j)
        unhit &= ~Z[:, j]
    return len(chosen)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--out', required=True)
    ap.add_argument('--seed', type=int, default=20260926)
    a = ap.parse_args()
    rng = np.random.default_rng(a.seed)
    res = {'transversal': [], 'hitting': []}
    for n in (10**3, 10**4, 10**5, 10**6):
        l3 = math.lgamma(n + 1) / math.log(3)
        res['transversal'].append({'n': n, 'log3_n_factorial': round(l3), 'n^2': n**2, 'n^3': n**3})
    for b in (3, 4, 5, 6):
        h = 300
        states = np.array(list(itertools.product(range(5), repeat=b)))  # 5^b x b
        coef = rng.integers(0, 3, size=(h, b, 5))
        const = rng.integers(0, 3, size=h)
        vals = (coef[:, np.arange(b)[None, :], states].sum(axis=2).T + const[None, :]) % 3  # states x h
        Z = vals == 0
        g = greedy_hitting(Z)
        bound = b * math.log(5) / math.log(1.5)
        res['hitting'].append({'b': b, 'forms': h, 'states': int(states.shape[0]),
                               'greedy_size': g, 'union_bound_k': round(bound, 1),
                               'min_zero_fraction': round(float(Z.sum(axis=1)[Z.any(axis=1)].min() / h), 3)})
    json.dump(res, open(a.out, 'w'), indent=1)
    print(json.dumps(res))


if __name__ == '__main__':
    main()
