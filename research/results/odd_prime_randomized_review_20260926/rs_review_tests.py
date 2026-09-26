"""Cheap tests for the randomized-prefix route review (26 September 2026).

R1 (coding bridge). For uniform C in F_3^{t x h}, the least weight of a nonzero 0/1 vector in
ker C: the zero patterns a block can never forbid are exactly those of smaller weight. Exhaustive
over {0,1}^h for h = 16, t = 4, 6, 8, 20 samples each.

R2 (t-wise uniformity lead). For a randomized block of h forms with prefix matrix C (t rows), the
allowed value vectors are v in F_3^h whose zero pattern z(v) = (v_i == 0)_i is 0 or not in ker C.
Decide by exact LP whether a pairwise-uniform distribution on F_3^h is supported on the allowed set,
for h = 4, t = 1, 2, 10 random C each.
"""
import argparse, itertools, json, random
import numpy as np
from scipy.optimize import linprog


def min_weight(C, h):
    best = None
    for w in range(1, h + 1):
        for S in itertools.combinations(range(h), w):
            if all(sum(row[i] for i in S) % 3 == 0 for row in C):
                return w
    return best


def pairwise_feasible(C, h):
    pats = []
    for v in itertools.product(range(3), repeat=h):
        z = [int(x == 0) for x in v]
        forb = any(z) and all(sum(r[i] * z[i] for i in range(h)) % 3 == 0 for r in C)
        if not forb:
            pats.append(v)
    rows, rhs = [], []
    for a, b in itertools.combinations(range(h), 2):
        for x, y in itertools.product(range(3), repeat=2):
            rows.append([1.0 if (p[a] == x and p[b] == y) else 0.0 for p in pats]); rhs.append(1 / 9)
    res = linprog(np.zeros(len(pats)), A_eq=np.array(rows), b_eq=np.array(rhs), bounds=[(0, None)] * len(pats), method="highs")
    return res.status == 0, len(pats)


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--out", required=True)
    ap.add_argument("--seed", type=int, default=20260926); a = ap.parse_args()
    rng = random.Random(a.seed)
    out = {"R1": [], "R2": []}
    h = 16
    for t in (4, 6, 8):
        ws = []
        for _ in range(20):
            C = [[rng.randrange(3) for _ in range(h)] for _ in range(t)]
            ws.append(min_weight(C, h))
        out["R1"].append({"h": h, "t": t, "min_weights": ws})
        print("R1", t, ws, flush=True)
    for t in (1, 2):
        for _ in range(10):
            C = [[rng.randrange(3) for _ in range(4)] for _ in range(t)]
            f, npats = pairwise_feasible(C, 4)
            out["R2"].append({"h": 4, "t": t, "allowed": npats, "pairwise_feasible": f})
    json.dump(out, open(a.out, "w"), indent=1)


if __name__ == "__main__":
    main()
