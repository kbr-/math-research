"""Hub criterion (H) of the clause hub criterion theorem, checked against the full Singular computations.

Theorem (exact form): a hub-private clause family F is t-local at full closure (every consequence derived at its own
degree from full closures of subfamilies of t blocks) iff for every set O of blocks and every degree s,
    I(V_O)_{<=s} = sum over O' subset of O, |O'| = min(t,|O|), of I(V_O')_{<=s}
in the hub function ring F_3[v]/(v^3 - v), where V_O is the set of hub points outside every active set A_b, b in O,
and I(V)_{<=s} is the space of functions vanishing on V that have a representative of degree <= s.
This script computes the least such t for each family of covering_numbers.py, using only the hub ring (at most 81
points), and prints it next to the least t measured by the full computation in clause_locality*.out and
clause_points.out.  Equality in every family is the prediction.
"""
import itertools, os, sys
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import importlib.util
spec = importlib.util.spec_from_file_location('cn', os.path.join(os.path.dirname(os.path.abspath(__file__)), 'covering_numbers.py'))

def rank3(M):
    M = M.copy() % 3; r = 0; rows, cols = M.shape
    for c in range(cols):
        nz = np.nonzero(M[r:, c])[0]
        if nz.size == 0: continue
        piv = r + nz[0]
        M[[r, piv]] = M[[piv, r]]
        M[r] = (M[r] * M[r, c]) % 3          # 1*1=1, 2*2=4=1: scaling by the pivot inverts it over F_3
        f = M[:, c].copy(); f[r] = 0
        M = (M - np.outer(f, M[r])) % 3      # vectorized elimination of column c from every other row
        r += 1
        if r == rows: break
    return r

def kernel_basis(E):
    # basis (rows) of {x : E x = 0} over F_3, E of shape (k, n)
    k, n = E.shape
    M = E.copy() % 3; piv = []; r = 0
    for c in range(n):
        nz = np.nonzero(M[r:, c])[0]
        if nz.size == 0: continue
        p = r + nz[0]
        M[[r, p]] = M[[p, r]]; M[r] = (M[r] * M[r, c]) % 3
        f = M[:, c].copy(); f[r] = 0
        M = (M - np.outer(f, M[r])) % 3
        piv.append(c); r += 1
        if r == k: break
    free = [c for c in range(n) if c not in piv]
    B = []
    for f in free:
        x = np.zeros(n, dtype=np.int64); x[f] = 1
        for i, c in enumerate(piv): x[c] = (-M[i, f]) % 3
        B.append(x)
    return np.array(B, dtype=np.int64).reshape(len(B), n)

def least_t(A, d):
    P = list(itertools.product(range(3), repeat=d))
    mons = list(itertools.product(range(3), repeat=d))            # reduced monomials, exponents 0..2
    ev = np.array([[int(np.prod([v[i] ** e[i] if e[i] else 1 for i in range(d)])) % 3 for e in mons] for v in P], dtype=np.int64)
    deg = np.array([sum(e) for e in mons])
    m = len(A)
    def V(O):
        U = set().union(*(A[i] for i in O)) if O else set()
        return [j for j, v in enumerate(P) if v not in U]
    cache = {}
    def I(O, s):
        key = (O, s)
        if key not in cache:
            cols = np.where(deg <= s)[0]
            rows = V(O)
            if rows:
                K = kernel_basis(ev[np.ix_(rows, cols)])
            else:
                K = np.eye(len(cols), dtype=np.int64)
            full = np.zeros((K.shape[0], len(mons)), dtype=np.int64); full[:, cols] = K
            cache[key] = full
        return cache[key]
    maxdeg = 2 * d
    for t in range(1, m + 1):
        ok = True
        for r in range(t + 1, m + 1):
            for O in itertools.combinations(range(m), r):
                for s in range(maxdeg + 1):
                    target = rank3(I(O, s)) if I(O, s).shape[0] else 0
                    parts = [I(Op, s) for Op in itertools.combinations(O, t)]
                    S = np.vstack([p for p in parts if p.shape[0]]) if any(p.shape[0] for p in parts) else np.zeros((0, len(mons)), dtype=np.int64)
                    got = rank3(S) if S.shape[0] else 0
                    if got != target: ok = False; break
                if not ok: break
            if not ok: break
        if ok: return t
    return m

if __name__ == '__main__':
    import contextlib, io
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        hn = importlib.util.module_from_spec(spec); spec.loader.exec_module(hn)
    print('family  covering_number  hub_criterion_t  measured_t')
    for nm, (fm, names) in hn.F.items():
        A = [hn.active(b, len(names)) for b in fm]
        print(f'{nm:6s}  {hn.covering(A):15d}  {least_t(A, len(names)):15d}  {hn.measured.get(nm, "?"):>10}', flush=True)
