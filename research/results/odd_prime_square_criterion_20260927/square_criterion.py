"""Square criterion modulo row sums (27 September 2026).

Statements tested: in the collision algebra At (cells x_{ic}, column-injective monomials) with
R_2 = sum_i r_i At_1, for a linear form l = sum a_{ic} x_{ic} with column vectors
u_c = (a_{0c}, ..., a_{m-1,c}):
 (a) necessary (proved by restricting to three columns): l^2 in R_2 implies the u_c are collinear;
 (b) the collinear forms are NOT all in R_2 (first version of this script: 6 of 40 rank-one forms);
 (c) exact criterion checked here: l^2 in R_2 iff all but at most one u_c are equal, i.e. l is
     congruent modulo the row sums to a form supported on one column.
Reports, per kind, the counts of (in R_2, collinear, single-column) combinations. Tiny exact linear algebra mod 3 (dimensions below 400), runs in seconds.
"""
import itertools, random, sys, json

def rank_mod3(rows, ncols):
    rows = [r[:] for r in rows]; rk = 0; col = 0
    nrows = len(rows)
    for col in range(ncols):
        piv = next((i for i in range(rk, nrows) if rows[i][col] % 3), None)
        if piv is None: continue
        rows[rk], rows[piv] = rows[piv], rows[rk]
        inv = 1 if rows[rk][col] % 3 == 1 else 2
        rows[rk] = [(v * inv) % 3 for v in rows[rk]]
        for i in range(nrows):
            if i != rk and rows[i][col] % 3:
                f = rows[i][col]
                rows[i] = [(a - f * b) % 3 for a, b in zip(rows[i], rows[rk])]
        rk += 1
        if rk == nrows: break
    return rk

def run(m, N, trials, seed):
    rnd = random.Random(seed)
    cells = [(i, c) for c in range(N) for i in range(m)]
    mons2 = [((i, c), (j, d)) for (i, c), (j, d) in itertools.combinations(cells, 2) if c != d]
    idx2 = {frozenset(k): t for t, k in enumerate(mons2)}
    def mul1(a, b):  # product of two linear forms (dicts cell->coef) in At_2
        v = [0] * len(mons2)
        for x, s in a.items():
            for y, t in b.items():
                if x[1] == y[1]: continue
                k = idx2[frozenset((x, y))]; v[k] = (v[k] + s * t) % 3
        return v
    R = []
    for i in range(m):
        r = {(i, c): 1 for c in range(N)}
        for x in cells: R.append(mul1(r, {x: 1}))
    rR = rank_mod3(R, len(mons2))
    def in_R(l):
        return rank_mod3(R + [mul1(l, l)], len(mons2)) == rR
    def collinear(l):
        us = [tuple(l.get((i, c), 0) for i in range(m)) for c in range(N)]
        p = us[0]; ds = [tuple((a - b) % 3 for a, b in zip(u, p)) for u in us]
        return rank_mod3([list(d) for d in ds], m) <= 1
    def single_column(l):
        us = [tuple(l.get((i, c), 0) for i in range(m)) for c in range(N)]
        from collections import Counter
        return Counter(us).most_common(1)[0][1] >= N - 1
    out = {"m": m, "N": N, "dimAt2": len(mons2), "rankR2": rR, "cases": []}
    for kind in ("single-column", "rank-one", "rank-two", "dense"):
        agree = 0; sq = 0; table = {}
        for _ in range(trials):
            if kind == "single-column":
                p = [rnd.randrange(3) for _ in range(m)]; w = [rnd.randrange(3) for _ in range(m)]; c0 = rnd.randrange(N)
                l = {(i, c): (w[i] if c == c0 else p[i]) for i in range(m) for c in range(N)}
            elif kind == "rank-one":
                q = [rnd.randrange(3) for _ in range(m)]; lam = [rnd.randrange(3) for _ in range(N)]
                p = [rnd.randrange(3) for _ in range(m)]  # add a row-sum shift p
                l = {(i, c): (q[i] * lam[c] + p[i]) % 3 for i in range(m) for c in range(N)}
            elif kind == "rank-two":
                q1 = [rnd.randrange(3) for _ in range(m)]; q2 = [rnd.randrange(3) for _ in range(m)]
                l1 = [rnd.randrange(3) for _ in range(N)]; l2 = [rnd.randrange(3) for _ in range(N)]
                l = {(i, c): (q1[i] * l1[c] + q2[i] * l2[c]) % 3 for i in range(m) for c in range(N)}
            else:
                l = {(i, c): rnd.randrange(3) for i in range(m) for c in range(N)}
            l = {k: v for k, v in l.items() if v}
            a, b, c = in_R(l), collinear(l), single_column(l)
            sq += a; agree += (a == b); table[(a, b, c)] = table.get((a, b, c), 0) + 1
        out["cases"].append({"kind": kind, "trials": trials, "squareInR": sq, "collinearAgrees": agree, "table": {str(k): v for k, v in table.items()}})
    return out

if __name__ == "__main__":
    res = [run(3, 5, 40, 1), run(3, 6, 40, 2), run(4, 5, 30, 3)]
    print(json.dumps(res, indent=1))
