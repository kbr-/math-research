"""Graded dimensions gamma_k of the weak unary PHP top algebra over F_3 (component-wise), and the semi-regular counts:
degree-3 fill M3 = ceil(gamma_3/(gamma_1-1)) and degree-4 fill M4 = least M with gamma_4 - M(gamma_2-gamma_1) + C(M,2) <= 0,
the t^3 and t^4 coefficients of HS_A(t)((1-t^2)/(1-t^3))^M.  Usage: --n N --workers W"""
import argparse, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import a4lib as L
ap = argparse.ArgumentParser(); ap.add_argument('--n', type=int); ap.add_argument('--workers', type=int, default=2); opt = ap.parse_args()
L.setup(opt.n); g = [1] + [L.quotient(k, opt.workers)[1] for k in (1, 2, 3, 4)]
M3 = -(-g[3] // (g[1] - 1)); M4 = next(M for M in range(1, 10 ** 6) if g[4] - M * (g[2] - g[1]) + M * (M - 1) // 2 <= 0)
print(dict(n=opt.n, gamma=g, degree3_fill=M3, degree4_fill=M4))
