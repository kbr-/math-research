#!/usr/bin/env python3
"""Route review of the closure recursion line: falsification attempt and lead tests, p = 3.

T1 (conj:good-column, falsification): a two-block pair whose forms leave no free hole (l_0 nonzero on
   every hole), N = 12, e = 2: for every hole j, count links |S| <= 2 where a_S(Z^0_j) is not contained
   in a_S(Z^1_j), split by |S|.  The conjecture needs some hole with no failing link.
T2 (Fourier bias lead): for the dense pair of transfer_vs_uniformity.py (hole 11 free), per link |S| <= 2,
   e = 2: fiber-top equality against the bias beta_S = max over u != 0 in F_3^2 and c != 0 of
   #{h in link holes : u . phi(h) = c}, the exponent that governs |Z'_a| - |Z'_{a-1}| by character sums.
   Also the fiber sizes |Z'_a|, a = 0, 1, 2, on the 11 holes, for the random and dense pairs.
T3 (squarefree Groebner degeneration lead): for one clause at N = 10 (fiber_check.py's forms), ranks of
   s and s^2 per degree <= 4 on gr F^Z against its degree-lex initial monomial algebra.
B2 (linked-cluster bridge): Hilbert functions through degree 4 of the slice (N = 12), two clauses A, B
   and their intersection; tests H(A and B) * H(slice) = H(A) * H(B) as truncated power series, for
   clauses on disjoint supports (holes 0-5, 6-11) and on dense overlapping forms.
"""
import itertools, json, sys
from math import comb
import numpy as np
here = __file__.rsplit('/', 1)[0]
sys.path.insert(0, here + '/../odd_prime_closure_route_review_20260925')
from vanishing_tops import rank3, rref3
from fiber_check import tops

P = 3


def clause_fn(phi, i, S, k):
    return lambda c: int(np.dot(phi[i], c) % 3) == k[i] and all(int(np.dot(phi[j], c) % 3) != k[j] for j in S)


def slice_pts(N, m, allowed):
    return np.array([c for c in itertools.product((0, 1), repeat=N) if sum(c) % 3 == m % 3 and allowed(c)])


def contained(A, B):
    if len(A) == 0: return True
    if len(B) == 0: return False
    return rank3(np.vstack([A, B])) == rank3(B)


def equal(A, B):
    return contained(A, B) and contained(B, A)


def link_tops(Zf, hs, S, e):
    rest = [h for h in hs if h not in S]
    sel = Zf[np.all(Zf[:, [hs.index(h) for h in S]] == 1, axis=1)] if S else Zf
    return tops(sel[:, [hs.index(h) for h in rest]], rest, e)[1]


def t1():
    N, m, e = 12, 13, 2
    rng = np.random.default_rng(20260926)
    phi = rng.integers(0, 3, size=(2, N)); phi[0] = rng.integers(1, 3, size=N)
    allowed = lambda c: not clause_fn(phi, 0, [1], {0: 0, 1: 0})(c) and not clause_fn(phi, 0, [1], {0: 1, 1: 1})(c)
    pts = slice_pts(N, m, allowed)
    res = {}
    for j in range(N):
        hs = [h for h in range(N) if h != j]
        Z0 = pts[pts[:, j] == 0][:, hs]; Z1 = pts[pts[:, j] == 1][:, hs]
        fails = {0: 0, 1: 0, 2: 0}
        for ssz in (0, 1, 2):
            for S in itertools.combinations(hs, ssz):
                if not contained(link_tops(Z0, hs, S, e), link_tops(Z1, hs, S, e)):
                    fails[ssz] += 1
        res[j] = fails
        print('T1 hole', j, fails, flush=True)
    return {'phi': phi.tolist(), 'points': int(len(pts)), 'fails_by_hole': res,
            'good_columns': [j for j, f in res.items() if sum(f.values()) == 0]}


def forms12(dense):
    N = 12
    rng = np.random.default_rng(20260925 + N)
    phi = rng.integers(0, 3, size=(4, N))
    if dense:
        phi[0] = rng.integers(1, 3, size=N)
    phi[:, N - 1] = 0
    return phi


def bias(phi, used, holes):
    best = 0
    for u in itertools.product(range(3), repeat=len(used)):
        if not any(u):
            continue
        vals = [int(sum(ui * phi[b][h] for ui, b in zip(u, used)) % 3) for h in holes]
        best = max(best, max(vals.count(1), vals.count(2)))
    return best


