"""Rank of Phi_4 : A_2^M -> A_4, (a_b) -> sum_b a_b l_b^2, on the weak unary PHP top algebra (n holes), for the
function-form specialization: l_b = sum_i c_{b,i} x_{i, sigma_b(i)}, one cell per pigeon, with sigma_b a uniform
function from pigeons to holes and c_{b,i} = 1 (--coef one) or uniform in {1,2} (--coef random); or, with
--family orbit, l_b = the base uniform form shifted by (r_b, h_b) in Z_(n+1) x Z_n (pigeon i -> i+r, hole a -> a+h),
the shifts taken in the order of a seeded shuffle.  Computes the rank for every prefix M = 1..max(Ms) in one incremental elimination
(gf3_prefix.c) and compares with the recorded generic count min(gamma_4, M(gamma_2 - gamma_1) - C(M,2)).  Reuses the recorded a4lib machinery.
Usage: --n N --Ms M1,M2,... --seed S --coef one|random --workers W --out PATH"""
import argparse, json, os, sys, time
from multiprocessing import Pool
import numpy as np
REC = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'odd_prime_degree_four_20260923')
sys.path.insert(0, REC); sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import a4lib as L
from a4lib import gf3
ap = argparse.ArgumentParser(); ap.add_argument('--n', type=int, default=7); ap.add_argument('--Ms', default='2,5,20,39,40')
ap.add_argument('--seed', type=int, default=0); ap.add_argument('--coef', default='one'); ap.add_argument('--workers', type=int, default=12)
ap.add_argument('--family', default='function'); ap.add_argument('--out'); opt = ap.parse_args(); L.setup(opt.n)
t0 = time.time()
Q2, g2 = L.quotient(2, opt.workers); Q4, g4 = L.quotient(4, opt.workers); Q1, g1 = L.quotient(1, opt.workers)
basis2 = [q['cols'][c] for q in Q2.values() for c in q['nonp']]
print(f'n={opt.n}: gamma_1={g1} gamma_2={g2} gamma_4={g4} ({time.time()-t0:.0f}s)', flush=True)
Ms = [int(x) for x in opt.Ms.split(',')]; Mmax = max(Ms)
rng = np.random.default_rng(opt.seed); ls = []
if opt.family == 'orbit':
    base = rng.integers(0, 3, size=L.v); shifts = [(r, h) for r in range(L.P1) for h in range(L.n)]
    order = rng.permutation(len(shifts))
    for t in order[:Mmax]:
        r, h = shifts[t]; l = np.zeros(L.v, dtype=np.int64)
        for i in range(L.P1):
            for a in range(L.n): l[((i + r) % L.P1) * L.n + (a + h) % L.n] = base[i * L.n + a]
        ls.append(l)
for _ in range(Mmax if opt.family == 'function' else 0):
    l = np.zeros(L.v, dtype=np.int64)
    for i in range(L.P1):
        l[i * L.n + int(rng.integers(0, L.n))] = 1 if opt.coef == 'one' else int(rng.integers(1, 3))
    ls.append(l)
def block(b):
    sq = L.square(ls[b])
    rows = np.zeros((len(basis2), g4), dtype=np.uint8)
    for k, m in enumerate(basis2): rows[k] = L.normal_form(L.mul({m: 1}, sq), Q4, g4)
    return gf3.pack(rows)[0]
with Pool(opt.workers) as pool: blocks = pool.map(block, range(Mmax), chunksize=1)
W = (g4 + 63) // 64
print(f'rows built ({time.time()-t0:.0f}s)', flush=True)
res = dict(n=opt.n, gamma_1=g1, gamma_2=g2, gamma_4=g4, seed=opt.seed, coef=opt.coef, family=opt.family, forms=[l.tolist() for l in ls], runs=[])
from gf3_prefix import prefix_ranks
P = np.vstack(blocks[:Mmax]); ends = [len(basis2) * (b + 1) for b in range(Mmax)]
ranks = prefix_ranks(P, W, g4, ends, threads=opt.workers); del P       # one elimination, every prefix M = 1..Mmax
for M in range(1, Mmax + 1):
    r = ranks[M - 1]; pred = min(g4, M * (g2 - g1) - M * (M - 1) // 2)
    res['runs'].append(dict(M=M, rank=int(r), predicted=int(pred), kernel_excess=int(pred - r)))
print('first excess at M =', next((x['M'] for x in res['runs'] if x['kernel_excess']), None),
      '; ranks at', {x['M']: (x['rank'], x['predicted']) for x in res['runs'] if x['M'] in Ms}, f'({time.time()-t0:.0f}s)', flush=True)
if opt.out: json.dump(res, open(opt.out, 'w'), indent=1)
