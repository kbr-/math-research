"""Tropical leading-term lower bound for double points on the pattern algebra P (R x L board).
Forms l_j = sum_x c_{j,x} t^{w_j(x)} x with generic c.  The double-point matrix has rows = 3-faces F, columns (j,u);
entry at (F,(j,u)) for u in F is 2 c_{j,x} c_{j,y} t^{w_j(F)-w_j(u)} ({x,y} = F - u).  For weights with no ties, after
scaling each row by t^{-min order} the t=0 matrix has one nonzero entry per row, at (j(F), z(F)) = argmin_{j,u}
(w_j(F) - w_j(u)), i.e. z(F) the w_j-heaviest cell and j(F) the form minimizing the sum of F's two lighter weights.
So rank over F(t), hence for generic forms over F_3bar, is >= #distinct (j(F), z(F)) (semicontinuity; any characteristic).
Compared with the maximum min(gamma_3, M(gamma_1-1)).  Weight families: uniform random reals; 'linear'
(random linear function of (row, label) plus small noise).  Usage: python3 tropical_count.py --R 7 --L 5 --trials 20 --out F"""
import argparse, itertools, json, math
import numpy as np
PAT3 = {(0, 2, 3), (1, 0, 2), (1, 2, 0), (1, 2, 3)}
def faces3(R, L):
    out = []
    for rows in itertools.combinations(range(R), 3):
        for labs in itertools.permutations(range(L), 3):
            if any(labs[i] == 0 and labs[j] == 1 for i in range(3) for j in range(i + 1, 3)) or labs in PAT3: continue
            out.append([r * L + c for r, c in zip(rows, labs)])
    return np.array(out, dtype=np.int64)
def bound(F, W):
    """W: M x v weights.  Returns #distinct (winner, heaviest cell) pairs."""
    Wf = W[:, F]                                   # M x g3 x 3
    top = Wf.argmax(axis=2); val = Wf.sum(axis=2) - Wf.max(axis=2)
    j = val.argmin(axis=0); z = F[np.arange(F.shape[0]), top[j, np.arange(F.shape[0])]]
    return len(np.unique(j * W.shape[1] + z))
ap = argparse.ArgumentParser(); ap.add_argument('--R', type=int, default=7); ap.add_argument('--L', type=int, default=5)
ap.add_argument('--trials', type=int, default=20); ap.add_argument('--seed', type=int, default=1); ap.add_argument('--out', required=True)
a = ap.parse_args(); R, L = a.R, a.L; v = R * L; F = faces3(R, L); g3 = len(F); cap = g3 / (v - 1)
rng = np.random.default_rng(a.seed); res = dict(R=R, L=L, g1=v, g3=g3, capacity=cap, runs=[])
rc = np.repeat(np.arange(R), L).astype(float); lc = np.tile(np.arange(L), R).astype(float)
for M in sorted({max(1, int(cap) // 2), int(cap), math.ceil(cap)}):
    target = min(g3, M * (v - 1))
    for fam in ('random', 'linear'):
        best = 0
        for _ in range(a.trials):
            if fam == 'random': W = rng.random((M, v))
            else: W = rng.normal(size=(M, 1)) * rc + rng.normal(size=(M, 1)) * lc + rng.normal(size=(M, 1)) * rc * lc + 1e-3 * rng.random((M, v))
            best = max(best, bound(F, W))
        res['runs'].append(dict(M=M, family=fam, target=target, best=best, fraction=best / target))
        print(f'R={R} L={L} M={M} {fam}: best {best} of {target} ({best/target:.3f})', flush=True)
json.dump(res, open(a.out, 'w'), indent=1)
