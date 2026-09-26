"""Cheap tests for the whole-thread route review (26 September 2026).

T1 (Smolensky-type restriction dimension). For a Res(Lin_p) line with forms L_1..L_r (rank r)
on v Boolean variables, the falsifying set is Z = {x in {0,1}^v : L_i(x) != b_i for all i}.
Compute dim of (multilinear polynomials of degree <= k) restricted to Z, over F_2 (where Z is a
flat of the cube) and over F_3, against the full dimension sum_{j<=k} C(v,j).

T2 (Razborov-Smolensky substitution). With g_i = 1 - L_i^2 (indicator L_i = 0) and
s_j = sum_i c_ij g_i, Q = prod_j (1 - s_j^2) and
beta_i = sum_{j: c_ij != 0} c_ij s_j prod_{j'<j}(1 - s_{j'}^2); check 1 - Q = sum_i beta_i g_i at every
point of F_3^h, and that Q = 1 where all g_i = 0.

T3 (zero patterns). For weak PHP points (near-matchings: n of the n+1 pigeons placed injectively,
n = 6), the zero pattern g(x) in {0,1}^h of a block of h = 6 forms: its weight distribution and
min-entropy, for (a) uniform random dense forms and (b) the cell forms x_{0t} - 1 of one pigeon;
and, for t = 3 random coefficient rows C, the fraction of points with g(x) != 0 and Cg(x) = 0
against 3^{-t}.
"""
import argparse, itertools, json, random
from math import comb, log2
import numpy as np


def rank_mod(A, p):
    A = A.copy() % p
    r = 0
    rows, cols = A.shape
    for c in range(cols):
        piv = None
        for i in range(r, rows):
            if A[i, c]:
                piv = i; break
        if piv is None:
            continue
        A[[r, piv]] = A[[piv, r]]
        inv = pow(int(A[r, c]), p - 2, p)
        A[r] = A[r] * inv % p
        nz = np.nonzero(A[:, c])[0]
        for i in nz:
            if i != r:
                A[i] = (A[i] - A[i, c] * A[r]) % p
        r += 1
        if r == rows:
            break
    return r


def t1(rng, v=10, ks=(2, 3), rs=(2, 4, 6)):
    pts = np.array(list(itertools.product((0, 1), repeat=v)), dtype=np.int64)
    out = []
    for p in (2, 3):
        for r in rs:
            L = np.array([[rng.randrange(p) for _ in range(v)] for _ in range(r)], dtype=np.int64)
            b = np.array([rng.randrange(p) for _ in range(r)], dtype=np.int64)
            vals = (pts @ L.T) % p
            Z = pts[np.all(vals != b, axis=1)]
            for k in ks:
                mons = [s for j in range(k + 1) for s in itertools.combinations(range(v), j)]
                M = np.array([[int(all(z[i] for i in s)) for s in mons] for z in Z], dtype=np.int64)
                d = rank_mod(M.T, p) if len(Z) else 0
                out.append({"p": p, "r": r, "k": k, "points": int(len(Z)), "restricted_dim": d,
                            "full_dim": len(mons), "flat_dim_bound": sum(comb(v - r, j) for j in range(k + 1))})
    return out


def t2(rng, h=4, t=3):
    ok = True
    for _ in range(20):
        C = [[rng.randrange(3) for _ in range(h)] for _ in range(t)]
        for Lv in itertools.product(range(3), repeat=h):
            g = [(1 - x * x) % 3 for x in Lv]
            s = [sum(C[j][i] * g[i] for i in range(h)) % 3 for j in range(t)]
            Q = 1
            for j in range(t):
                Q = Q * (1 - s[j] * s[j]) % 3
            beta = []
            for i in range(h):
                bi = 0
                for j in range(t):
                    pref = 1
                    for jj in range(j):
                        pref = pref * (1 - s[jj] * s[jj]) % 3
                    bi = (bi + C[j][i] * s[j] * pref) % 3
                beta.append(bi)
            if (1 - Q) % 3 != sum(beta[i] * g[i] for i in range(h)) % 3:
                ok = False
            if all(x == 0 for x in g) and Q != 1:
                ok = False
    return {"identity_holds": ok, "h": h, "t": t, "trials": 20}


def t3(rng, n=6, h=6, t=3, samples=20000):
    m = n + 1
    cells = [(i, j) for i in range(m) for j in range(n)]
    res = {}
    fams = {"random_dense": [({c: rng.randrange(3) for c in cells}, rng.randrange(3)) for _ in range(h)],
            "one_pigeon_cells": [({(0, j): 1}, 2) for j in range(h)]}  # x_{0j} - 1 = x_{0j} + 2
    for name, forms in fams.items():
        counts, weights = {}, {}
        C = [[rng.randrange(3) for _ in range(h)] for _ in range(t)]
        forb = 0
        for _ in range(samples):
            pig = rng.sample(range(m), n)
            holes = list(range(n)); rng.shuffle(holes)
            x = {(pig[a], holes[a]) for a in range(n)}
            g = tuple(int((c0 + sum(cf for c, cf in co.items() if c in x)) % 3 == 0) for co, c0 in forms)
            counts[g] = counts.get(g, 0) + 1
            w = sum(g); weights[w] = weights.get(w, 0) + 1
            if w and all(sum(C[j][i] * g[i] for i in range(h)) % 3 == 0 for j in range(t)):
                forb += 1
        res[name] = {"min_entropy_bits": round(-log2(max(counts.values()) / samples), 3),
                     "patterns": len(counts), "weight_hist": {str(k): v for k, v in sorted(weights.items())},
                     "forbidden_fraction": forb / samples, "three_to_minus_t": 3 ** -t}
    return res


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--out", required=True)
    ap.add_argument("--seed", type=int, default=20260926); a = ap.parse_args()
    rng = random.Random(a.seed)
    out = {"T1": t1(rng), "T2": t2(rng), "T3": t3(rng)}
    json.dump(out, open(a.out, "w"), indent=1)
    print(json.dumps(out["T2"]), flush=True)


if __name__ == "__main__":
    main()
