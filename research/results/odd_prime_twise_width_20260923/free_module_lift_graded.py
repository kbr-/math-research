"""Degree-resolved version of free_module_lift.py: for kE = F_p[y_1..y_r]/(y_i^p) graded by total degree,
closed tuples (z_a)_{|a|=p-1} in degree e versus lifts (multinomial * y^a w) with w of degree e-(p-1).
Also prints a basis of closed tuples modulo lifts (as monomial supports) for the smallest failing case."""
import itertools, sys, json
from math import factorial
import numpy as np
sys.path.insert(0, __file__.rsplit('/', 1)[0])
def rref_mod(A, p):
    A = A.copy() % p; r = 0; rows, cols = A.shape; piv = []
    for c in range(cols):
        pr = next((i for i in range(r, rows) if A[i, c]), None)
        if pr is None: continue
        A[[r, pr]] = A[[pr, r]]; A[r] = (A[r] * pow(int(A[r, c]), p - 2, p)) % p
        for i in np.nonzero(A[:, c])[0]:
            if i != r: A[i] = (A[i] - A[i, c] * A[r]) % p
        piv.append(c); r += 1
        if r == rows: break
    return A[:r], piv
def nullspace_mod(A, p):
    R, piv = rref_mod(A, p); n = A.shape[1]; free = [c for c in range(n) if c not in piv]; out = []
    for f in free:
        v = np.zeros(n, dtype=np.int64); v[f] = 1
        for i, c in enumerate(piv): v[c] = (-R[i, f]) % p
        out.append(v)
    return np.array(out, dtype=np.int64).reshape(len(out), n)
def run(p, r, show=False):
    d = p - 1
    mons = lambda e: [b for b in itertools.product(range(p), repeat=r) if sum(b) == e]
    A = [a for a in itertools.product(range(d + 1), repeat=r) if sum(a) == d]
    B = [b for b in itertools.product(range(d + 2), repeat=r) if sum(b) == d + 1]
    res = []
    for e in range(r * (p - 1) + 1):
        Me, Me1 = mons(e), mons(e + 1); ie = {b: i for i, b in enumerate(Me)}; ie1 = {b: i for i, b in enumerate(Me1)}
        if not Me: continue
        m, m1 = len(Me), len(Me1)
        Cl = np.zeros((len(B) * max(m1, 1), len(A) * m), dtype=np.int64)
        for bi, b in enumerate(B):
            for ai, a in enumerate(A):
                for i in range(r):
                    if a[i] + 1 == b[i] and all(a[j] == b[j] for j in range(r) if j != i):
                        for mono in Me:
                            if mono[i] + 1 < p:
                                c = list(mono); c[i] += 1
                                Cl[bi * m1 + ie1[tuple(c)], ai * m + ie[mono]] += 1
        closed = nullspace_mod(Cl, p) if m1 else np.eye(len(A) * m, dtype=np.int64)
        W = mons(e - d) if e >= d else []
        L = np.zeros((len(W), len(A) * m), dtype=np.int64)
        for wi, w in enumerate(W):
            for ai, a in enumerate(A):
                tgt = tuple(w[j] + a[j] for j in range(r))
                if all(x < p for x in tgt):
                    co = factorial(d)
                    for x in a: co //= factorial(x)
                    L[wi, ai * m + ie[tgt]] = co % p
        lr = len(rref_mod(L, p)[1]) if len(W) else 0
        row = {'degree': e, 'closed': int(closed.shape[0]), 'lifted': lr}
        res.append(row)
        if show and closed.shape[0] > lr:
            # a closed tuple outside the lifts
            Lr = rref_mod(L, p)[0] if len(W) else np.zeros((0, len(A) * m), dtype=np.int64)
            base = len(rref_mod(Lr, p)[1]) if len(Lr) else 0
            for v in closed:
                if len(rref_mod(np.vstack([Lr, v[None]]), p)[1]) > base:
                    terms = []
                    for ai, a in enumerate(A):
                        for mono in Me:
                            c = int(v[ai * m + ie[mono]])
                            if c: terms.append((a, mono, c))
                    row['witness'] = [[list(a), list(mn), c] for a, mn, c in terms]
                    print(f'  witness p={p} r={r} degree {e}:', terms)
                    break
    return {'p': p, 'r': r, 'by_degree': res}
if __name__ == '__main__':
  out = []
  for p, r in [(3, 3), (3, 4), (5, 3), (7, 3)]:
    o = run(p, r, show=(p, r) in [(3, 3), (5, 3)])
    print(p, r, [(x['degree'], x['closed'], x['lifted']) for x in o['by_degree'] if x['closed'] != x['lifted']])
    out.append(o)
  json.dump(out, open(sys.argv[1], 'w'), indent=1)
