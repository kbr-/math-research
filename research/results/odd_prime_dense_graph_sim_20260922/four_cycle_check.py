#!/usr/bin/env python3
"""Finite checks for the four-cycle test on dense bipartite graphs.

(1) Exact version of Lemma T: if every pigeon misses fewer than |B|/3 holes, every function on the
edges whose alternating sum vanishes on all 4-cycles is additive (a_i + b_h).  Checked by comparing
the F_p-dimension of the 4-cycle-invariant space with the additive dimension |A|+|B|-1 (G connected).
(2) Sharpness: on blow-ups of the 6-cycle (each vertex adjacent to two of three classes) the
invariant space is strictly larger, and the witness query #{i in A1 : g(i) in B2} mod p is not
constant on the support of nu_G.
Deterministic seed; output is printed and written as JSON next to this script.
"""
import itertools, json, random, sys, os

def rank_mod_p(rows, ncols, p):
    rows = [r[:] for r in rows]
    rank, col = 0, 0
    piv_row = 0
    for col in range(ncols):
        pr = None
        for r in range(piv_row, len(rows)):
            if rows[r][col] % p:
                pr = r; break
        if pr is None:
            continue
        rows[piv_row], rows[pr] = rows[pr], rows[piv_row]
        inv = pow(rows[piv_row][col], p - 2, p)
        rows[piv_row] = [(x * inv) % p for x in rows[piv_row]]
        for r in range(len(rows)):
            if r != piv_row and rows[r][col] % p:
                f = rows[r][col]
                rows[r] = [(x - f * y) % p for x, y in zip(rows[r], rows[piv_row])]
        piv_row += 1
        if piv_row == len(rows):
            break
    return piv_row

def invariant_dim(A, B, E, p):
    idx = {e: k for k, e in enumerate(sorted(E))}
    rows = []
    for i, j in itertools.combinations(A, 2):
        common = [h for h in B if (i, h) in E and (j, h) in E]
        for h, k in itertools.combinations(common, 2):
            r = [0] * len(idx)
            r[idx[(i, h)]] += 1; r[idx[(j, k)]] += 1
            r[idx[(i, k)]] -= 1; r[idx[(j, h)]] -= 1
            rows.append([x % p for x in r])
    rk = rank_mod_p(rows, len(idx), p) if rows else 0
    return len(idx) - rk

def random_dense(a, b, mu, rng):
    # delete cells while every vertex misses at most mu cells
    E = {(i, h) for i in range(a) for h in range(b)}
    miss_i = [0] * a; miss_h = [0] * b
    cells = sorted(E); rng.shuffle(cells)
    for (i, h) in cells:
        if miss_i[i] < mu and miss_h[h] < mu and rng.random() < 0.9:
            E.discard((i, h)); miss_i[i] += 1; miss_h[h] += 1
    return E

def support_values(A_cls, B_cls, E, p):
    """Enumerate nu_G support (one hole with p+1 pigeons, others one) and the witness query."""
    A = sorted(A_cls); B = sorted(B_cls)
    vals = set(); count = 0
    for hs in B:
        nb = [i for i in A if (i, hs) in E]
        for S in itertools.combinations(nb, p + 1):
            rest = [i for i in A if i not in S]
            holes = [h for h in B if h != hs]
            for perm in itertools.permutations(holes):
                if all((i, h) in E for i, h in zip(rest, perm)):
                    count += 1
                    g = dict(zip(rest, perm)); g.update({i: hs for i in S})
                    vals.add(sum(1 for i in A if A_cls[i] == 1 and B_cls[g[i]] == 2) % p)
    return count, sorted(vals)

def main():
    rng = random.Random(20260922)
    out = {"exact_version": [], "hexagon": []}
    for p in (3, 5):
        for (a, b) in ((6, 6), (7, 7), (8, 8), (9, 9), (9, 6), (8, 5)):
            mu = (b - 1) // 3  # 3*mu < b
            for trial in range(6):
                E = random_dense(a, b, mu, rng)
                d = invariant_dim(range(a), range(b), E, p)
                out["exact_version"].append({"p": p, "a": a, "b": b, "mu": mu, "edges": len(E),
                                             "inv_dim": d, "additive_dim": a + b - 1,
                                             "ok": d == a + b - 1})
    # hexagon blow-ups: classes A1,A2,A3 and B1,B2,B3, edge iff classes differ
    for (sa, sb, p) in (((3, 3, 3), (2, 2, 2), 3), ((5, 2, 2), (2, 2, 2), 3), ((2, 2, 2), (2, 2, 2), 3)):
        A_cls = {}; B_cls = {}
        k = 0
        for c, s in enumerate(sa, 1):
            for _ in range(s): A_cls[k] = c; k += 1
        k = 0
        for c, s in enumerate(sb, 1):
            for _ in range(s): B_cls[k] = c; k += 1
        E = {(i, h) for i in A_cls for h in B_cls if A_cls[i] != B_cls[h]}
        d = invariant_dim(sorted(A_cls), sorted(B_cls), E, p)
        rec = {"A_sizes": sa, "B_sizes": sb, "p": p, "inv_dim": d,
               "additive_dim": len(A_cls) + len(B_cls) - 1}
        if len(A_cls) == len(B_cls) + p:
            cnt, vals = support_values(A_cls, B_cls, E, p)
            rec.update({"support_size": cnt, "witness_values_mod_p": vals})
        out["hexagon"].append(rec)
    bad = [r for r in out["exact_version"] if not r["ok"]]
    out["summary"] = {"exact_cases": len(out["exact_version"]), "exact_failures": len(bad)}
    print(json.dumps(out["summary"]))
    for r in out["hexagon"]:
        print(json.dumps(r))
    with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "four_cycle_check.json"), "w") as f:
        json.dump(out, f, indent=1)

if __name__ == "__main__":
    main()
