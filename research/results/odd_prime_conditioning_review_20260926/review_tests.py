"""Cheap tests for the conditioning route review (26 September 2026).

Test 1 (Kothari-Mori-O'Donnell-Witmer lead). A W clause on forms (L_S, L_i), |S| = k, forbids exactly the
value patterns v in F_3^{k+1} with v_j != 0 for all j in S and v_i = 0. Question: is there a
t-wise uniform distribution on F_3^{k+1} supported on the allowed patterns? Decided exactly by
linear-programming feasibility, for k = 1..5 and t = 2, 3.

Test 2 (permanent condition for additive forms). Statement tested: for forms whose reduced
coefficients are additive, d_{it} = v_t - v_{top(i)} (column statistics), the doubled permanent
of thm:sparse-conditioning is nonzero for some separated choice. Random left-5-regular graph with
r = 3000 pigeons and r-1 holes, top = largest hole index of the pigeon, q = 1..4 forms, 200 random choices of 2q
pigeons of a greedy separated set and one non-top cell each; reports the fraction with a nonzero
permanent (a positive fraction means the condition holds). Sanity control (holds by construction,
since separated pigeons cannot both lie in the ball): forms whose reduced
coefficients vanish outside the distance-2 ball of one pigeon, where the permanent must vanish
for every separated choice (q = 1).
"""
import argparse
import itertools
import json
import random

import numpy as np
from scipy.optimize import linprog


def tuniform_feasible(k, t):
    n = k + 1
    pats = [v for v in itertools.product(range(3), repeat=n)
            if not (all(v[j] != 0 for j in range(k)) and v[k] == 0)]
    rows, rhs = [], []
    for coords in itertools.combinations(range(n), t):
        for vals in itertools.product(range(3), repeat=t):
            rows.append([1.0 if all(p[c] == x for c, x in zip(coords, vals)) else 0.0 for p in pats])
            rhs.append(3.0 ** (-t))
    res = linprog(np.zeros(len(pats)), A_eq=np.array(rows), b_eq=np.array(rhs),
                  bounds=[(0, None)] * len(pats), method="highs")
    return res.status == 0, len(pats)


def perm_mod3(M):
    """Ryser's formula, vectorized over the column subsets; exact integers, then mod 3."""
    M = np.array(M, dtype=np.int64)
    n = M.shape[0]
    masks = np.arange(1, 1 << n)
    S = ((masks[:, None] >> np.arange(n)[None, :]) & 1).astype(np.int64)
    sums = M @ S.T
    prods = np.prod(sums % 3, axis=0) % 3
    signs = np.where(S.sum(axis=1) % 2 == n % 2, 1, -1)
    return int((signs * prods).sum() % 3)


def random_graph(r, rng):
    h = r - 1
    return [sorted(rng.sample(range(h), 5)) for _ in range(r)]


def separated_set(G, rng):
    holes = {}
    for i, N in enumerate(G):
        for t in N:
            holes.setdefault(t, []).append(i)
    nb = [set(j for t in N for j in holes[t]) - {i} for i, N in enumerate(G)]
    order = list(range(len(G)))
    rng.shuffle(order)
    chosen, banned = [], set()
    for i in order:
        if i in banned:
            continue
        chosen.append(i)
        ball = {i} | nb[i]
        for j in list(nb[i]):
            ball |= nb[j]
        banned |= ball
    return chosen


def sample_perm(rows_of, P, q, rng, samples=200):
    """Fraction of random choices (2q distinct separated pigeons, one non-top cell each) with a
    nonzero doubled permanent."""
    cols = [j for j in range(q) for _ in range(2)]
    hits = 0
    for _ in range(samples):
        pig = rng.sample(P, 2 * q)
        chosen = [rng.choice(rows_of[i]) for i in pig]  # one non-top cell per pigeon
        M = [[row[c] for c in cols] for row in chosen]
        hits += perm_mod3(M) != 0
    return hits / samples


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--seed", type=int, default=20260926)
    a = ap.parse_args()
    rng = random.Random(a.seed)
    out = {"tuniform": [], "additive": [], "control": []}
    for k in range(1, 6):
        for t in (2, 3):
            if t > k + 1:
                continue
            feas, npats = tuniform_feasible(k, t)
            out["tuniform"].append({"k": k, "t": t, "allowed_patterns": npats, "feasible": feas})
            print("tuniform", k, t, feas, flush=True)
    r = 3000
    for trial in range(10):
        G = random_graph(r, rng)
        P = separated_set(G, rng)
        for q in range(1, 5):
            v = [[rng.randrange(3) for _ in range(r - 1)] for _ in range(q)]
            rows_of = []
            for i, N in enumerate(G):
                top = N[-1]
                rows_of.append([[(v[j][t] - v[j][top]) % 3 for j in range(q)] for t in N[:-1]])
            frac = sample_perm(rows_of, P, q, rng)
            out["additive"].append({"trial": trial, "q": q, "separated": len(P), "nonzero_fraction": frac})
        print("additive trial", trial, "separated", len(P), flush=True)
    # control: q = 1, reduced coefficients supported on the distance-2 ball of pigeon 0
    for trial in range(10):
        G = random_graph(r, rng)
        P = separated_set(G, rng)
        holes = {}
        for i, N in enumerate(G):
            for t in N:
                holes.setdefault(t, []).append(i)
        nb = [set(j for t in N for j in holes[t]) - {i} for i, N in enumerate(G)]
        ball = {0} | nb[0]
        rows_of = [[[rng.randrange(3) if i in ball else 0] for _ in range(4)] for i in range(r)]
        found = False
        for x, y in itertools.combinations(P, 2):
            for rx in rows_of[x]:
                for ry in rows_of[y]:
                    if (2 * rx[0] * ry[0]) % 3:
                        found = True
        out["control"].append({"trial": trial, "ball": len(ball), "perm_nonzero_somewhere": found})
    json.dump(out, open(a.out, "w"), indent=1)


if __name__ == "__main__":
    main()
