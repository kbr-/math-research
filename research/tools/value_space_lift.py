"""Single-row lift defect of a coupled pair in its value space (odd-prime-full-set-lift).

Statement tested.  For a finite point set X with a degree filtration and rho = r - 1 for an F_3-valued
function r of degree 1, the degree-D lift N_D cap F_{D-1} in N_{D-1} along rho (N_e = rho * F_{<=e-1})
holds iff the lift defect
    Delta_X(D) = H_X(D-1) - H_{X_1}(D-1) - H_{X_0 u X_2}(D-2)
vanishes, where X_a = X cap {r = a} and H_Z(e) = dim of functions of degree <= e on Z (the single-row lift
criterion of the entry).  Under the pullback hypotheses the board's defect is the base Hilbert series
convolved with the value-space defect, so this script computes Delta_Y for the value set Y of the coupled
pair and for controls, together with the exact lift defect dim(N_D cap F_{D-1}) - dim N_{D-1}.

Value space (m rows): coordinates y, y' in F_3 (each of degree 1, exponents <= 2) and the state pi of
column 1 in {empty, 1..m}, with cells x_{i1} of degree 1 and x_{i1} x_{j1} = 0.  The coupled pair has
r_1 = c0 + [pi = 1] - y - y' (from L + L' = -r_1 + x_{11} + c0).  Y = {y in V1, y' in V2} x all states.
Sizes are at most 3*3*(m+1) points, so plain Python elimination runs in well under a second.

Usage: python3 value_space_lift.py --m 2 3 --out PATH
"""
import argparse
import itertools
import json


def rank_mod3(rows):
    rows = [list(r) for r in rows]
    rank, ncols = 0, (len(rows[0]) if rows else 0)
    for c in range(ncols):
        piv = next((i for i in range(rank, len(rows)) if rows[i][c] % 3), None)
        if piv is None:
            continue
        rows[rank], rows[piv] = rows[piv], rows[rank]
        inv = 1 if rows[rank][c] % 3 == 1 else 2
        rows[rank] = [(v * inv) % 3 for v in rows[rank]]
        for i in range(len(rows)):
            if i != rank and rows[i][c] % 3:
                f = rows[i][c]
                rows[i] = [(a - f * b) % 3 for a, b in zip(rows[i], rows[rank])]
        rank += 1
    return rank


def monomials(m, e):
    out = []
    for a, b in itertools.product(range(3), repeat=2):
        for cell in range(m + 1):  # 0: no cell, i: x_{i1}
            if a + b + (1 if cell else 0) <= e:
                out.append((a, b, cell))
    return out


def hf(points, m, e):
    if e < 0 or not points:
        return 0
    mons = monomials(m, e)
    rows = []
    for (y, yp, pi) in points:
        rows.append([(pow(y, a, 3) if a else 1) * (pow(yp, b, 3) if b else 1) * (1 if (cell == 0 or pi == cell) else 0) % 3
                     for (a, b, cell) in mons])
    return rank_mod3(rows)


def evalrows(points, m, e, weight=None):
    mons = monomials(m, e) if e >= 0 else []
    rows = []
    for p in points:
        w = 1 if weight is None else weight(p)
        rows.append([w * (pow(p[0], a, 3) if a else 1) * (pow(p[1], b, 3) if b else 1) * (1 if (cell == 0 or p[2] == cell) else 0) % 3
                     for (a, b, cell) in mons])
    return rows


def rank_cols(rows):
    return rank_mod3(rows) if rows and rows[0] else 0


def lift_defect(Y, m, c0, D):
    """dim (N_D cap F_{D-1}) - dim N_{D-1}, N_e = rho * F_{<=e-1}, computed from evaluation ranks."""
    rho = lambda p: (c0 + (1 if p[2] == 1 else 0) - p[0] - p[1] - 1) % 3
    ND = evalrows(Y, m, D - 1, rho)
    F = evalrows(Y, m, D - 1)
    both = [a + b for a, b in zip(ND, F)]
    inter = rank_cols(ND) + rank_cols(F) - rank_cols(both)
    return inter - rank_cols(evalrows(Y, m, D - 2, rho))


def defect(Y, m, c0, D):
    r = lambda p: (c0 + (1 if p[2] == 1 else 0) - p[0] - p[1]) % 3
    Y1 = [p for p in Y if r(p) == 1]
    Yp = [p for p in Y if r(p) != 1]
    return hf(Y, m, D - 1) - hf(Y1, m, D - 1) - hf(Yp, m, D - 2)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--m", type=int, nargs="+", default=[2])
    ap.add_argument("--out", required=True)
    args = ap.parse_args()
    F3 = [0, 1, 2]
    cases = {
        "coupled {y!=0} x {y'!=0}": ([1, 2], [1, 2]),
        "one unbalanced {y!=0} x F3": ([1, 2], F3),
        "cylinder control F3 x F3": (F3, F3),
        "coupled {y=0} x {y'=0}": ([0], [0]),
        "coupled {y!=0} x {y'=0}": ([1, 2], [0]),
    }
    result = {"m": args.m, "Dmax": 8, "cases": {}}
    for m, (name, (V1, V2)) in itertools.product(args.m, cases.items()):
        for c0 in range(3):
            Y = [(y, yp, pi) for y in V1 for yp in V2 for pi in range(m + 1)]
            ds = [defect(Y, m, c0, D) for D in range(1, 9)]
            ls = [lift_defect(Y, m, c0, D) for D in range(1, 9)]
            result["cases"][f"m={m}; {name}; c0={c0}"] = {"Delta": ds, "lift_defect": ls}
            print(f"m={m}; {name}; c0={c0}: Delta(D), D=1..8: {ds}; lift defect: {ls}")
    with open(args.out, "w") as f:
        json.dump(result, f, indent=1)


if __name__ == "__main__":
    main()
