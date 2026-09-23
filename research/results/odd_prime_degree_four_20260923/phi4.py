"""Rank of Phi_4 : A_2^M -> A_4, (a_b) -> sum_b a_b l_b^2, for M uniform linear forms l_b over F_3 (weak unary PHP top
algebra, n holes).  The semi-regular model (Frobenius syzygies l_b A_1 e_b and Koszul syzygies l_c^2 e_b - l_b^2 e_c
only) predicts rank = min(gamma_4, M(gamma_2 - gamma_1) - C(M,2)), the t^4 coefficient of
HS_A(t)((1-t^2)/(1-t^3))^M.  Usage: --n N --Ms M1,M2,... --seed S --workers W --out PATH"""
import argparse, json, os, sys, time
from multiprocessing import Pool
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import a4lib as L
from a4lib import gf3
ap = argparse.ArgumentParser(); ap.add_argument('--n', type=int, default=7); ap.add_argument('--Ms', default='20,40,41')
ap.add_argument('--seed', type=int, default=0); ap.add_argument('--workers', type=int, default=12); ap.add_argument('--out')
opt = ap.parse_args(); L.setup(opt.n)
t0 = time.time()
Q2, g2 = L.quotient(2, opt.workers); Q4, g4 = L.quotient(4, opt.workers)
Q1, g1 = L.quotient(1, opt.workers)
basis2 = [q['cols'][c] for q in Q2.values() for c in q['nonp']]
print(f'n={opt.n}: gamma_1={g1} gamma_2={g2} gamma_4={g4} ({time.time()-t0:.0f}s)', flush=True)
Ms = [int(x) for x in opt.Ms.split(',')]; Mmax = max(Ms)
rng = np.random.default_rng(opt.seed); ls = [rng.integers(0, 3, size=L.v) for _ in range(Mmax)]
def block(b):
    sq = L.square(ls[b])
    rows = np.zeros((len(basis2), g4), dtype=np.uint8)
    for k, m in enumerate(basis2): rows[k] = L.normal_form(L.mul({m: 1}, sq), Q4, g4)
    return gf3.pack(rows)[0]
with Pool(opt.workers) as pool: blocks = pool.map(block, range(Mmax), chunksize=1)
W = (g4 + 63) // 64
print(f'rows built ({time.time()-t0:.0f}s)', flush=True)
res = dict(n=opt.n, gamma_1=g1, gamma_2=g2, gamma_4=g4, seed=opt.seed, runs=[])
for M in Ms:
    P = np.vstack(blocks[:M]); r = gf3.rref(None, parallel=True, packed=(P, W, g4))[2].shape[0]; del P
    pred = min(g4, M * (g2 - g1) - M * (M - 1) // 2)
    res['runs'].append(dict(M=M, rank=int(r), predicted=int(pred), kernel_excess=int(pred - r)))
    print(res['runs'][-1], f'({time.time()-t0:.0f}s)', flush=True)
    if opt.out: json.dump(res, open(opt.out, 'w'), indent=1)
