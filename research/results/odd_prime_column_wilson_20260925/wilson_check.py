"""Exact F_3 check of the two square-free kernel identities used by thm:column-wilson-taylor.

On Lambda_m (square-free algebra on m cells), l = sum of the cells: ker(l^2 on Lambda_j) = l Lambda_{j-1} for
m >= 2j+2, and ker(l on Lambda_j) = l^2 Lambda_{j-2} for m >= 2j+1 (from Wilson's rank formula).  Checked by
dimensions (dim ker = dim image, the image being contained in the kernel since l^3 = 0) for m <= 12, all j; also
reports where each identity fails (sharpness)."""
import itertools, json, sys
import numpy as np
def rank3(M):
    M = M.copy() % 3; r = 0
    for c in range(M.shape[1]):
        nz = np.nonzero(M[r:, c])[0]
        if len(nz) == 0: continue
        p = r + nz[0]; M[[r, p]] = M[[p, r]]
        if M[r, c] == 2: M[r] = (2 * M[r]) % 3
        o = np.nonzero(M[:, c])[0]; o = o[o != r]
        M[o] = (M[o] - np.outer(M[o, c], M[r])) % 3
        r += 1
        if r == M.shape[0]: break
    return r
def incl(m, a, b, coef=1):
    A = list(itertools.combinations(range(m), a)); B = list(itertools.combinations(range(m), b))
    bi = {s: i for i, s in enumerate(B)}; M = np.zeros((len(A), len(B)), dtype=np.int64)
    for i, s in enumerate(A):
        for extra in itertools.combinations([x for x in range(m) if x not in s], b - a):
            M[i, bi[tuple(sorted(s + extra))]] = coef
    return M
res = []
for m in range(1, 13):
    for j in range(0, m + 1):
        from math import comb
        rk2 = rank3(incl(m, j, j + 2, 2)) if j + 2 <= m else 0
        im1 = rank3(incl(m, j - 1, j)) if j >= 1 else 0
        id1 = (comb(m, j) - rk2) == im1
        rk1 = rank3(incl(m, j, j + 1)) if j + 1 <= m else 0
        im2 = rank3(incl(m, j - 2, j, 2)) if j >= 2 else 0
        id2 = (comb(m, j) - rk1) == im2
        res.append(dict(m=m, j=j, ker_l2_eq_lL=id1, ker_l_eq_l2L=id2))
ok1 = all(r['ker_l2_eq_lL'] for r in res if r['m'] >= 2 * r['j'] + 2)
ok2 = all(r['ker_l_eq_l2L'] for r in res if r['m'] >= 2 * r['j'] + 1)
sharp1 = all(not r['ker_l2_eq_lL'] for r in res if r['m'] == 2 * r['j'] + 1 and r['j'] >= 1)
sharp2 = all(not r['ker_l_eq_l2L'] for r in res if r['m'] == 2 * r['j'] and r['j'] >= 1)
out = dict(checked='m <= 12, all j', identity1_holds_in_range=ok1, identity2_holds_in_range=ok2, identity1_fails_at_m_eq_2j_plus_1=sharp1, identity2_fails_at_m_eq_2j=sharp2)
print(json.dumps(out)); json.dump(dict(summary=out, rows=res), open(sys.argv[1], 'w'), indent=1)
