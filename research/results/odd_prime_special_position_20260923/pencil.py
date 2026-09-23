"""Special-position defects without bounded core, rank-one model over F_3.  Points mu_1..mu_N in F_3^v (random, N =
C(v+1,2)-2) have a pencil of quadrics through them; add an F_3-point mu_{N+1} of the pencil's base locus not among them.
Then the m = N+1 squares mu_c^2 are linearly dependent in S_2 (dim C(v+1,2)) although W_2 = C(v+1,2) - m = 1 > 0.
Reports the support of the dependency (the smallest defect-carrying subset: the dependency space is one-dimensional,
so every dependent subset of squares contains its support), the girth of the points (single-element range) and checks the
X-model quotient dims directly.  Usage: --vs 3,4,5,6 --trials T --seed S"""
import argparse, itertools, json, os, sys
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', 'odd_prime_alignment_mechanism_20260922'))
import gf3
ap = argparse.ArgumentParser(); ap.add_argument('--vs', default='3,4,5,6'); ap.add_argument('--trials', type=int, default=3)
ap.add_argument('--seed', type=int, default=0); ap.add_argument('--cap', action='store_true'); ap.add_argument('--out'); opt = ap.parse_args(); rng = np.random.default_rng(opt.seed)
def nullspace(M):
    """basis of {a : a M = 0} over F_3 for an integer matrix M (rows = vectors)."""
    M = np.array(M, dtype=np.int64) % 3; n = M.shape[0]
    A = np.concatenate([M, np.eye(n, dtype=np.int64)], axis=1); r = 0
    for c in range(M.shape[1]):
        piv = next((i for i in range(r, n) if A[i, c]), None)
        if piv is None: continue
        A[[r, piv]] = A[[piv, r]]; A[r] = (A[r] * A[r, c]) % 3
        for i in range(n):
            if i != r and A[i, c]: A[i] = (A[i] - A[i, c] * A[r]) % 3
        r += 1
    return A[r:, M.shape[1]:]
def veronese(p):
    v = len(p); return np.array([p[i] * p[j] for i in range(v) for j in range(i, v)]) % 3
def projective_points(v):
    out = []
    for p in itertools.product(range(3), repeat=v):
        if any(p) and p[next(i for i in range(v) if p[i])] == 1: out.append(np.array(p))
    return out
def girth(P):
    """smallest number of points with a nontrivial linear dependency (min weight of the null space code)."""
    N = nullspace(P)  # rows: dependencies a with sum a_c mu_c = 0
    if len(N) == 0: return None
    best = P.shape[0]
    for coeffs in itertools.product(range(3), repeat=len(N)):
        if any(coeffs):
            w = int(((np.array(coeffs) @ N) % 3 != 0).sum()); best = min(best, w)
    return best
res = []
for v in map(int, opt.vs.split(',')):
    pts_all = projective_points(v); dimS2 = v * (v + 1) // 2; N = dimS2 - 2
    for t in range(opt.trials):
        for attempt in range(200):
            if opt.cap:   # random greedy cap: no three collinear points (no 3-term dependency)
                order = rng.permutation(len(pts_all)); P = []
                for i in order:
                    p = pts_all[i]
                    if all(not any(((p + e * a + f * b) % 3 == 0).all() for e in (1, 2) for f in (1, 2)) for a, b in itertools.combinations(P, 2)):
                        P.append(p)
                    if len(P) == N: break
                if len(P) < N: continue
            else:
                idx = rng.choice(len(pts_all), N, replace=False); P = [pts_all[i] for i in idx]
            V = np.array([veronese(p) for p in P])
            Q = nullspace(V.T)            # quadrics q (coefficient vectors) with q . veronese(p) = 0 for all p in P
            if len(Q) != 2: continue
            base = [p for p in pts_all if not any((p == x).all() for x in P) and all((q @ veronese(p)) % 3 == 0 for q in Q)]
            if base: break
        else:
            res.append(dict(v=v, trial=t, found=False)); continue
        P.append(base[0]); Pm = np.array(P); V = np.array([veronese(p) for p in P])
        dep = nullspace(V)                # dependencies among the squares
        supp = [int(((d % 3) != 0).sum()) for d in dep]
        sp = [int(np.linalg.matrix_rank(Pm[(d % 3) != 0].astype(float))) if False else None for d in dep]
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
        sp = [rank3(Pm[(d % 3) != 0]) for d in dep]
        g = girth(Pm) if (len(P) - v) <= 12 else None
        res.append(dict(v=v, trial=t, found=True, m=len(P), W2=dimS2 - len(P), dependency_dim=len(dep), support=supp, support_span=sp,
                        base_points_available=len(base), girth=g, points=Pm.tolist()))
        print({k: res[-1][k] for k in ('v', 'trial', 'm', 'W2', 'dependency_dim', 'support', 'support_span', 'base_points_available', 'girth')}, flush=True)
if opt.out: json.dump(res, open(opt.out, 'w'), indent=1, default=int)
