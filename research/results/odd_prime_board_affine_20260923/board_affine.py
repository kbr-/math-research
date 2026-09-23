"""Special position of robust affine systems in the weak unary PHP top algebra A over F_3 (n holes, component-wise normal
forms from a4lib.py).  For linear forms l_1..l_r (row functions f^b_i), computes the Hilbert function of A/(l_1..l_r) through
degree K and compares it with W = HS_A/(1+t+t^2)^r truncated at its first nonpositive coefficient (graded Nakayama: equality
through D iff A is free over F_3[l]/(l^3)^{(x)r} through D).  Robustness hypothesis of the wide-conditioning conjecture:
every nonzero F_3-combination has row functions Q-robust (nonconstant after deleting any Q labels) on at least t rows.
Families: random (uniform forms), column (every row carries the same hole function phi_b), mixed (column plus uniform).
Usage: --n --rs --K --family --trials --Q --t --seed"""
import argparse, itertools, json, os, sys
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', 'odd_prime_degree_four_20260923'))
import a4lib as L
ap = argparse.ArgumentParser(); ap.add_argument('--n', type=int, default=7); ap.add_argument('--rs', default='2,3,4,5')
ap.add_argument('--K', type=int, default=3); ap.add_argument('--family', default='random'); ap.add_argument('--trials', type=int, default=4)
ap.add_argument('--Q', type=int, default=2); ap.add_argument('--t', type=int, default=5); ap.add_argument('--seed', type=int, default=0)
ap.add_argument('--phis', default=None); ap.add_argument('--out'); opt = ap.parse_args(); L.setup(opt.n); n = opt.n; P1 = n + 1; rng = np.random.default_rng(opt.seed)
Q = {}; g = {}
for k in range(1, opt.K + 1): Q[k], g[k] = L.quotient(k, 2)
g[0] = 1; basis = {k: [q['cols'][c] for q in Q[k].values() for c in q['nonp']] for k in Q}; basis[0] = [()]
def robust_row(f):
    return all(len(set(f[j] for j in range(n) if j not in X)) >= 2 for X in itertools.combinations(range(n), opt.Q))
def robust_system(F):   # F: list of r arrays of shape (P1, n)
    r = len(F)
    for c in itertools.product(range(3), repeat=r):
        if not any(c): continue
        G = sum(ci * Fi for ci, Fi in zip(c, F)) % 3
        if sum(robust_row(G[i]) for i in range(P1)) < opt.t: return False
    return True
def W_trunc(r, K):
    inv = [{0: 1, 1: -1, 2: 0}[i % 3] for i in range(K + 1)]; c = [1] + [0] * K
    for _ in range(r): c = [sum(c[i] * inv[k - i] for i in range(k + 1)) for k in range(K + 1)]
    W = [sum(g[i] * c[k - i] for i in range(k + 1)) for k in range(K + 1)]; out = []; dead = False
    for w in W: dead = dead or w <= 0; out.append(0 if dead else w)
    return W, out
def hilbert(F):
    lins = [{(i * n + j,): int(Fb[i, j]) for i in range(P1) for j in range(n) if Fb[i, j]} for Fb in F]
    H = [1]
    for k in range(1, opt.K + 1):
        pairs = [(m, lin) for m in basis[k - 1] for lin in lins]; packs = []; Wk = (g[k] + 63) // 64
        for c0 in range(0, len(pairs), 2000):   # pack in chunks: a dense degree-4 block at n=8 would need about 4 GB
            ch = pairs[c0:c0 + 2000]; rows = np.zeros((len(ch), g[k]), dtype=np.uint8)
            for t, (m, lin) in enumerate(ch): rows[t] = L.normal_form(L.mul({m: 1}, lin) if m else lin, Q[k], g[k])
            packs.append(L.gf3.pack(rows)[0])
        H.append(g[k] - L.gf3.rref(None, parallel=True, packed=(np.vstack(packs), Wk, g[k]))[2].shape[0])
    return H
def draw(r):
    if opt.family == 'random': return [rng.integers(0, 3, size=(P1, n)) for _ in range(r)]
    if opt.family == 'column': return [np.tile(rng.integers(0, 3, size=n), (P1, 1)) for _ in range(r)]
    if opt.family == 'mixed': return [np.tile(rng.integers(0, 3, size=n), (P1, 1)) if b % 2 == 0 else rng.integers(0, 3, size=(P1, n)) for b in range(r)]
res = []
if opt.phis:   # explicit single column-type forms, one system per hole function
    W, T = W_trunc(1, opt.K)
    for s_ in opt.phis.split(';'):
        phi = np.array([int(x) for x in s_.split(',')]); F = [np.tile(phi, (P1, 1))]
        H = hilbert(F); excess = [h - x for h, x in zip(H, T)]
        res.append(dict(r=1, family='explicit-column', phi=phi.tolist(), robust=robust_system(F), H=H, T=T, W=W, excess=excess))
        print({k: res[-1][k] for k in ('phi', 'robust', 'H', 'T', 'excess')}, flush=True)
    opt.rs = ''
for r in (map(int, opt.rs.split(',')) if opt.rs else []):
    W, T = W_trunc(r, opt.K)
    for tr in range(opt.trials):
        for att in range(500):
            F = draw(r)
            if robust_system(F): break
        else:
            res.append(dict(r=r, trial=tr, robust_found=False)); print(res[-1], flush=True); continue
        H = hilbert(F); excess = [h - x for h, x in zip(H, T)]
        res.append(dict(r=r, trial=tr, family=opt.family, H=H, T=T, W=W, excess=excess, forms=[f.tolist() for f in F]))
        print(dict(r=r, trial=tr, family=opt.family, H=H, T=T, excess=excess), flush=True)
if opt.out: json.dump(dict(n=n, K=opt.K, Q=opt.Q, t=opt.t, gamma=[g[k] for k in range(opt.K + 1)], runs=res), open(opt.out, 'w'), indent=1, default=int)
