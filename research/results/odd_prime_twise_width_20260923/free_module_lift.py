"""Does the r-operator polarized lift hold on the free module kE = F_p[y_1..y_r]/(y_i^p)?
Closed tuples: z(u) = sum_{|a|=delta} u^a z_a with Theta_u z(u) = 0 identically, Theta_u = sum u_i y_i.
Lifts: z_a = multinomial(delta; a) y^a w.  Prints dim(closed tuples) and dim(lifts) for small p, r.
Pure linear algebra over F_p (exact)."""
import itertools, sys, json
import numpy as np
def rank_mod(A, p):
    A = A.copy() % p; r = 0; rows, cols = A.shape
    for c in range(cols):
        piv = next((i for i in range(r, rows) if A[i, c]), None)
        if piv is None: continue
        A[[r, piv]] = A[[piv, r]]; A[r] = (A[r] * pow(int(A[r, c]), p - 2, p)) % p
        nz = np.nonzero(A[:, c])[0]
        for i in nz:
            if i != r: A[i] = (A[i] - A[i, c] * A[r]) % p
        r += 1
        if r == rows: break
    return r
def run(p, r):
    delta = p - 1
    basis = list(itertools.product(range(p), repeat=r)); idx = {b: i for i, b in enumerate(basis)}; m = len(basis)
    def mult(i):  # matrix of multiplication by y_i
        Mx = np.zeros((m, m), dtype=np.int64)
        for b in basis:
            if b[i] + 1 < p:
                c = list(b); c[i] += 1; Mx[idx[tuple(c)], idx[b]] = 1
        return Mx
    Y = [mult(i) for i in range(r)]
    A = [a for a in itertools.product(range(delta + 1), repeat=r) if sum(a) == delta]
    B = [b for b in itertools.product(range(delta + 2), repeat=r) if sum(b) == delta + 1]
    # closedness: for each |b|=delta+1: sum_i sum_{a: a+e_i=b} Y_i z_a = 0
    Cl = np.zeros((len(B) * m, len(A) * m), dtype=np.int64)
    for bi, b in enumerate(B):
        for ai, a in enumerate(A):
            for i in range(r):
                if a[i] + 1 == b[i] and all(a[j] == b[j] for j in range(r) if j != i):
                    Cl[bi*m:(bi+1)*m, ai*m:(ai+1)*m] += Y[i]
    closed_dim = len(A) * m - rank_mod(Cl, p)
    from math import factorial
    L = np.zeros((len(A) * m, m), dtype=np.int64)
    for ai, a in enumerate(A):
        co = factorial(delta)
        for x in a: co //= factorial(x)
        P = np.eye(m, dtype=np.int64)
        for i in range(r):
            for _ in range(a[i]): P = P @ Y[i]
        L[ai*m:(ai+1)*m] = (co * P) % p
    lift_dim = rank_mod(L, p)
    return {'p': p, 'r': r, 'module_dim': m, 'closed_tuples': closed_dim, 'lifted_tuples': lift_dim}
out = [run(p, r) for p, r in [(2, 2), (2, 3), (3, 2), (3, 3), (3, 4), (5, 2), (5, 3)]]
for o in out: print(o)
json.dump(out, open(sys.argv[1], 'w'), indent=1)
