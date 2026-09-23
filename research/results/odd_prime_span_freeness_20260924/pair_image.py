"""Image subalgebra of the recorded occupancy pair in the weak unary PHP top algebra A (n = 8, F_3): dimensions of
Tbar_t = span{l_1^a l_2^b : a + b = t, a, b <= 2} in A_t for t = 2, 3 (normal forms from a4lib).  With the recorded
HS_A = (1,63,1656,22929) and A/(l_1,l_2)A = (1,61,1531,19685), the kernel of Tbar (x) C -> A in degree 3 is
19685 + 2*1531 + dim(Tbar_2)*61 + dim(Tbar_3) - 22929.  Usage: python3 pair_image.py OUT.json"""
import json, os, sys
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); RES = os.path.join(HERE, '..'); BA = os.path.join(RES, 'odd_prime_board_affine_20260923')
outp = sys.argv[1]; sys.argv = [sys.argv[0], '--n', '8', '--K', '3', '--rs', '', '--family', 'random']
exec(open(os.path.join(BA, 'board_affine.py')).read().split("res = []\nif opt.phis:")[0])
rec = json.load(open(os.path.join(BA, 'n8_K3_column_robust.json')))['runs'][0]
l1, l2 = [{(i * n + j,): int(Fb[i, j]) for i in range(P1) for j in range(n) if Fb[i, j]} for Fb in [np.array(f) for f in rec['forms']]]
p11, p12, p22 = L.mul(l1, l1), L.mul(l1, l2), L.mul(l2, l2)
T2 = np.array([L.normal_form(p, Q[2], g[2]) % 3 for p in (p11, p12, p22)], dtype=np.uint8)
T3 = np.array([L.normal_form(L.mul(p11, l2), Q[3], g[3]) % 3, L.normal_form(L.mul(p22, l1), Q[3], g[3]) % 3], dtype=np.uint8)
d2, d3 = int(L.gf3.rank(T2)), int(L.gf3.rank(T3))
ker3 = 19685 + 2 * 1531 + d2 * 61 + d3 - g[3]
res = dict(gamma=[1, g[1], g[2], g[3]], Tbar2=d2, Tbar3=d3, kernel_degree3=ker3, forms=rec['forms'])
print(res); json.dump(res, open(outp, 'w'), indent=1)
