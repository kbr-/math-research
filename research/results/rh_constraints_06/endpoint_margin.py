#!/usr/bin/env python3
"""Evaluate the seven-eighths source's endpoint certificate and its dependence on the input alpha.

Source (retained TeX, section "The endpoint inequality", lemma "Compensated endpoint certificate"):
for 0 <= delta <= alpha = 5/6 and 0 <= y <= 1/2,
    D = (37 + 34 y)/18,  P = (7 + 18 y + 8 y^2)/9,  J = (alpha - delta) D + delta P,
    -E_* = (1 + (3 + 8 y) delta)/48 - (13/32) (alpha - delta) delta P / J,
and the lemma states -E_* >= 49/440640.

Tested statements:
1. (reading check) with alpha = 5/6 the minimum of -E_* over a grid of (delta, y) is at least 49/440640, and
   the source's polynomial identity 10368 J (-E_*) = 10(37+34y) - 8(237+377y+26y^2) delta
   + 48(51+131y+94y^2+32y^3) delta^2 holds exactly at every grid point (exact rationals);
2. (sensitivity, not a statement of the source) the same expression with alpha replaced by 3/4, the value
   2 beta - 1 at beta = 7/8, keeping D and P unchanged: its minimum over 0 <= delta <= 3/4.
Whether D and P keep their form when alpha changes is NOT checked here; item 2 is a what-if on one formula.
"""
import argparse
import json
from fractions import Fraction as Fr


def neg_e(delta, y, alpha):
    d = (37 + 34 * y) / Fr(18)
    p = (7 + 18 * y + 8 * y * y) / Fr(9)
    j = (alpha - delta) * d + delta * p
    return (1 + (3 + 8 * y) * delta) / Fr(48) - Fr(13, 32) * (alpha - delta) * delta * p / j, j


def scan(alpha, n=400):
    best = None
    for i in range(n + 1):
        delta = alpha * Fr(i, n)
        for k in range(101):
            y = Fr(k, 200)
            val, j = neg_e(delta, y, alpha)
            if alpha == Fr(5, 6):
                poly = (10 * (37 + 34 * y) - 8 * (237 + 377 * y + 26 * y * y) * delta
                        + 48 * (51 + 131 * y + 94 * y * y + 32 * y**3) * delta * delta)
                assert 10368 * j * val == poly, (delta, y)
            if best is None or val < best[0]:
                best = (val, delta, y)
    return best


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    args = ap.parse_args()
    out = {}
    for name, alpha in [("alpha_5_6", Fr(5, 6)), ("alpha_3_4", Fr(3, 4))]:
        val, delta, y = scan(alpha)
        out[name] = {"alpha": str(alpha), "min_neg_E": float(val), "min_neg_E_exact": str(val),
                     "at_delta": float(delta), "at_y": float(y), "grid": "delta = alpha*i/400, y = k/200"}
        print(name, "min -E_* = %.6e at delta = %.4f, y = %.3f" % (val, delta, y))
    floor = Fr(49, 440640)
    out["source_floor"] = float(floor)
    out["reading_check_pass"] = bool(Fr(out["alpha_5_6"]["min_neg_E_exact"]) >= floor)
    print("source floor %.6e; reading check %s" % (floor, out["reading_check_pass"]))
    with open(args.out, "w") as f:
        json.dump(out, f, indent=1)
    raise SystemExit(0 if out["reading_check_pass"] else 1)


if __name__ == "__main__":
    main()
