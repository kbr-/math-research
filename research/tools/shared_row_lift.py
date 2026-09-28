"""Single-row lift defects of two coupled pairs sharing a row, in value space (odd-prime-shared-row-lift).

Statement tested.  k coupled pairs on the same row r_1: L_j + L_j' = -r_1 + x_{10} + c_j.  Their value map
(y_1, y_1', ..., y_k, y_k', pi) satisfies y_j + y_j' - c_j = y_1 + y_1' - c_1 (pure relations forced by the
shared row), and r_1 = c_1 + [pi = 1] - y_1 - y_1'.  With Y = {y, y', z, z' in the members' value sets} x states and
rho = r_1 - 1, the script computes the exact lift defect lambda_Y(D) = dim(N_D cap F_{D-1}) - dim N_{D-1}
(N_e = rho F_{<=e-1}) and the Hilbert defect Delta_Y of prop:single-row-lift-transfer, for D = 1..10.
By that proposition, in the product model these decide the two-row board's top lift.  The value space has
at most 3^3 * (m + 1) points, so plain Python elimination runs in about a second.

Usage: python3 shared_row_lift.py --m 2 --pairs 2 3 --Dmax 10 --out PATH
"""
import argparse
import itertools
import json


def rank_mod3(rows):
    rows = [list(r) for r in rows]
    if not rows or not rows[0]:
        return 0
    rank = 0
    for c in range(len(rows[0])):
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


NCOORD = 4
EXPMAX = 3  # exponents < EXPMAX; 2 suffices on sets inside {y != 0}, where y^2 = 1


def monomials(m, e):
    out = []
    for ex in itertools.product(range(EXPMAX), repeat=NCOORD):
        for cell in range(m + 1):
            if sum(ex) + (1 if cell else 0) <= e:
                out.append((ex, cell))
    return out


def evalrows(points, m, e, weight=None):
    mons = monomials(m, e) if e >= 0 else []
    rows = []
    for p in points:
        w = 1 if weight is None else weight(p)
        row = []
        for ex, cell in mons:
            v = w
            for coord, k in zip(p[:NCOORD], ex):
                v = v * pow(coord, k, 3) if k else v
            if cell and p[NCOORD] != cell:
                v = 0
            row.append(v % 3)
        rows.append(row)
    return rows


def hf(points, m, e):
    return rank_mod3(evalrows(points, m, e)) if e >= 0 and points else 0


def defects(Y, m, c0, D):
    rho = lambda p: (c0 + (1 if p[NCOORD] == 1 else 0) - p[0] - p[1] - 1) % 3
    Y1 = [p for p in Y if rho(p) == 0]
    Yp = [p for p in Y if rho(p) != 0]
    delta = hf(Y, m, D - 1) - hf(Y1, m, D - 1) - hf(Yp, m, D - 2)
    ND = evalrows(Y, m, D - 1, rho)
    F = evalrows(Y, m, D - 1)
    both = [a + b for a, b in zip(ND, F)]
    lam = rank_mod3(ND) + rank_mod3(F) - rank_mod3(both) - (rank_mod3(evalrows(Y, m, D - 2, rho)) if D >= 2 else 0)
    return lam, delta


def main():
    global NCOORD, EXPMAX
    ap = argparse.ArgumentParser()
    ap.add_argument("--m", type=int, default=2)
    ap.add_argument("--pairs", type=int, nargs="+", default=[2])
    ap.add_argument("--Dmax", type=int, default=10)
    ap.add_argument("--out", required=True)
    args = ap.parse_args()
    m = args.m
    NZ, F3 = [1, 2], [0, 1, 2]
    result = {"m": m, "cases": {}}
    for k in args.pairs:
        NCOORD = 2 * k
        sets = {"all pairs unbalanced": [NZ] * (2 * k)}
        if k == 2:
            sets["second pair balanced (control)"] = [NZ, NZ, F3, F3]
        for name, Vs in sets.items():
            EXPMAX = 2 if all(V == NZ for V in Vs) else 3
            for cs in itertools.product(range(3), repeat=k):
                Y = []
                for coords in itertools.product(*Vs):
                    s1 = (coords[0] + coords[1] - cs[0]) % 3
                    if all((coords[2 * j] + coords[2 * j + 1] - cs[j]) % 3 == s1 for j in range(1, k)):
                        Y += [tuple(coords) + (pi,) for pi in range(m + 1)]
                res = [defects(Y, m, cs[0], D) for D in range(1, args.Dmax + 1)]
                lam = [r[0] for r in res]
                dl = [r[1] for r in res]
                key = f"k={k}; {name}; constants={cs}"
                result["cases"][key] = {"lambda": lam, "Delta": dl, "size": len(Y)}
                print(f"{key} |Y|={len(Y)}: lambda {lam}; Delta {dl}")
    with open(args.out, "w") as f:
        json.dump(result, f, indent=1)


if __name__ == "__main__":
    main()
