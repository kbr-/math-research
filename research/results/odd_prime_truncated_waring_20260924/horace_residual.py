"""Naive hyperplane Horace for double points in T = F_3[y_1..y_d]/(y_i^3), degree 3.

Split T_3 = T'_3 + T'_2 y_d + T'_1 y_d^2 (T' in y_1..y_{d-1}). Specialize s forms into W' (no y_d); the other
r = M - s forms are l = l' + y_d. rank Phi >= rank(trace) + rank(residual), where the trace is the double-point
map of the s specialized forms in T'_3 (the same problem in d-1 variables) and the residual is the image
modulo T'_3, in T'_2 (+) T'_1: specialized forms give l_s^2 y_d; a free form l = l'+y_d gives, for w' in W',
(2 l' w', w') and, for w = y_d, (l'^2, 2 l'). Expected residual rank: min(s + r(d-1), C(d,2) + d - 1).
Tested prediction: the residual is defective once C(r,2) > d-1, because Koszul pairs l'_t e_s - l'_s e_t
(c = 0) meet only d-1 linear conditions in T'_1. The split used is the balanced one: M = M_inj(d),
s = min(M, M_inj(d-1)). Usage: python3 horace_residual.py OUT.json DMIN DMAX SEEDS"""
import itertools, json, sys, time
from math import comb
import numpy as np
sys.path.insert(0, 'research/results/odd_prime_truncated_waring_20260924'); sys.path.insert(0, 'research/tools')
from double_points_T import monomials, square
from rank_modp import rank_mod_p

def residual_rank(Sforms, Rforms, dp):
    m2 = monomials(dp, 2); i2 = {e: k for k, e in enumerate(m2)}; n2 = len(m2)
    rows = []
    for l in Sforms:
        rows.append({i2[e]: c for e, c in square(l, dp).items()})
    for l in Rforms:
        for j in range(dp):                       # w' = y_j: (2 l' y_j, y_j)
            row = {}
            for i in range(dp):
                if l[i] % 3:
                    e = [0] * dp; e[i] += 1; e[j] += 1
                    k = i2[tuple(e)]; row[k] = (row.get(k, 0) + 2 * l[i]) % 3
            row[n2 + j] = (row.get(n2 + j, 0) + 1) % 3
            rows.append({k: v for k, v in row.items() if v})
        row = {i2[e]: c for e, c in square(l, dp).items()}      # w = y_d: (l'^2, 2 l')
        for i in range(dp):
            if l[i] % 3: row[n2 + i] = (2 * l[i]) % 3
        rows.append({k: v for k, v in row.items() if v})
    return rank_mod_p(rows, n2 + dp, 3), n2 + dp

def main():
    out = {'cases': []}; dmin, dmax, S = int(sys.argv[2]), int(sys.argv[3]), int(sys.argv[4]); t0 = time.time()
    for d in range(dmin, dmax + 1):
        D = lambda k: comb(k + 2, 3) - k
        M = D(d) // (d - 1); s = min(M, D(d - 1) // (d - 2)); r = M - s; dp = d - 1
        best = 0
        for sd in range(S):
            rng = np.random.default_rng(7 * 10**6 + 1000 * d + sd)
            Sf = [list(rng.integers(0, 3, dp)) for _ in range(s)]; Rf = [list(rng.integers(0, 3, dp)) for _ in range(r)]
            rk, tgt = residual_rank(Sf, Rf, dp); best = max(best, rk)
        exp = min(s + r * (d - 1), tgt)
        rec = {'d': d, 'M': M, 's': s, 'r': r, 'residual_best': best, 'residual_expected': exp, 'target': tgt,
               'deficit': exp - best, 'koszul_excess': max(0, comb(r, 2) - (d - 1)), 'seeds': S}
        out['cases'].append(rec); print(json.dumps(rec), flush=True)
    out['seconds'] = round(time.time() - t0, 1); json.dump(out, open(sys.argv[1], 'w'), indent=1); print('seconds', out['seconds'])

if __name__ == '__main__':
    main()
