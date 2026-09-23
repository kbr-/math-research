"""Low-density product constraints on the weak unary PHP top algebra A over F_3 (n = 7): constraint b has top
P_b = l_{2b}^2 l_{2b+1}^2 (degree 4) for linear forms l (random row functions).  Computes dim(A/(P_1..P_M))_k for k = 4, 5
and compares with W = HS_A (1 - t^4/(1+t+t^2)^2)^M, positive in degree 5 at n = 7 (gamma_5 = 21792).  Families: random;
a planted triple (three constraints whose six forms lie in a random 3-dimensional span) plus random ones; a planted
overlapping pair (two constraints whose four forms span 3 dimensions) plus random ones.  For planted families the model
B = F_3[s_1..s_d]/(s_i^3) on the planted span gives the component-corrected prediction's excess in degree 5 (the model
predicts a degree-5 excess for the triple and none for the pair).  Usage: --M --trials --seed --out"""
import itertools, json, os, sys
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', 'odd_prime_degree_four_20260923')); import a4lib as L
sys.path.insert(0, os.path.join(HERE, '..', 'odd_prime_alignment_mechanism_20260922')); import gf3
LD = os.path.join(HERE, '..', 'odd_prime_low_density_20260923')
a = dict(zip(sys.argv[1::2], sys.argv[2::2])); Mtot = int(a['--M']); trials = int(a['--trials']); rng = np.random.default_rng(int(a['--seed']))
sys.argv = [sys.argv[0], '--vs', '', '--Ms', '']
exec(open(os.path.join(LD, 'products.py')).read().split('res = []')[0])   # model functions: hilbert, series_W, polymul, lin, mons, truncated
n = 7; P1 = n + 1; L.setup(n); Q = {}; g = {0: 1}
for k in range(1, 6): Q[k], g[k] = L.quotient(k, 4)
basis = {k: [q['cols'][c] for q in Q[k].values() for c in q['nonp']] for k in Q}
NV = P1 * n
def form_poly(F): return {(i * n + j,): int(F[i, j]) for i in range(P1) for j in range(n) if F[i, j] % 3}
def top(Fa, Fb):
    la, lb = form_poly(Fa), form_poly(Fb)
    return L.mul(L.mul(la, la), L.mul(lb, lb))
def board_H(tops):
    v4 = [L.normal_form(p, Q[4], g[4]) % 3 for p in tops]
    H4 = g[4] - (gf3.rank(np.array(v4, dtype=np.uint8)) if v4 else 0)
    rows = []
    for v in v4:
        rep = {basis[4][c]: int(v[c]) for c in np.nonzero(v)[0]}
        for x in range(NV): rows.append(L.normal_form(L.mul(rep, {(x,): 1}), Q[5], g[5]) % 3)
    H5 = g[5] - gf3.rank(np.array(rows, dtype=np.uint8))
    return [g[0], g[1], g[2], g[3], H4, H5]
def W_series(M):
    K = 5; inv = [{0: 1, 1: -1, 2: 0}[i % 3] for i in range(K + 1)]
    inv2 = [sum(inv[i] * inv[k - i] for i in range(k + 1)) for k in range(K + 1)]
    fac = [(1 if k == 0 else 0) - (inv2[k - 4] if k >= 4 else 0) for k in range(K + 1)]
    W = [g[k] for k in range(K + 1)]
    for _ in range(M): W = [sum(W[i] * fac[k - i] for i in range(k + 1)) for k in range(K + 1)]
    return W
def model_excess5(coords, npl):
    """Excess in degree 5 of the planted constraints alone in the model ring on their span, over the independent prediction."""
    d = len(coords[0]); P = [polymul(polymul(lin(coords[2 * b]), lin(coords[2 * b])), polymul(lin(coords[2 * b + 1]), lin(coords[2 * b + 1]))) for b in range(npl)]
    H = hilbert(d, P, 5, [mons(d, k) for k in range(6)]); _, W = series_W(d, npl, 5); T = truncated(W)
    return H[5] - T[5], H, T
rand_form = lambda: rng.integers(0, 3, size=(P1, n))
out = []; W = W_series(Mtot)
for kind in ('random', 'triple', 'pair'):
    for tr in range(trials):
        npl = {'random': 0, 'triple': 3, 'pair': 2}[kind]; model = None
        if npl:
            d = 3; base = [rand_form() for _ in range(d)]
            while True:
                coords = [rng.integers(0, 3, size=d) for _ in range(2 * npl)]
                if all(rank3([coords[2 * b], coords[2 * b + 1]]) == 2 for b in range(npl)) and rank3(coords) == d: break
            forms = [sum(int(c) * f for c, f in zip(co, base)) % 3 for co in coords]
            model = model_excess5(coords, npl)
        else: forms = []
        forms += [rand_form() for _ in range(2 * (Mtot - npl))]
        tops = [top(forms[2 * b], forms[2 * b + 1]) for b in range(Mtot)]
        H = board_H(tops); ex = [h - w for h, w in zip(H, W)]
        rec = dict(kind=kind, trial=tr, M=Mtot, H=H, W=W, excess=ex, model_excess5=None if model is None else int(model[0]),
                   model_H=None if model is None else model[1], model_T=None if model is None else model[2], forms=[f.tolist() for f in forms])
        out.append(rec); print(kind, tr, 'H', H[4:], 'W', W[4:], 'excess', ex[4:], 'model excess5', rec['model_excess5'], flush=True)
json.dump(dict(n=n, gamma=[g[k] for k in range(6)], runs=out), open(a['--out'], 'w'), indent=1, default=int)
