"""Adversarial falsification search for the low-density core hypothesis in the truncated ring B = F_3[s_1..s_v]/(s_i^3):
M width-two product constraints mu_a^2 mu_b^2 (total density M/9 < 1) with NO overlapping small subfamily (every pair of
constraints: four forms span 4 dims; every triple: six forms span >= --triple-span, 6 by default, i.e. no dependency;
the files loose_triples_* used 5, which admits overlapping triples).  Hill-climbing over single-form changes maximizes
the total excess sum_k max(0, H_k - T_k), k <= K, where T is W = HS_B (1 - t^4/(1+t+t^2)^2)^M truncated at its first
nonpositive coefficient.  A positive excess would be a defect without an overlapping pair or triple.
Usage: --v --M --K --steps --restarts --seed"""
import argparse, itertools, json, os, sys
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
src = open(os.path.join(HERE, '..', 'odd_prime_low_density_20260923', 'products.py')).read()
exec(src.split("res = []")[0].split("ap = argparse.ArgumentParser()")[0])
exec("def _funcs():\n    pass\n")
body = src.split("opt = ap.parse_args(); rng = np.random.default_rng(opt.seed)")[1].split("res = []")[0]
exec(body)
ap = argparse.ArgumentParser(); ap.add_argument('--v', type=int, default=8); ap.add_argument('--M', type=int, default=8)
ap.add_argument('--K', type=int, default=8); ap.add_argument('--steps', type=int, default=400); ap.add_argument('--restarts', type=int, default=4)
ap.add_argument('--seed', type=int, default=0); ap.add_argument('--quadric', action='store_true'); ap.add_argument('--triple-span', type=int, default=6); ap.add_argument('--out'); opt = ap.parse_args(); rng = np.random.default_rng(opt.seed)
v, M, K = opt.v, opt.M, opt.K; monc = [mons(v, k) for k in range(K + 1)]; _, W = series_W(v, M, K); T = truncated(W)
def ok(mus):
    if any(rank3([mus[2 * b], mus[2 * b + 1]]) < 2 for b in range(M)): return False
    if any(rank3([mus[2 * a], mus[2 * a + 1], mus[2 * b], mus[2 * b + 1]]) < 4 for a, b in itertools.combinations(range(M), 2)): return False
    return all(rank3([mus[2 * x + i] for x in S for i in (0, 1)]) >= opt.triple_span for S in itertools.combinations(range(M), 3))
def score(mus):
    P = [polymul(polymul(lin(mus[2 * b]), lin(mus[2 * b])), polymul(lin(mus[2 * b + 1]), lin(mus[2 * b + 1]))) for b in range(M)]
    H = hilbert(v, P, K, monc); return sum(max(0, h - t) for h, t in zip(H, T)), H
best_all = None; log = []
pool = None
if opt.quadric:   # structured starts and moves: forms restricted to the F_3-points of a random quadric q(x) = x^T Q x = 0
    while True:
        Q = rng.integers(0, 3, size=(v, v)); Q = (Q + Q.T) % 3
        pool = [np.array(x) for x in itertools.product(range(3), repeat=v) if any(x) and int(np.array(x) @ Q @ np.array(x)) % 3 == 0]
        if len(pool) >= 4 * M: break
def draw(): return pool[int(rng.integers(len(pool)))].copy() if pool is not None else rng.integers(0, 3, size=v)
for rs in range(opt.restarts):
    while True:
        mus = [draw() for _ in range(2 * M)]
        if ok(mus): break
    sc, H = score(mus); evals = 1
    for step in range(opt.steps):
        cand = [m.copy() for m in mus]; i = int(rng.integers(2 * M)); cand[i] = draw()
        if not ok(cand): continue
        s2, H2 = score(cand); evals += 1
        if s2 >= sc: mus, sc, H = cand, s2, H2
    log.append(dict(restart=rs, best_excess=sc, H=H, T=T, evals=evals, forms=[m.tolist() for m in mus]))
    print(dict(quadric=opt.quadric, restart=rs, best_excess=sc, evals=evals, H=H[4:], T=T[4:]), flush=True)
if opt.out: json.dump(dict(v=v, M=M, K=K, triple_span=opt.triple_span, runs=log), open(opt.out, 'w'), indent=1, default=int)
