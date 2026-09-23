"""Is l_1^2 l_2^2 nonzero in A_4 (weak unary PHP top algebra, n = 8, F_3) for the recorded occupancy pair?  Together with
pair_image.json (Tbar_2 = 3, Tbar_3 = 2) this decides whether gr R_C = F_3[y1,y2]/(y^3) -> A is injective in every degree
(its top degree is 4).  Normal form in A_4 from a4lib (quotient setup in degree 4 only).  Usage: python3 pair_top.py OUT.json"""
import json, os, sys, time
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); RES = os.path.join(HERE, '..')
sys.path.insert(0, os.path.join(RES, 'odd_prime_degree_four_20260923')); import a4lib as L
t0 = time.time(); n = 8; P1 = n + 1; L.setup(n)
Q4, g4 = L.quotient(4, 2); print('degree-4 quotient dim', g4, f'({time.time()-t0:.0f}s)', flush=True)
rec = json.load(open(os.path.join(RES, 'odd_prime_board_affine_20260923', 'n8_K3_column_robust.json')))['runs'][0]
l1, l2 = [{(i * n + j,): int(Fb[i, j]) for i in range(P1) for j in range(n) if Fb[i, j]} for Fb in [np.array(f) for f in rec['forms']]]
p = L.mul(L.mul(l1, l1), L.mul(l2, l2)); v = L.normal_form(p, Q4, g4) % 3
res = dict(g4=int(g4), nonzero=bool(v.any()), support=int((v != 0).sum()))
print(res, f'({time.time()-t0:.0f}s)', flush=True); json.dump(res, open(sys.argv[1], 'w'), indent=1)
