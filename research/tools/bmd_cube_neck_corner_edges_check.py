#!/usr/bin/env python3
"""Read the raw output of bmd_cube_neck_corner_edges.gp and test the edge-pencil description (cycle bmd-20261001-k).

For every edge [v_r, v_(r+1)] of conj:cube-neck-corner-antidiagonal-polygon (vector (c, -(mn-c))) and every
coefficient pair (rho, rho'), the raw line gives [h, contains L(alpha[0]+(beta-1)[1]), rank of the top
coefficients, kappa].  Tested: (a) containment and top rank 1 (the limit is a member of the pencil between the
two vertex systems); (b) h equals the predicted edge value w . v_r; (c) kappa(rho, rho') = kappa(1,1) *
rho^(-c) * rho'^(mn-c) (the edge form is a monomial in the pencil coordinate: no zero ratios).
"""
import argparse
import ast
import re
from fractions import Fraction


def edge_params(m, n):
    starts = {sum(1 for k in range(m) for l in range(n) if k + l < s) for s in range(1, m + n - 1)}
    return [c for c in range(1, m * n) if c not in starts]


def vertices(m, n):
    c = edge_params(m, n)
    return [(sum(c[:r]), sum(m * n - x for x in c[r:])) for r in range(len(c) + 1)]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--raw", required=True)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    text = re.sub(r"\x1b\[[0-9;]*m", "", open(a.raw).read())
    line = next(l for l in text.splitlines() if "raw tasks " in l)
    tl, _, rl = line.split("raw tasks ", 1)[1].partition(": ")
    tasks = ast.literal_eval(tl)
    rl = re.sub(r"(-?\d+)/(\d+)", r'"\1/\2"', rl)
    res = ast.literal_eval(rl)
    base, out, bad = {}, [], []
    for (m, n, w1, w2, al, be, r1, r2), (h, cont, top, kap) in zip(tasks, res):
        r = al - (m - 1)
        c = edge_params(m, n)[r]
        v = vertices(m, n)[r]
        kap = Fraction(kap) if not isinstance(kap, str) or "/" in kap or kap.lstrip("-").isdigit() else kap
        key = (m, n, r)
        if (r1, r2) == (1, 1):
            base[key] = kap
        pred_h = w1 * v[0] + w2 * v[1]
        ok = cont == 1 and top == 1 and h == pred_h
        ok = ok and isinstance(kap, Fraction) and kap != 0 and key in base and base[key] != 0
        if ok:
            ok = kap == base[key] * Fraction(r1) ** (-c) * Fraction(r2) ** (m * n - c)
        out.append(f"({m},{n}) edge r={r} c={c} w=({w1},{w2}) (rho,rho')=({r1},{r2}): h={h} (pred {pred_h}) "
                   f"contains={cont} top rank={top} kappa={kap} {'ok' if ok else 'MISMATCH'}")
        if not ok:
            bad.append(out[-1])
    out.append(f"checked {len(tasks)} (edge, coefficient pair) cases; mismatches: {len(bad)}")
    open(a.out, "w").write("\n".join(out) + "\n")
    print("\n".join(out[-1:] + bad))


if __name__ == "__main__":
    main()
