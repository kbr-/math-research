"""Selector count with a linear dependency among the forms: l_1..l_{k-1} uniform, l_k = l_1+...+l_{k-1} (--dep k), then
further uniform forms.  --deg 3 compares rank Phi_3 with min(gamma_3, M(gamma_1-1)); --deg 4 compares rank Phi_4 with
min(gamma_4, M(gamma_2-gamma_1)-C(M,2)).  (A first version of this docstring claimed that a five-term dependency breaks
freeness at degree 2; in the Nakayama sense it first breaks it at degree 4, see the entry.)  Usage: --n --Ms --seed --dep --deg"""
import argparse, json, os, sys
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', 'odd_prime_degree_four_20260923'))
import a4lib as L
ap = argparse.ArgumentParser(); ap.add_argument('--n', type=int, default=6); ap.add_argument('--Ms', default='5,10,20,40,60')
ap.add_argument('--seed', type=int, default=0); ap.add_argument('--dep', type=int, default=5); ap.add_argument('--deg', type=int, default=3); ap.add_argument('--out'); opt = ap.parse_args(); L.setup(opt.n)
Q1, g1 = L.quotient(1, 2); Q2, g2 = L.quotient(2, 2); Qt, gt = L.quotient(opt.deg, 2)
basis = [q['cols'][c] for q in (Q1 if opt.deg == 3 else Q2).values() for c in q['nonp']]
rng = np.random.default_rng(opt.seed); Ms = [int(x) for x in opt.Ms.split(',')]
ls = [rng.integers(0, 3, size=L.v) for _ in range(opt.dep - 1)]; ls.append(sum(ls) % 3)
ls += [rng.integers(0, 3, size=L.v) for _ in range(max(Ms) - opt.dep)]
blocks = []
for l in ls:
    sq = L.square(l); blocks.append(np.array([L.normal_form(L.mul({m: 1}, sq), Qt, gt) for m in basis], dtype=np.uint8))
res = dict(n=opt.n, gamma_1=g1, gamma_2=g2, gamma_target=gt, deg=opt.deg, dep=opt.dep, seed=opt.seed, runs=[])
for M in Ms:
    r = L.gf3.rank(np.vstack(blocks[:M]), parallel=True)
    pred = min(gt, M * (g1 - 1)) if opt.deg == 3 else min(gt, M * (g2 - g1) - M * (M - 1) // 2)
    res['runs'].append(dict(M=M, rank=int(r), predicted=int(pred))); print(res['runs'][-1], flush=True)
if opt.out: json.dump(res, open(opt.out, 'w'), indent=1)
