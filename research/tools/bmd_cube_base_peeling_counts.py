"""Counts of the peeling degeneration of the base V^(b) (30 September 2026; cycle bmd-20260930-zb).

Tested statement: peeling the doubles of V^(b) one at a time gives far components F_p (2 <= p <= b-1,
e = p-1 peeled, l = b-p remaining) whose exponents at 0, -1/c and infinity are those listed in the
entry, and necks whose Weierstrass count is Sigma_0(F_p) + Sigma_inf(E_p).  By the Fuchs relation the
component count is #F_p = binom(R,2) - Sigma_c - Sigma_0 - Sigma_inf.  The script evaluates these
exact sums, checks every exponent list has R_b distinct entries, and checks
sum_p (#F_p + #neck_p) = T(b), with T(b) = (b-2) E + 12 binom(b,2) - sum_k MM_k as in
bmd_cube_base_weight.gp (N = 2b, E = binom(R,2)).  It also checks the closed form
#F_p = 4l(2e^2 + 6el - 5e - 4l + 5), and the attainment identity T(b) + sum_k (md_k - E) = -(R^2 + 2R),
which says that attaining T(b) forces the ordinary exponents 3, ..., R+2 at infinity; T, md and this
identity are polynomials in b of degree at most 5 for every b >= 1, and it is checked at b = 1..13.
The closed form is a polynomial identity of total degree <= 4 in (e, l); the checked set
{e, l >= 1, e + l <= 12} contains a unisolvent triangle for degree 4.  The neck formula and the
telescoped identity are proved in the entry; here they are consistency checks.
Exact Fractions; runs in well under a second.
"""
import sys
from fractions import Fraction as Fr
from math import comb

H = Fr(1, 2)


def Rn(n):
    return n * (2 * n - 1)


def md(N, c):
    K = 2 * N - 4
    return -c * K + comb(K, 2) - 3 + comb(comb(N - 2, 2), 2)


def T(b):
    N = 2 * b
    E = comb(Rn(b), 2)
    DT = (N - b - 2) * E + 12 * comb(b, 2)
    MM = [md(N, Fr(7, 2) if c > 1 else Fr(5, 2)) + 3 + 10 * (b - c) + 14 * (c - 1) for c in range(1, b + 1)]
    return DT - sum(MM)


def far(b, p):
    """Exponent lists of F_p at 0 and at infinity (w-orders), e = p-1 >= 1, l = b-p >= 1."""
    e, l = p - 1, b - p
    z_int = list(range(-(Rn(l) + 2), -2)) + list(range(0, Rn(e) + 4 * e + 1))
    z_half = [i - 7 * H for i in range(4 * e - 4 * e * l, 4 * e + 4 * l)]
    i_int = list(range(-(Rn(e) - 1), 1)) + list(range(3, Rn(l) + 4 * l + 4))
    i_half = [7 * H - i for i in range(-4 * e * l, 4 * e)]
    return z_int + z_half, i_int + i_half


def near_inf(b, p):
    """Exponent list of E_p at infinity (w-orders), l = b-p >= 1."""
    l = b - p
    ints = list(range(-(Rn(p) - 1), 1)) + list(range(3, Rn(l) + 3))
    half = [7 * H - i for i in range(4 * p - 4 * p * l, 4 * p)]
    return ints + half


def main(out):
    lines = []
    for b in (1, 2):
        R = Rn(b)
        if T(b) + md(2 * b, Fr(5, 2)) + (b - 1) * md(2 * b, Fr(7, 2)) - b * comb(R, 2) != -(R * R + 2 * R):
            raise SystemExit(f"b={b}: attainment identity fails")
        lines.append(f"b={b}: T(b)={T(b)}; attainment identity OK")
    for b in range(3, 14):
        N = 2 * b
        R = Rn(b)
        B = comb(R, 2)
        Sc = md(N, Fr(7, 2))
        tot = 0
        parts = []
        for p in range(2, b):
            z, i = far(b, p)
            ni = near_inf(b, p)
            for L, nm in ((z, "F0"), (i, "Finf"), (ni, "Einf")):
                if len(L) != R or len(set(L)) != R:
                    raise SystemExit(f"b={b} p={p} {nm}: {len(L)} entries, {len(set(L))} distinct, R={R}")
            nF = B - Sc - sum(z) - sum(i)
            nk = sum(z) + sum(ni)
            if nF.denominator != 1 or nk.denominator != 1 or nF < 0 or nk < 0:
                raise SystemExit(f"b={b} p={p}: bad counts {nF} {nk}")
            e, l = p - 1, b - p
            if nF != 4 * l * (2 * e * e + 6 * e * l - 5 * e - 4 * l + 5):
                raise SystemExit(f"b={b} p={p}: closed form fails")
            parts.append((p, int(nF), int(nk), 16 * p * (b - p) * (b - p - 1)))
            tot += nF + nk
        att = T(b) + md(N, Fr(5, 2)) + (b - 1) * Sc - b * B
        if att != -(R * R + 2 * R):
            raise SystemExit(f"b={b}: attainment identity fails")
        ok = tot == T(b)
        lines.append(f"b={b} N={N} T(b)={T(b)} sum={tot} {'OK' if ok else 'MISMATCH'}; attainment identity OK; closed form OK; "
                     f"(p, #F_p, #neck_p, 16p(b-p)(b-p-1)): {parts}")
        if not ok or any(q[2] != q[3] for q in parts):
            lines.append("FAILURE")
    txt = "\n".join(lines) + "\n"
    sys.stdout.write(txt)
    if out:
        with open(out, "w") as f:
            f.write(txt)


if __name__ == "__main__":
    main(sys.argv[sys.argv.index("--out") + 1] if "--out" in sys.argv else None)
