"""Check of the spare-label lemma on one t-set of rows of the functional board.

Statement tested: with N labels (label N-1 eliminated, y-labels 0..N-2) and a label set X of y-labels with |X| >= t,
the t-matchings with labels < N-1 and at most one label in X are linearly independent in G_t.
Dually (G_t = K_t^*, K_t = zero-marginal arrays on injective labelings, y_m = evaluation at m): the projection of
K_t = ker C onto the family coordinates F is surjective, i.e. rank C[:, not F] == rank C.  One row set suffices,
since G_t splits over t-sets of rows.  Controls: |X| = t-1 (the lemma's proof needs |X| >= t) and the family of all
matchings with labels < N-1 (dependent, since dim K_t < (N-1)_t)."""
import itertools, json, sys, numpy as np

def rank3(A):
    A = A.copy() % 3; r = 0; rows, cols = A.shape
    for c in range(cols):
        p = np.nonzero(A[r:, c])[0]
        if len(p) == 0: continue
        p = p[0] + r; A[[r, p]] = A[[p, r]]
        A[r] = (A[r] * (1 if A[r, c] == 1 else 2)) % 3
        nz = np.nonzero(A[:, c])[0]; nz = nz[nz != r]
        A[nz] = (A[nz] - np.outer(A[nz, c], A[r])) % 3
        r += 1
        if r == rows: break
    return r

def check(t, N, X, allm=False):
    tup = list(itertools.permutations(range(N), t)); idx = {m: i for i, m in enumerate(tup)}
    C = []
    for r in range(t):
        for rest in itertools.permutations(range(N), t - 1):
            row = np.zeros(len(tup), dtype=np.int64)
            for c in range(N):
                if c in rest: continue
                m = rest[:r] + (c,) + rest[r:]; row[idx[m]] = 1
            C.append(row)
    C = np.array(C)
    fam = lambda m: (N - 1) not in m and (allm or sum(1 for c in m if c in X) <= 1)
    F = [i for i, m in enumerate(tup) if fam(m)]; nF = [i for i in range(len(tup)) if i not in set(F)]
    rc = rank3(C); rn = rank3(C[:, nF])
    return dict(t=t, N=N, X='all' if allm else sorted(X), family=len(F), dimK=len(tup) - rc, independent=bool(rn == rc))

out = []
for t, N in [(3, 6), (3, 7), (4, 8), (4, 9)]:
    out.append(check(t, N, set(range(t))))          # the lemma's case |X| = t
    out.append(check(t, N, set(range(t - 1))))      # control |X| = t-1
    out.append(check(t, N, set(), allm=True))      # control: all matchings
    print(*(json.dumps(o) for o in out[-3:]), flush=True)
json.dump(out, open(sys.argv[1], 'w'), indent=1)
