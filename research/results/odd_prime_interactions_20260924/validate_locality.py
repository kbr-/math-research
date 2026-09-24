"""Cross-validation: pair defects from the rank formula r(UuW)-r(U)-r(W)+r(UnW) (mv_locality.py's method) against the
nullspace sums dim I(UnW) - dim(I(U)+I(W)) (triple_locality.py's method), on the triple script's forms, and a check of
the degree-shift bound I_d(UnW) within I_{d+2}(U) + I_{d+2}(W) (p=3, selectors, shift p-1).
Usage: python3 validate_locality.py OUT.json N:dmax:m:seed [...]"""
import itertools, json, random, sys
import numpy as np
sys.argv, args = sys.argv[:1] + ['/dev/null'], sys.argv[1:]
exec(open(__file__.replace('validate_locality.py', 'triple_locality.py')).read().split('out = sys.argv[1]')[0])
out = args[0]; res = []
for case in args[1:]:
    N, dmax, m, seed = map(int, case.split(':')); rnd = random.Random(seed); L = []
    while len(L) < 3:
        f = [rnd.randrange(1, p) for _ in range(N)]
        if len(set(f)) > 1: L.append((f, rnd.randrange(p)))
    pts = [c for c in itertools.product((0, 1), repeat=N) if sum(c) % p == m % p]
    ok = lambda c, i: sum(a * x for a, x in zip(L[i][0], c)) % p != L[i][1]
    def mons(d): return [T for e in range(d + 1) for T in itertools.combinations(range(N), e)]
    def ev(X, d): return np.array([[int(all(c[j] for j in T)) for c in X] for T in mons(d)], dtype=np.int64)
    for d in range(2, dmax + 1):
        for a, b in [(0, 1), (0, 2), (1, 2)]:
            U = [c for c in pts if ok(c, a)]; W = [c for c in pts if ok(c, b)]
            UW = [c for c in pts if ok(c, a) or ok(c, b)]; UnW = [c for c in U if ok(c, b)]
            rk = rank(ev(UW, d)) - rank(ev(U, d)) - rank(ev(W, d)) + rank(ev(UnW, d))
            ns = len(null_left(ev(UnW, d))) - rank(np.vstack([null_left(ev(U, d)), null_left(ev(W, d))]))
            # shift bound: pad degree-d nullspace of UnW into degree d+2 monomial coordinates
            Md, Ms = mons(d), mons(d + 2); idx = {T: i for i, T in enumerate(Ms)}
            Inn = null_left(ev(UnW, d)); pad = np.zeros((len(Inn), len(Ms)), dtype=np.int64)
            for i, T in enumerate(Md): pad[:, idx[T]] = Inn[:, i]
            S2 = np.vstack([null_left(ev(U, d + 2)), null_left(ev(W, d + 2))]) if d + 2 <= N else None
            shift_ok = rank(np.vstack([S2, pad])) == rank(S2)
            row = dict(case=case, d=d, pair=f'{a}{b}', defect_rank=rk, defect_nullspace=-ns, shift_bound_holds=bool(shift_ok))
            res.append(row); print(json.dumps(row), flush=True); json.dump(res, open(out, 'w'), indent=1)
