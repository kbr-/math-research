"""Degree-2 PC refutability of weak unary PHP^{n+1}_n over F_3 plus M random occupancy predicates
q(L) = 1 - L^2 = 0 (L nonzero), L = sum_s c_s C_s with C_s the column sum and c uniform in F_3^n.
Claim under test: these forms are t-wise collectively wide for random c, yet about n^2/2 of them
are refuted at degree two by linearization in the occupancy monomials, far below the general-form
threshold (n-3)(n-1)+1 of the random-conditioning law.  Reuses the fast collision-quotient driver.
Usage: occupancy_predicates.py --n N --seeds S --out PATH"""
import argparse, json, os, sys
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', 'odd_prime_one_count_20260922'))
from random_conditioning_fast import QSpace, closure_of, refuted, base_rows, rref_stack, close
def occ_pred(rng, n):
    c = rng.integers(0, 3, size=n)
    L = {}
    for s in range(n):
        if c[s]:
            for i in range(n + 1):
                L[(i * n + s,)] = int(c[s])
    # 1 - L^2 over F_3, multilinear with collisions left to the quotient (vec drops collision monomials)
    sq = {}
    items = list(L.items())
    for (m1, a1) in items:
        for (m2, a2) in items:
            mon = tuple(sorted(set(m1 + m2)))
            sq[mon] = (sq.get(mon, 0) + a1 * a2) % 3
    p = {(): 1}
    for mon, v in sq.items():
        p[mon] = (p.get(mon, 0) - v) % 3
    return {m: v for m, v in p.items() if v}
ap = argparse.ArgumentParser(); ap.add_argument('--n', type=int, required=True); ap.add_argument('--seeds', type=int, default=3); ap.add_argument('--out', required=True)
a = ap.parse_args(); n = a.n
space = QSpace(n, 2)
res = {'n': n, 'D': 2, 'quotient_columns': space.cols, 'general_form_law': (n - 3) * (n - 1) + 1, 'occupancy_monomials_deg2': n + n * (n - 1) // 2, 'seeds': []}
for s in range(a.seeds):
    rng = np.random.default_rng(7000 + 10 * n + s)
    preds = [occ_pred(rng, n) for _ in range(3 * n * n)]
    P, W, piv = closure_of(space, base_rows(n))
    M = 0
    while not refuted(space, P, W):
        M += 1
        P, W, piv = rref_stack(P, W, space.cols, space.vec(preds[M - 1])[None, :])
        P, W, piv = close(space, P, W, piv)
    res['seeds'].append({'seed': 7000 + 10 * n + s, 'least_refuted_M': M})
    print(f'n={n} seed {s}: least refuted M = {M}; occupancy monomials {res["occupancy_monomials_deg2"]}; general-form law {res["general_form_law"]}', flush=True)
json.dump(res, open(a.out, 'w'), indent=1)