def t2():
    N, m, e, J = 12, 13, 2, 11
    H = list(range(N - 1))
    out = {}
    for kind in ('random', 'dense'):
        phi = forms12(kind == 'dense')
        allowed = lambda c: not clause_fn(phi, 0, [1], {0: 0, 1: 0})(c) and not clause_fn(phi, 0, [1], {0: 1, 1: 1})(c)
        full = np.array([c for c in itertools.product((0, 1), repeat=N - 1)
                         if allowed(np.array(list(c) + [0]))])
        sizes = {a: int(np.sum(full.sum(axis=1) % 3 == a)) for a in range(3)}
        rec = {'fiber_sizes_by_residue': sizes}
        if kind == 'dense':
            pts = slice_pts(N, m, allowed)
            Z0 = pts[pts[:, J] == 0][:, H]; Z1 = pts[pts[:, J] == 1][:, H]
            rows = []
            for ssz in (0, 1, 2):
                for S in itertools.combinations(H, ssz):
                    rest = [h for h in H if h not in S]
                    eq = equal(link_tops(Z0, H, S, e), link_tops(Z1, H, S, e))
                    rows.append({'S': list(S), 'equal': bool(eq), 'bias': bias(phi, [0, 1], rest)})
            rec['links'] = rows
            for ssz in (1, 2):
                for eq in (True, False):
                    bs = [r['bias'] for r in rows if len(r['S']) == ssz and r['equal'] == eq]
                    print('T2', kind, '|S|', ssz, 'equal' if eq else 'unequal', 'bias values', sorted(set(bs)), 'count', len(bs), flush=True)
        print('T2', kind, 'sizes', sizes, flush=True)
        out[kind] = rec
    return out


def t3():
    N, m = 10, 11
    rng = np.random.default_rng(20260925)
    phi = rng.integers(0, 3, size=(4, N)); phi[:, 9] = 0
    pts = slice_pts(N, m, lambda c: not clause_fn(phi, 0, [1], {0: 0, 1: 0})(c))
    holes = list(range(N)); DM = 4
    mons = {d: list(itertools.combinations(holes, d)) for d in range(DM + 2)}
    order = [mu for d in range(DM + 2) for mu in mons[d]]
    E = np.array([[int(all(p[h] for h in mu)) for mu in order] for p in pts], dtype=np.int64)
    _, piv = rref3(E)
    std = set(order[i] for i in piv)
    def smat(d):
        idx = {mu: i for i, mu in enumerate(mons[d + 1])}
        M = np.zeros((len(mons[d]), len(mons[d + 1])), dtype=np.int64)
        for i, mu in enumerate(mons[d]):
            for h in holes:
                if h not in mu:
                    M[i, idx[tuple(sorted(mu + (h,)))]] = 1
        return M
    S = {d: smat(d) for d in range(DM + 1)}
    A = {d: tops(pts, holes, d)[1] for d in range(DM + 2)}
    res = {}
    for d in range(DM):
        def qrank(M, tgt):
            base = rank3(A[tgt]) if len(A[tgt]) else 0
            X = np.vstack([A[tgt], M % 3]) if len(A[tgt]) else M % 3
            return rank3(X) - base
        g1, g2 = qrank(S[d], d + 1), qrank(S[d] @ S[d + 1], d + 2)
        sd = [i for i, mu in enumerate(mons[d]) if mu in std]
        s1 = [i for i, mu in enumerate(mons[d + 1]) if mu in std]
        s2 = [i for i, mu in enumerate(mons[d + 2]) if mu in std]
        M1 = S[d][np.ix_(sd, s1)]; M2 = S[d + 1][np.ix_(s1, s2)]
        m1 = rank3(M1) if M1.size else 0; m2 = rank3(M1 @ M2 % 3) if M1.size and M2.size else 0
        hilb = (comb(N, d) - (rank3(A[d]) if len(A[d]) else 0), len(sd))
        res[d] = {'hilbert_gr_vs_initial': hilb, 'rank_s_gr': g1, 'rank_s_initial': m1,
                  'rank_s2_gr': g2, 'rank_s2_initial': m2}
        print('T3 degree', d, res[d], flush=True)
    return res


def hilbert(pts, N, DM):
    out = []
    prev = 0
    for d in range(DM + 1):
        order = [mu for k in range(d + 1) for mu in itertools.combinations(range(N), k)]
        E = np.array([[int(all(p[h] for h in mu)) for mu in order] for p in pts], dtype=np.int64)
        r = rank3(E)
        out.append(r - prev); prev = r
    return out


def b2():
    N, m, DM = 12, 13, 4
    rng = np.random.default_rng(20260927)
    out = {}
    for kind in ('disjoint', 'dense overlapping'):
        phi = rng.integers(1, 3, size=(4, N))
        if kind == 'disjoint':
            phi[0:2, 6:] = 0; phi[2:4, :6] = 0
        A = lambda c: not clause_fn(phi, 0, [1], {0: 0, 1: 0})(c)
        B = lambda c: not clause_fn(phi, 2, [3], {2: 0, 3: 0})(c)
        Hs = {name: hilbert(slice_pts(N, m, f), N, DM) for name, f in
              (('slice', lambda c: True), ('A', A), ('B', B), ('A and B', lambda c: A(c) and B(c)))}
        lhs = np.convolve(Hs['A and B'], Hs['slice'])[:DM + 1].tolist()
        rhs = np.convolve(Hs['A'], Hs['B'])[:DM + 1].tolist()
        out[kind] = {'hilbert': Hs, 'H(AB)H(slice)': lhs, 'H(A)H(B)': rhs, 'identity_holds_through': next(
            (d - 1 for d in range(DM + 1) if lhs[d] != rhs[d]), DM)}
        print('B2', kind, out[kind], flush=True)
    return out


def main():
    res = {'T2': t2(), 'T3': t3(), 'B2': b2(), 'T1': t1()}
    if '--out' in sys.argv:
        json.dump(res, open(sys.argv[sys.argv.index('--out') + 1], 'w'), indent=1)


if __name__ == '__main__':
    main()
