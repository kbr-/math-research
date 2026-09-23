"""Width-two product constraints at total density below one, in the truncated ring B = F_3[s_1..s_v]/(s_i^3) (cubes of all
linear forms vanish).  Constraint b has top P_b = mu_{2b}^2 mu_{2b+1}^2 (forms mu in F_3^v), M <= 8 constraints (density
M/9 < 1).  Prediction W = HS_B * (1 - t^4/(1+t+t^2)^2)^M, exact for independent forms.  Computes the Hilbert function H of
B/(P_1..P_M) through degree K and the first degree where H differs from max(W,0).  For each defect, finds the smallest
subsets S of constraints whose own quotient B/(P_b : b in S) already differs from its own prediction by that degree, and the
span of their forms (the core).  Usage: --vs --Ms --trials --seed --K"""
import argparse, itertools, json, os, sys
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', 'odd_prime_alignment_mechanism_20260922'))
import gf3
ap = argparse.ArgumentParser(); ap.add_argument('--vs', default='4,5,6,7'); ap.add_argument('--Ms', default='3,4,6,8')
ap.add_argument('--trials', type=int, default=5); ap.add_argument('--seed', type=int, default=0); ap.add_argument('--K', type=int, default=8)
ap.add_argument('--forms', default='random'); ap.add_argument('--out'); opt = ap.parse_args(); rng = np.random.default_rng(opt.seed)
def mons(v, k): return [e for e in itertools.product(range(3), repeat=v) if sum(e) == k]
def polymul(p, q):
    out = {}
    for e, a in p.items():
        for f, b in q.items():
            g = tuple(x + y for x, y in zip(e, f))
            if max(g) <= 2: out[g] = (out.get(g, 0) + a * b) % 3
    return {e: a for e, a in out.items() if a}
def lin(mu):
    v = len(mu); return {tuple(1 if j == i else 0 for j in range(v)): int(mu[i]) % 3 for i in range(v) if mu[i] % 3}
def series_W(v, M, K):
    B = [0] * (K + 1)
    for e in itertools.product(range(3), repeat=v):
        if sum(e) <= K: B[sum(e)] += 1
    # 1/(1+t+t^2)^2 truncated
    inv = [{0: 1, 1: -1, 2: 0}[i % 3] for i in range(K + 1)]
    inv2 = [sum(inv[i] * inv[k - i] for i in range(k + 1)) for k in range(K + 1)]
    fac = [(1 if k == 0 else 0) - (inv2[k - 4] if k >= 4 else 0) for k in range(K + 1)]
    W = B[:]
    for _ in range(M): W = [sum(W[i] * fac[k - i] for i in range(k + 1)) for k in range(K + 1)]
    return B, W
def hilbert(v, P, K, monc):
    H = []
    for k in range(K + 1):
        Mk = monc[k]; idx = {e: j for j, e in enumerate(Mk)}
        if k < 4 or not P: H.append(len(Mk)); continue
        rows = []
        for m in monc[k - 4]:
            for p in P:
                r = np.zeros(len(Mk), dtype=np.uint8)
                for e, a in p.items():
                    g = tuple(x + y for x, y in zip(e, m))
                    if max(g) <= 2: r[idx[g]] = (r[idx[g]] + a) % 3
                rows.append(r)
        H.append(len(Mk) - (gf3.rank(np.array(rows)) if rows else 0))
    return H
def rank3(M):
    M = np.array(M, dtype=np.int64) % 3; r = 0
    for c in range(M.shape[1]):
        piv = next((i for i in range(r, M.shape[0]) if M[i, c]), None)
        if piv is None: continue
        M[[r, piv]] = M[[piv, r]]; M[r] = (M[r] * M[r, c]) % 3
        for i in range(M.shape[0]):
            if i != r and M[i, c]: M[i] = (M[i] - M[i, c] * M[r]) % 3
        r += 1
    return r
def truncated(W):
    """expected Hilbert function: W up to its first nonpositive coefficient, zero from there on."""
    out = []; dead = False
    for w in W:
        dead = dead or w <= 0; out.append(0 if dead else w)
    return out
def first_defect(H, W):
    T = truncated(W)
    for k in range(len(H)):
        if H[k] != T[k]: return k
    return None
res = []
for v in map(int, opt.vs.split(',')):
    monc = [mons(v, k) for k in range(opt.K + 1)]
    for M in map(int, opt.Ms.split(',')):
        if 2 * M <= v: continue
        B, W = series_W(v, M, opt.K)
        for t in range(opt.trials):
            while True:   # each constraint's two forms independent (a proportional pair has top mu^4 = 0)
                mus = [rng.integers(0, 3, size=v) for _ in range(2 * M)]
                if all(rank3([mus[2 * b], mus[2 * b + 1]]) == 2 for b in range(M)): break
            P = [polymul(polymul(lin(mus[2 * b]), lin(mus[2 * b])), polymul(lin(mus[2 * b + 1]), lin(mus[2 * b + 1]))) for b in range(M)]
            H = hilbert(v, P, opt.K, monc); k0 = first_defect(H, W)
            pairspan = min(rank3([mus[2 * a], mus[2 * a + 1], mus[2 * b], mus[2 * b + 1]]) for a, b in itertools.combinations(range(M), 2))
            row = dict(v=v, M=M, trial=t, H=H, W=W, first_defect=k0, min_pair_span=pairspan, forms=[m.tolist() for m in mus])
            if k0 is not None:
                core = None
                for s in range(1, M + 1):
                    for S in itertools.combinations(range(M), s):
                        _, WS = series_W(v, s, k0)
                        HS = hilbert(v, [P[b] for b in S], k0, monc)
                        kS = first_defect(HS, WS)
                        if kS is not None and kS <= k0:
                            core = dict(S=list(S), degree=kS, span=rank3([mus[2 * b + i] for b in S for i in (0, 1)])); break
                    if core: break
                row['core'] = core
            res.append(row)
            print({k: row.get(k) for k in ('v', 'M', 'trial', 'first_defect', 'min_pair_span', 'core')}, 'H', H[4:], 'T', truncated(W)[4:], flush=True)
if opt.out: json.dump(res, open(opt.out, 'w'), indent=1, default=int)
