#!/usr/bin/env python3
"""Two cheap tests for the closure route review (26 September 2026).

1. Mean-field blocking: a pigeon r of degree d on a random board is predicted to be a blocked
   centre with probability about P(every hole of r has enough other pigeons). Random control
   (pigeon degree 4 over 120 holes, 121 pigeons): (1 - e^{-lam})^4 with lam = 120*4/120.
   Twin board (base degree 2 over 60 holes): each of r's two base holes needs >= 2 other
   pigeons, (1 - e^{-lam}(1 + lam))^2 with lam = 120*2/60. Compared with blocked_count.json.
2. Burning closure versus Mikša-Nordström support: for a term t (a partial matching), the
   s-support Sup_s(t) is the union of pigeon sets U' with |U'| <= s whose boundary (holes with
   exactly one neighbour in U') lies in N(t) = union of the holes of the pigeons of t
   (Definitions 3.16-3.17 with the variable sets (4.3) of Theorem 4.9). Greedy burning adds a
   pigeon while all its holes lie in the burnt set, starting from N(t). Reports how often the
   two differ on small random boards (exact enumeration of U').
Usage: closure_tests.py --out PATH [--seed S]
"""
import argparse, itertools, json, math
import numpy as np


def support(nbrs, T, s):
    Nt = set().union(*(nbrs[p] for p in T))
    sup = set()
    P = len(nbrs)
    for size in range(1, s + 1):
        for U in itertools.combinations(range(P), size):
            cnt = {}
            for p in U:
                for h in nbrs[p]:
                    cnt[h] = cnt.get(h, 0) + 1
            if all(h in Nt for h, c in cnt.items() if c == 1):
                sup.update(U)
    return sup


def burning(nbrs, T):
    burnt = set().union(*(nbrs[p] for p in T))
    cl = set()
    changed = True
    while changed:
        changed = False
        for p, N in enumerate(nbrs):
            if p not in cl and N <= burnt:
                cl.add(p); changed = True
    return cl


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--out', required=True)
    ap.add_argument('--seed', type=int, default=20260926)
    a = ap.parse_args()
    bc = json.load(open('research/results/odd_prime_twin_boards_20260926/blocked_count.json'))['boards']
    lam_r = 120 * 4 / 120
    lam_t = 120 * 2 / 60
    pred = {'random_control': 121 * (1 - math.exp(-lam_r)) ** 4,
            'twin': 121 * (1 - math.exp(-lam_t) * (1 + lam_t)) ** 2}
    res = {'blocking': {k: {'predicted': round(pred[k], 1), 'observed': bc[k]['blocked_centres']}
                        for k in pred}}
    rng = np.random.default_rng(a.seed)
    rows = []
    for trial in range(40):
        P, H, d, s = 13, 12, 3, 4
        nbrs = [frozenset(rng.choice(H, size=d, replace=False).tolist()) for _ in range(P)]
        T = rng.choice(P, size=2, replace=False).tolist()
        sup, bur = support(nbrs, T, s), burning(nbrs, T)
        rows.append({'support': len(sup), 'burning': len(bur), 'burning_subset': bur <= sup,
                     'equal': sup == bur})
    res['burning'] = {'trials': len(rows), 'equal': sum(r['equal'] for r in rows),
                      'burning_subset_of_support': sum(r['burning_subset'] for r in rows),
                      'mean_support': round(float(np.mean([r['support'] for r in rows])), 2),
                      'mean_burning': round(float(np.mean([r['burning'] for r in rows])), 2)}
    json.dump(res, open(a.out, 'w'), indent=1)
    print(json.dumps(res))


if __name__ == '__main__':
    main()
