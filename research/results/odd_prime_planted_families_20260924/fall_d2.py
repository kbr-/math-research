"""Degree-2 falls of the weak base plus selector families, by direct linear algebra over F_3.

Tested statement: the weak unary base (m rows, N holes) plus M selectors 1 - (l_t - v_t)^2 (l_t uniform random
row-dependent forms) is z-injective below 2, i.e. ker_z(1) = dim(V_2 cap P_<=1) - dim V_1 = 0 and ker_z(0) = 0, where V_k is
the span of NS multiples of degree <= k. Coordinates: multilinear monomials of degree <= 2 with no two cells in one column
(Booleanity x^2 - x and column exclusions are degree-2 generators, so reducing modulo them stays inside V_2). V_2 is spanned
by the reduced selectors and (r_i - 1) * m, deg m <= 1; V_1 by the r_i - 1. dim(V_2 cap P_<=1) = rank V_2 - rank of its
degree-2 part. 'psel<M>': planted, v_t != l_t(x*) for the matching x* (row i in hole i), so satisfiable; 'gsel<M>': random v.
Selectors are generated with the same random stream as planted_fall.py, so seeds match its cases.
Usage: python3 fall_d2.py OUT.json m:N:seed:member ..."""
import json, random, sys, time
import numpy as np
p = 3

def rank_mod3(M):
    """Rank over F_3 by vectorized elimination (one Python iteration per pivot column)."""
    M = (M % p).astype(np.int8); r = 0; rows, cols = M.shape
    for c in range(cols):
        if r == rows: break
        nz = np.nonzero(M[r:, c])[0]
        if len(nz) == 0: continue
        piv = r + nz[0]
        if piv != r: M[[r, piv]] = M[[piv, r]]
        if M[r, c] == 2: M[r] = (M[r] * 2) % p
        below = np.nonzero(M[:, c])[0]; below = below[below != r]
        if len(below): M[below] = (M[below] - np.outer(M[below, c], M[r])) % p
        r += 1
    return r

out = sys.argv[1]; res = []
for case in sys.argv[2:]:
    m, N, seed, member = case.split(':'); m, N, seed = int(m), int(N), int(seed); rnd = random.Random(seed)
    t0 = time.time()
    cells = [(i, j) for i in range(m) for j in range(N)]; ncell = len(cells); cid = {c: k for k, c in enumerate(cells)}
    pairs = [(a, b) for a in range(ncell) for b in range(a + 1, ncell) if cells[a][1] != cells[b][1]]
    pid = {pr: k for k, pr in enumerate(pairs)}
    ncol = 1 + ncell + len(pairs)          # [const | cells | pairs]
    def vec_quad(coef, v):               # 1 - (l - v)^2 reduced: l^2 = sum a^2 x + 2 sum_{a<b} a_a a_b x_a x_b (same column -> 0)
        row = np.zeros(ncol, dtype=np.int64)
        row[0] = (1 - v * v) % p
        for k, a in enumerate(coef):
            if a: row[1 + k] = (row[1 + k] - a * a + 2 * v * a) % p
        nzk = [k for k, a in enumerate(coef) if a]
        for x in range(len(nzk)):
            for y in range(x + 1, len(nzk)):
                a, b = nzk[x], nzk[y]
                if cells[a][1] != cells[b][1]:
                    row[1 + ncell + pid[(a, b)]] = (row[1 + ncell + pid[(a, b)]] - 2 * coef[a] * coef[b]) % p
        return row
    rows = []
    if member != 'base':
        kind, M = member[:4], int(member[4:])
        for _ in range(M):
            coef = [rnd.randrange(p) for _ in cells]; v = rnd.randrange(p)
            if kind == 'psel':
                v = (sum(a for a, (i, j) in zip(coef, cells) if i == j) + rnd.randrange(1, p)) % p
            rows.append(vec_quad(coef, v))
    for i in range(m):                     # (r_i - 1) * 1 and (r_i - 1) * x_c, reduced
        base = np.zeros(ncol, dtype=np.int64); base[0] = -1 % p
        for j in range(N): base[1 + cid[(i, j)]] = 1
        rows.append(base)
        for c in range(ncell):
            row = np.zeros(ncol, dtype=np.int64); row[1 + c] = -1 % p
            for j in range(N):
                d = cid[(i, j)]
                if d == c: row[1 + c] = (row[1 + c] + 1) % p        # x_c^2 = x_c
                elif cells[d][1] != cells[c][1]:
                    a, b = min(c, d), max(c, d); row[1 + ncell + pid[(a, b)]] = 1
            rows.append(row)
    V2 = np.array(rows)
    r2 = rank_mod3(V2); rtop = rank_mod3(V2[:, 1 + ncell:]); dimV1 = m
    rec = dict(case=case, rank_V2=r2, rank_top2=rtop, ker_z1=r2 - rtop - dimV1, one_in_V2=bool(rank_mod3(np.vstack([V2, np.eye(ncol, dtype=np.int64)[:1]])) == r2),
               seconds=round(time.time() - t0, 1))
    res.append(rec); print(json.dumps(rec), flush=True); json.dump(res, open(out, 'w'), indent=1)
