#!/usr/bin/env python3
"""The least boundary of the seven-eighths source's family of scales, under stated extrapolations.

Source formulas (retained TeX; proposition "Row counts from the witnesses", lemma "A high exponent for one
row bin", lemma "Compensated endpoint certificate"), written here for general scales (l, b):
    boundary        sigma0 = 11/12 - l/4,   kappa0 = 2 sigma0 - 1 = 5/6 - l/2,   h = 1/2 + 3l/2 + b/2,
    plain capacity  z_P(m) = (1 - 2m)/(6 kappa0)   (source: 6 kappa0 = 9/2 at kappa0 = 3/4), c = 1/(3 kappa0),
    D_x = 3 - (1 + 2c) x,   P_x = (2 - 2c x)(1 - x),   alpha = 5/6 (fixed slope of sixth-power amplification),
    J = (alpha - delta) D_x + delta P_x,   R_* = 1 - delta + (alpha - delta) delta P_x / (2 J),
    E_* = -3/4 - l/4 - b/3 + h R_* + (1/2 + l) delta + x delta l       (must be negative),
    low side: 3l/2 + 4b/3 <= 1/2.
EXTRAPOLATIONS (not statements of the source): that these forms hold for (l, b) other than (1/6, 1/8); in
particular that the constants of the low estimate, the contour value 17/50, the slope alpha and the witness
ranges do not depend on the scales, and that no further constraint of the source (prime supply, frequency
ranges, order of choices) binds first.

Tested statements:
1. (reading check) at (l, b) = (1/6, 1/8) the general E_* equals the source's closed form
   -E_* = (1 + (3 + 8y) delta)/48 - (13/32)(5/6 - delta) delta P_x / J, y = 1/2 - x, on the whole grid
   (exact rationals), its maximum is negative with -E_* >= 49/440640, and the float function e_star used
   for the optimum agrees with it there.  This tests the form at the source's point only; the dependence
   on (l, b) rests on the derivation in the entry, not on this check;
2. (computation under the extrapolations) for each b on a grid, the largest l with max E_* <= 0 over
   0 <= delta <= 5/6, 0 <= x <= 1/2 and the low-side condition; and the least boundary 11/12 - l/4.
The prime-supply condition l/h > 7/37 of the source is reported for the optimum, not imposed.
"""
import argparse
import json
from fractions import Fraction as Fr

import numpy as np

ALPHA = 5.0 / 6.0


def e_star(delta, x, l, b):
    kappa0 = 5.0 / 6.0 - l / 2.0
    c = 1.0 / (3.0 * kappa0)
    h = 0.5 + 1.5 * l + 0.5 * b
    d = 3.0 - (1.0 + 2.0 * c) * x
    p = (2.0 - 2.0 * c * x) * (1.0 - x)
    j = (ALPHA - delta) * d + delta * p
    r = 1.0 - delta + (ALPHA - delta) * delta * p / (2.0 * j)
    return -0.75 - l / 4.0 - b / 3.0 + h * r + (0.5 + l) * delta + x * delta * l


def reading_check():
    worst = None
    l, b, alpha = Fr(1, 6), Fr(1, 8), Fr(5, 6)
    h = Fr(1, 2) + 3 * l / 2 + b / 2
    for i in range(0, 201):
        delta = alpha * Fr(i, 200)
        for k in range(0, 51):
            x = Fr(k, 100)
            y = Fr(1, 2) - x
            d = 3 - Fr(17, 9) * x
            p = (2 - Fr(8, 9) * x) * (1 - x)
            j = (alpha - delta) * d + delta * p
            r = 1 - delta + (alpha - delta) * delta * p / (2 * j)
            mine = -Fr(3, 4) - l / 4 - b / 3 + h * r + (Fr(1, 2) + l) * delta + x * delta * l
            src = -((1 + (3 + 8 * y) * delta) / Fr(48) - Fr(13, 32) * (alpha - delta) * delta * p / j)
            assert mine == src, (delta, x)
            # the float implementation used for the optimum, at the source's point (c = 4/9 there)
            assert abs(e_star(float(delta), float(x), 1.0 / 6.0, 0.125) - float(mine)) < 1e-12, (delta, x)
            if worst is None or mine > worst:
                worst = mine
    assert -worst >= Fr(49, 440640)
    return float(worst)


def max_e(l, b, nd=1201, nx=201):
    delta = np.linspace(0.0, ALPHA, nd)[:, None]
    x = np.linspace(0.0, 0.5, nx)[None, :]
    e = e_star(delta, x, l, b)
    i = np.unravel_index(np.argmax(e), e.shape)
    return float(e[i]), float(delta[i[0], 0]), float(x[0, i[1]])


def largest_l(b):
    lo, hi = 0.0, 1.0 / 3.0
    hi = min(hi, (0.5 - 4.0 * b / 3.0) / 1.5)  # low side
    if hi <= 0 or max_e(1e-9, b)[0] > 0:
        return None
    if max_e(hi, b)[0] <= 0:
        return hi, "low side"
    for _ in range(60):
        mid = (lo + hi) / 2
        if max_e(mid, b)[0] <= 0:
            lo = mid
        else:
            hi = mid
    return lo, "certificate"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    args = ap.parse_args()
    worst = reading_check()
    rows = []
    for k in range(0, 121):
        b = k / 400.0
        res = largest_l(b)
        if res is None:
            continue
        l, binding = res
        e, dl, xx = max_e(l, b)
        rows.append({"b": b, "l_max": l, "boundary": 11.0 / 12.0 - l / 4.0, "binding": binding,
                     "argmax_delta": dl, "argmax_x": xx, "supply_l_over_h": l / (0.5 + 1.5 * l + 0.5 * b)})
    best = max(rows, key=lambda r: r["l_max"])
    src = next(r for r in rows if abs(r["b"] - 0.125) < 1e-12)
    out = {"reading_check_max_E_at_source_scales": worst, "source_floor": 49 / 440640,
           "at_source_b": src, "optimum": best, "seven_eighths_minus_optimum": 0.875 - best["boundary"],
           "supply_threshold": 7 / 37, "rows": rows}
    with open(args.out, "w") as f:
        json.dump(out, f, indent=1)
    print("reading check: max E_* at source scales = %.6e (source floor %.6e)" % (worst, -49 / 440640))
    print("at b = 1/8: l_max = %.6f, boundary = %.6f, binding %s at delta = %.3f, x = %.3f"
          % (src["l_max"], src["boundary"], src["binding"], src["argmax_delta"], src["argmax_x"]))
    print("optimum: b = %.4f, l_max = %.6f, boundary = %.6f (7/8 - %.3e), binding %s at delta = %.3f, x = %.3f, l/h = %.4f"
          % (best["b"], best["l_max"], best["boundary"], out["seven_eighths_minus_optimum"], best["binding"],
             best["argmax_delta"], best["argmax_x"], best["supply_l_over_h"]))


if __name__ == "__main__":
    main()
