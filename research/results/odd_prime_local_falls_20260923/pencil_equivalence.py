"""Check the pencil reduction at n=6, D=3: for satisfiable pencils (four selectors on L1, L2, L1+L2+c3, L1-L2+c4),
the sum S of the four constraints is affine (lambda), and the degree-D closure of base + pencil equals the closure of
base + {lambda, chi_t(tau)} with tau = L1 (or L2 if L1 is parallel to lambda) and t the tau-value outside the
allowed set.  Equality is tested by rank(union) = rank of each closure.  Usage: --seeds 1,2,... --out PATH"""
import argparse, itertools, json, os, sys
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
from local_falls import Closure, QSpace, base_rows, random_eq, add_forms, sel, gf3
def pencil_forms(rng, v, c34):
    L1, L2 = random_eq(rng, v), random_eq(rng, v); c3, c4 = c34
    return L1, L2, [L1, L2, add_forms((1, L1), (1, L2), (1, {(): c3})), add_forms((1, L1), (2, L2), (1, {(): c4}))], (c3, c4)
ap = argparse.ArgumentParser(); ap.add_argument('--seeds', default='1,2,3,4,5'); ap.add_argument('--out'); a = ap.parse_args()
sp = QSpace(6, 3); v = sp.v; out = []
pairs = [c for c in itertools.product(range(3), repeat=2) if c != (0, 0)]
for s in map(int, a.seeds.split(',')):
    for c34 in pairs:
        rng = np.random.default_rng(s); L1, L2, Ls, _ = pencil_forms(rng, v, c34)
        cons = [sel(L) for L in Ls]
        S = {}
        for c in cons:
            for m, x in c.items(): S[m] = (S.get(m, 0) + x) % 3
        S = {m: x for m, x in S.items() if x}; affine = all(len(m) <= 1 for m in S)
        # function-level description in pencil coordinates (l1, l2)
        c3, c4 = c34; vals = lambda l1, l2: [l1, l2, (l1 + l2 + c3) % 3, (l1 + 2 * l2 + c4) % 3]
        P = [(l1, l2) for l1 in range(3) for l2 in range(3) if all(x != 0 for x in vals(l1, l2))]
        lam = lambda l1, l2: sum(1 - x * x for x in vals(l1, l2)) % 3
        tau_is_L1 = len({l1 for l1, l2 in P}) == 2
        tau = (lambda l1, l2: l1) if tau_is_L1 else (lambda l1, l2: l2)
        t = ({0, 1, 2} - {tau(*q) for q in P}).pop()
        T = L1 if tau_is_L1 else L2
        Tt = add_forms((1, T), (2, {(): t}))                      # tau - t
        chi = {m: x for m, x in sel(Tt).items()}                  # 1 - (tau - t)^2
        Ca = Closure(sp, 12); Ca.add(base_rows(6) + cons); ra = Ca.split()
        Cb = Closure(sp, 12); Cb.add(base_rows(6) + [S, chi]); rb = Cb.split()
        Cu = Closure(sp, 12); Cu.add(base_rows(6) + cons + [S, chi]); ru = Cu.split()
        row = dict(seed=s, c34=list(c34), P=P, S_affine=affine, lambda_zero_on_P=all(lam(*q) == 0 for q in P),
                   pencil=ra, reduced=rb, union_rank=ru['rank'], equal=ra['rank'] == rb['rank'] == ru['rank'])
        out.append(row); print(row['seed'], row['c34'], len(P), affine, row['lambda_zero_on_P'], ra['rank'], rb['rank'], ru['rank'], row['equal'], flush=True)
json.dump(out, open(a.out, 'w'), indent=1)
print('all equal:', all(r['equal'] for r in out))
