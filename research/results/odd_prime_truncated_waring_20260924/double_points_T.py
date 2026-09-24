"""Double points in the truncated algebra T = F_3[y_1..y_d]/(y_i^3), degree 3.

Tested statement (for prop:free-span-double-points): for generic linear forms l_1..l_M in W = T_1, the map
Phi: W^M -> T_3, (w_t) -> sum_t l_t^2 w_t, has rank min(M(d-1), dim T_3) (its kernel always contains the M
independent Frobenius syzygies l_t e_t, since l^3 = 0 in T), and the squares l_t^2 are independent in T_2 for
M <= dim T_2. Rank is lower semicontinuous, so one F_3 witness with the expected rank proves the generic
statement; injectivity passes to prefixes and surjectivity to extensions, so one seeded random sequence is
checked at M_inj = floor(dim T_3/(d-1)) (injective modulo Frobenius) and M_inj + 1 (onto), and the squares at
min(M_inj + 1, dim T_2). dim T_3 = C(d+2,3) - d, dim T_2 = C(d+1,2). Exact ranks: research/tools/rank_modp.cpp.
Usage: python3 double_points_T.py OUT.json DMAX"""
import itertools, json, sys, time
from math import comb
import numpy as np
sys.path.insert(0, 'research/tools')
from rank_modp import rank_mod_p

def monomials(d, k):
    out = []
    for c in itertools.combinations_with_replacement(range(d), k):
        e = [0] * d
        for i in c: e[i] += 1
        if max(e) <= 2: out.append(tuple(e))
    return out

def square(l, d):
    sq = {}
    for i in range(d):
        for j in range(i, d):
            c = (l[i] * l[j] * (1 if i == j else 2)) % 3
            if c:
                e = [0] * d; e[i] += 1; e[j] += 1
                if max(e) <= 2: sq[tuple(e)] = (sq.get(tuple(e), 0) + c) % 3
    return sq

def phi_rows(forms, d, idx3):
    rows = []
    for l in forms:
        sq = square(l, d)
        for j in range(d):
            row = {}
            for e, c in sq.items():
                f = list(e); f[j] += 1
                if f[j] <= 2:
                    k = idx3[tuple(f)]; row[k] = (row.get(k, 0) + c) % 3
            rows.append({k: v for k, v in row.items() if v})
    return rows

def main():
    out = {'cases': [], 'failures': []}; dmax = int(sys.argv[2]); t0 = time.time()
    for d in range(2, dmax + 1):
        m3 = monomials(d, 3); idx3 = {e: i for i, e in enumerate(m3)}; m2 = monomials(d, 2); idx2 = {e: i for i, e in enumerate(m2)}
        T3, T2 = len(m3), len(m2)
        assert T3 == comb(d + 2, 3) - d and T2 == comb(d + 1, 2)
        Minj = T3 // (d - 1); rng = np.random.default_rng(1000 + d)
        forms = [list(rng.integers(0, 3, d)) for _ in range(Minj + 1)]
        r_inj = rank_mod_p(phi_rows(forms[:Minj], d, idx3), T3, 3)
        r_on = rank_mod_p(phi_rows(forms, d, idx3), T3, 3)
        Ms = min(Minj + 1, T2)
        r_sq = rank_mod_p([{idx2[e]: c for e, c in square(l, d).items()} for l in forms[:Ms]], T2, 3)
        rec = {'d': d, 'dimT3': T3, 'dimT2': T2, 'M_inj': Minj, 'rank_inj': r_inj, 'expected_inj': Minj * (d - 1),
               'rank_onto': r_on, 'expected_onto': min(T3, (Minj + 1) * (d - 1)), 'squares_rank': r_sq, 'squares_M': Ms}
        ok = r_inj == Minj * (d - 1) and r_on == min(T3, (Minj + 1) * (d - 1)) and r_sq == Ms
        rec['maximal_rank'] = ok
        out['cases'].append(rec); print(json.dumps(rec), flush=True)
        if not ok: out['failures'].append(d)
    out['seconds'] = round(time.time() - t0, 1); json.dump(out, open(sys.argv[1], 'w'), indent=1)
    print('failures', out['failures'], 'seconds', out['seconds'])

if __name__ == '__main__':
    main()
