#!/usr/bin/env python3
"""Freeness of the atoms of the fibers' vanishing-top lattice at two holes (one row, p = 3), N = 12.

For a member Z on N = 12 holes and split holes 0, 1, the four fibers Z^{ab} give coefficient systems
A_t = A_2(Z^t) on the other 10 holes. For every nonempty T of fibers, X_T = cap_{t in T} A_t and
Y_T = sum_{t not in T} (X_T cap A_t). When the four systems are distributive (checked per link at
|S| <= 2 by distributivity_by_size.py), every sum-intersection word is an iterated extension of the
atoms X_T / Y_T, so freeness of all atoms through degree t gives freeness of every word.
Reported: short Jordan strings of r on each atom and on each X_T, degrees d <= 4 (the column tensor
powers on 8 holes are free below degree 4, so d <= 3 is in range and d = 4 is at its edge).
"""
import itertools, json, sys
import numpy as np
sys.path.insert(0, __file__.rsplit('/', 1)[0])
from vanishing_tops import rref3, rank3
from fiber_check import tops
from distributivity_check import inter

N, e, DMAX = 12, 2, 4
m = N + 1
rng = np.random.default_rng(20260925 + N)
phi = rng.integers(0, 3, size=(4, N)); phi[:, N - 1] = 0
form = lambda c, b: int(np.dot(phi[b], c) % 3)
clause = lambda c, i, S, k: form(c, i) == k[i] and all(form(c, j) != k[j] for j in S)
mem = {
    "two-block pair": lambda c: not clause(c, 0, [1], {0: 0, 1: 0}) and not clause(c, 0, [1], {0: 1, 1: 1}),
    "three clauses": lambda c: not clause(c, 0, [1], {0: 0, 1: 0}) and not clause(c, 2, [3], {2: 1, 3: 2})
                     and not clause(c, 1, [2], {1: 2, 2: 0}),
}
holes = [h for h in range(N) if h not in (0, 1)]


def assemble(sysfun):
    """Basis matrices B[d] (rows in tV_e coordinates on `holes`) and r matrices."""
    def coords(d):
        out = [(S, mu) for S in itertools.combinations(holes, d - e)
               for mu in itertools.combinations([h for h in holes if h not in S], e)]
        return out, {c: i for i, c in enumerate(out)}
    C = {d: coords(d) for d in range(e, DMAX + 3)}
    B = {}
    for d in range(e, DMAX + 3):
        idx = C[d][1]
        rows = []
        for S in itertools.combinations(holes, d - e):
            mus = list(itertools.combinations([h for h in holes if h not in S], e))
            for t in sysfun(S):
                v = np.zeros(len(idx), dtype=np.int64)
                for mu, cf in zip(mus, t):
                    if cf:
                        v[idx[(S, mu)]] = cf
                rows.append(v)
        B[d] = np.array(rows, dtype=np.int64).reshape(len(rows), len(idx))
    return C, B


def rmats(C):
    R = {}
    for d in range(e, DMAX + 2):
        src, sidx = C[d]; tgt, tidx = C[d + 1]
        M = np.zeros((len(src), len(tgt)), dtype=np.int64)
        for (S, mu), i in sidx.items():
            for h in holes:
                if h not in S and h not in mu:
                    M[i, tidx[(tuple(sorted(S + (h,))), mu)]] += 1
        R[d] = M % 3
    return R


def short_quotient(BX, BY, R):
    """Short strings of r on X/Y (Y subset X), degrees e..DMAX."""
    def dimq(d):
        return rank3(BX[d]) - (rank3(BY[d]) if len(BY[d]) else 0)
    def rk(d, power):
        img = BX[d]
        for k in range(power):
            img = img @ R[d + k] % 3 if len(img) else img
        tgt = d + power
        base = BY[tgt]
        both = rank3(np.vstack([base, img])) if len(base) and len(img) else (rank3(img) if len(img) else rank3(base) if len(base) else 0)
        return both - (rank3(base) if len(base) else 0)
    out = {}
    for d in range(e, DMAX + 1):
        out[d] = int(dimq(d) - rk(d, 1) - (rk(d - 2, 2) if d - 2 >= e else 0))
    return out


res = {}
for name, allowed in mem.items():
    pts = np.array([c for c in itertools.product((0, 1), repeat=N) if sum(c) % 3 == m % 3 and allowed(c)])
    fib = {(a, b): pts[(pts[:, 0] == a) & (pts[:, 1] == b)][:, holes] for a in (0, 1) for b in (0, 1)}
    cache = {}
    def sub(t, S):
        if (t, S) not in cache:
            Zf = fib[t]
            sel = Zf[np.all(Zf[:, [holes.index(h) for h in S]] == 1, axis=1)] if S else Zf
            rest = [h for h in holes if h not in S]
            cache[(t, S)] = tops(sel[:, [holes.index(h) for h in rest]], rest, e)[1]
        return cache[(t, S)]
    def X(T):
        def f(S):
            I = sub(T[0], S)
            for t in T[1:]:
                I = inter(I, sub(t, S))
            return I
        return f
    keys = list(fib)
    C = None
    out = {}
    for r_ in range(1, 5):
        for T in itertools.combinations(keys, r_):
            others = [t for t in keys if t not in T]
            def Y(S, T=T, others=others):
                parts = [inter(X(T)(S), sub(t, S)) for t in others]
                parts = [p for p in parts if len(p)]
                return rref3(np.vstack(parts))[0] if parts else np.zeros((0, X(T)(S).shape[1] if len(X(T)(S)) else len(list(itertools.combinations([h for h in holes if h not in S], e)))), dtype=np.int64)
            C, BX = assemble(X(T))
            _, BY = assemble(Y)
            R = rmats(C)
            atom = short_quotient(BX, BY, R)
            whole = short_quotient(BX, {d: np.zeros((0, BX[d].shape[1]), dtype=np.int64) for d in BX}, R)
            out[str(T)] = {'atom_short': atom, 'X_short': whole}
            print(name, T, 'atom', atom, 'X', whole, flush=True)
    res[name] = out
if '--out' in sys.argv:
    json.dump(res, open(sys.argv[sys.argv.index('--out') + 1], 'w'), indent=1)
