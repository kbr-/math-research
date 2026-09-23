"""One row triple (rows a<b<c = 0,1,2), labels 0..L-1: the degree-3 part Q_3 of the ideal of the quadrics
q_rs = sum_{c != c'} y_{r,c} y_{s,c'} in the matching space.  Monomials = injective label tuples (f0,f1,f2); lex order:
smaller tuple = larger monomial, so the leading term of an element is its smallest tuple.  Spanning set: q_01*y_{2,d},
q_02*y_{1,d}, q_12*y_{0,d}.  Prints the fully reduced echelon rows whose pivot is not a multiple of a degree-2 leading
term {(r,0),(s,1)}, with their full support, to find elements uniform in L.  Tiny sizes: Python elimination suffices.
Usage: python3 triple.py --Ls 4,5,6,7 --out OUT.json"""
import argparse, itertools, json
import numpy as np
def rref3(M):
    M = M.copy() % 3; piv = []; r = 0
    for c in range(M.shape[1]):
        nz = np.nonzero(M[r:, c])[0]
        if len(nz) == 0: continue
        k = r + nz[0]; M[[r, k]] = M[[k, r]]; M[r] = (M[r] * (1 if M[r, c] == 1 else 2)) % 3
        others = np.nonzero(M[:, c])[0]; others = others[others != r]
        M[others] = (M[others] - np.outer(M[others, c], M[r])) % 3; piv.append(c); r += 1
        if r == M.shape[0]: break
    return M[:r], piv
ap = argparse.ArgumentParser(); ap.add_argument('--Ls', default='4,5,6,7'); ap.add_argument('--out', required=True); a = ap.parse_args(); res = []
for L in map(int, a.Ls.split(',')):
    tup = sorted(itertools.permutations(range(L), 3)); idx = {t: i for i, t in enumerate(tup)}
    gens, names = [], []
    for (p, q, o) in ((0, 1, 2), (0, 2, 1), (1, 2, 0)):       # q_{pq} * y_{o,d}
        for d in range(L):
            v = np.zeros(len(tup), dtype=np.int64)
            for c1, c2 in itertools.permutations(range(L), 2):
                f = [None] * 3; f[p], f[q], f[o] = c1, c2, d
                if len(set(f)) == 3: v[idx[tuple(f)]] += 1
            gens.append(v % 3); names.append(f'q{p}{q}*y{o},{d}')
    E, piv = rref3(np.array(gens))
    lead2 = lambda t: any(t[i] == 0 and t[j] == 1 for i in range(3) for j in range(i + 1, 3))
    extra = [(tup[pv], {str(tup[k]): int(E[i, k]) for k in np.nonzero(E[i])[0]}) for i, pv in enumerate(piv) if not lead2(tup[pv])]
    res.append(dict(L=L, dim_Q3=len(piv), extra_pivots=[e[0] for e in extra], supports=[len(e[1]) for e in extra]))
    print(f'L={L}: dim Q3 {len(piv)} (expected {3*L-2}), extra leading terms {[e[0] for e in extra]}, support sizes {[len(e[1]) for e in extra]}', flush=True)
    if L <= 5:
        for lt, sup in extra: print('   ', lt, sup)
json.dump(res, open(a.out, 'w'), indent=1)
