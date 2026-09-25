#!/usr/bin/env python3
"""Fiber uniformity at a free hole against the transfer hypothesis, column members, N = 12, p = 3.

Statement under test (conj:free-hole-good, cor:free-hole-uniformity): at a hole j outside every form's
support, the two fibers Z^0, Z^1 of a member Z = {c in the slice : l(c) in Omega} have equal vanishing
tops a_{S,e} on every link S.  cor:free-hole-uniformity proves this on every link whose cube
Gamma = gr F^{{0,1}^{H'}} (H' = the link's holes) contains a free T_R-submodule agreeing with it in
degrees <= e, where T_R = F_3[w_0..w_r]/(w^3) acts through the tops of (s, l_b), l_b the forms the
member uses (hypothesis (H)).  (H) holds iff T_R * Gamma_{<=e} is free; tested by comparing dimensions
of T_R * Gamma_{<=e} with sum_k g_k t_{d-k} in every degree up to e + 2(r+1).
For every link |S| <= 2 and e = 1, 2 this records (H) and fiber equality.  The theorem predicts no link
with (H) and unequal fibers; the open question is whether fibers are equal where (H) fails.
Forms: those of two_step.py (seed 20260925 + N, hole N-1 free; dense variant with l_0 nonzero off it).
"""
import itertools, json, sys
from math import comb
import numpy as np
here = __file__.rsplit('/', 1)[0]
sys.path.insert(0, here + '/../odd_prime_closure_route_review_20260925')
from vanishing_tops import rank3
from fiber_check import tops

N = 12; m = N + 1; J = N - 1; H = list(range(N - 1))


def forms(dense):
    rng = np.random.default_rng(20260925 + N)
    phi = rng.integers(0, 3, size=(4, N))
    if dense:
        phi[0] = rng.integers(1, 3, size=N)
    phi[:, N - 1] = 0
    return phi


def t_hilbert(r):
    """Hilbert function of F[w_1..w_r]/(w^3)."""
    h = np.array([1])
    for _ in range(r):
        h = np.convolve(h, [1, 1, 1])
    return h


def mult(vec, holes, d):
    """Matrix of multiplication by sum_h vec[h] C_h from Gamma_d to Gamma_{d+1} on the given holes."""
    src = list(itertools.combinations(holes, d)); tgt = {mu: i for i, mu in enumerate(itertools.combinations(holes, d + 1))}
    M = np.zeros((len(src), len(tgt)), dtype=np.int64)
    for i, mu in enumerate(src):
        for h in holes:
            if h not in mu and vec[h] % 3:
                M[i, tgt[tuple(sorted(mu + (h,)))]] = vec[h] % 3
    return M


def hypothesis(vecs, holes, e):
    """Is T_R * Gamma_{<=e} free over T_R (T_R acting by the vecs' linear forms)?"""
    n = len(holes); r = len(vecs); t = t_hilbert(r); top = min(e + 2 * r, n)
    g = {0: 1}; U = np.eye(1, dtype=np.int64)                  # U = basis rows of Phi_{d} (d = 0)
    for d in range(1, e + 2 * r + 1):
        if d > n:
            return all(sum(g[k] * (t[d2 - k] if 0 <= d2 - k < len(t) else 0) for k in g) == 0
                       for d2 in range(d, e + 2 * r + 1))
        rows = [U @ mult(v, holes, d - 1) % 3 for v in vecs] if len(U) else []
        W = np.vstack(rows) % 3 if rows else np.zeros((0, comb(n, d)), dtype=np.int64)
        w = rank3(W) if len(W) else 0
        pred = sum(g[k] * (t[d - k] if d - k < len(t) else 0) for k in g)
        if w != pred:
            return False
        if d <= e:
            g[d] = comb(n, d) - w; U = np.eye(comb(n, d), dtype=np.int64)
        else:
            U = W
    return True


def main():
    phis = {'sparse': forms(False), 'dense': forms(True)}
    def clause(phi, c, i, S, k):
        f = lambda b: int(np.dot(phi[b], c) % 3)
        return f(i) == k[i] and all(f(jj) != k[jj] for jj in S)
    members = {
        'one clause, sparse': ('sparse', [0, 1], lambda p, c: not clause(p, c, 0, [1], {0: 0, 1: 0})),
        'two-block pair, sparse': ('sparse', [0, 1], lambda p, c: not clause(p, c, 0, [1], {0: 0, 1: 0})
                                   and not clause(p, c, 0, [1], {0: 1, 1: 1})),
        'two-block pair, dense': ('dense', [0, 1], lambda p, c: not clause(p, c, 0, [1], {0: 0, 1: 0})
                                  and not clause(p, c, 0, [1], {0: 1, 1: 1})),
        'three clauses, sparse': ('sparse', [0, 1, 2, 3], lambda p, c: not clause(p, c, 0, [1], {0: 0, 1: 0})
                                  and not clause(p, c, 2, [3], {2: 1, 3: 2}) and not clause(p, c, 1, [2], {1: 2, 2: 0})),
    }
    out = {}
    for name, (kind, used, allowed) in members.items():
        phi = phis[kind]
        pts = np.array([c for c in itertools.product((0, 1), repeat=N) if sum(c) % 3 == m % 3 and allowed(phi, c)])
        Z = {a: pts[pts[:, J] == a][:, H] for a in (0, 1)}
        res = {}
        for e in (1, 2):
            tab = {}
            for ssz in (0, 1, 2):
                cnt = {'H and equal': 0, 'H and unequal': 0, 'no H, equal': 0, 'no H, unequal': 0}
                for S in itertools.combinations(H, ssz):
                    rest = [h for h in H if h not in S]
                    T = []
                    for a in (0, 1):
                        sel = Z[a][np.all(Z[a][:, list(S)] == 1, axis=1)] if S else Z[a]
                        T.append(tops(sel[:, rest], rest, e)[1])
                    A, B = T
                    ra, rb = (rank3(A) if len(A) else 0), (rank3(B) if len(B) else 0)
                    both = rank3(np.vstack([A, B])) if ra + rb else 0
                    equal = ra == rb == both
                    vecs = [np.ones(N, dtype=np.int64)] + [phi[b] for b in used]
                    hyp = hypothesis(vecs, rest, e)
                    cnt[('H and ' if hyp else 'no H, ') + ('equal' if equal else 'unequal')] += 1
                tab[ssz] = cnt
                print(name, 'e', e, '|S|', ssz, cnt, flush=True)
            res[e] = tab
        out[name] = {'forms_used': used, 'points': int(len(pts)), 'by_e_and_link_size': res}
    if '--out' in sys.argv:
        json.dump({'phi_sparse': phis['sparse'].tolist(), 'phi_dense': phis['dense'].tolist(), 'results': out},
                  open(sys.argv[sys.argv.index('--out') + 1], 'w'), indent=1)


if __name__ == '__main__':
    main()
