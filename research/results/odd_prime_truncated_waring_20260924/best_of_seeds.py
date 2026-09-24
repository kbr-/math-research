"""Best rank over seeds of the double-point map in T = F_3[y]/(y^3) (see double_points_T.py): for each d,
the largest rank over S seeded random F_3 sequences at M_inj and at M_inj+1, against the expected values.
A best rank equal to the expected value certifies generic maximal rank for that d (lower semicontinuity);
a deficit at every seed suggests a defect over F_3bar but does not prove one (F_3 points may be special).
Usage: python3 best_of_seeds.py OUT.json DMIN DMAX SEEDS"""
import json, sys, time
from math import comb
import numpy as np
sys.path.insert(0, 'research/results/odd_prime_truncated_waring_20260924'); sys.path.insert(0, 'research/tools')
from double_points_T import monomials, phi_rows
from rank_modp import rank_mod_p

def main():
    out = {'cases': []}; dmin, dmax, S = int(sys.argv[2]), int(sys.argv[3]), int(sys.argv[4]); t0 = time.time()
    for d in range(dmin, dmax + 1):
        m3 = monomials(d, 3); idx3 = {e: i for i, e in enumerate(m3)}; T3 = len(m3); Minj = T3 // (d - 1)
        best_i = best_o = 0
        for s in range(S):
            rng = np.random.default_rng(10**6 * d + s)
            forms = [list(rng.integers(0, 3, d)) for _ in range(Minj + 1)]
            best_i = max(best_i, rank_mod_p(phi_rows(forms[:Minj], d, idx3), T3, 3))
            best_o = max(best_o, rank_mod_p(phi_rows(forms, d, idx3), T3, 3))
        rec = {'d': d, 'dimT3': T3, 'M_inj': Minj, 'best_rank_inj': best_i, 'expected_inj': Minj * (d - 1),
               'best_rank_onto': best_o, 'expected_onto': min(T3, (Minj + 1) * (d - 1)), 'seeds': S}
        rec['certified'] = best_i == rec['expected_inj'] and best_o == rec['expected_onto']
        out['cases'].append(rec); print(json.dumps(rec), flush=True)
    out['seconds'] = round(time.time() - t0, 1); json.dump(out, open(sys.argv[1], 'w'), indent=1); print('seconds', out['seconds'])

if __name__ == '__main__':
    main()
