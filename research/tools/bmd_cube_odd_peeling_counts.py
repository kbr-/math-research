"""Counts of the peeling degeneration of the odd base (30 September 2026; cycle bmd-20260930-ze).

The odd base V^(b)_odd, N = 2b+1, has b doubles D_1..D_b (hierarchy order) and one simple root a, with
R = binom(N, 2) = R_b + 2b functions.  Peeling the doubles in order k = 1..b (D_k = eps c, a fixed) gives
near components E_k = Pol_(<R_k) + V^(b-k)_odd + sum_(s>k) (1+D_s z)^(-7/2) Pol_(<4k) + (1+az)^(-3/2) Pol_(<2k)
and far components F_k (e = k-1, l = b-k) with the exponent lists derived in the entry.  The script evaluates
those lists exactly, checks that each has R distinct entries, computes #F_k by the Fuchs relation
binom(R,2) - Sigma_0 - Sigma_c - Sigma_inf, the neck count Sigma_0(F_k) + Sigma_inf(E_k), and checks
sum_k (#F_k + #neck_k) = T_odd(b), with T from bmd_cube_base_weight.gp:
  T = (N-a-2) E - 3R - n ms(N) - md(N,5/2) - (a-1) md(N,7/2),  n = 1, a = b.
It also checks the attainment identity T + sum of minimal branch orders = -(R^2 + 2R) (ordinary infinity).
It checks the closed forms of #F_k (a polynomial of total degree <= 4 in (e, l) for e, l >= 1, whose
checked set {e, l >= 1, e + l <= 13} contains a unisolvent triangle; a polynomial of degree <= 4 in e for
l = 0, checked at e = 1..13) and the premises of the Toeplitz merge at 0.  The attainment identity is a
polynomial identity of degree <= 5 in b; the summed identity is a consistency check (telescoping proves it).
Exact Fractions.
"""
import sys
from fractions import Fraction as Fr
from math import comb

H = Fr(1, 2)


def Rn(n):
    return n * (2 * n - 1)


def Ro(n):  # dimension of V^(n)_odd
    return Rn(n) + 2 * n


def md(N, c):
    K = 2 * N - 4
    return -c * K + comb(K, 2) - 3 + comb(comb(N - 2, 2), 2)


def ms(N):
    R = comb(N, 2)
    return -Fr(3, 2) * (N - 1) + comb(N - 1, 2) + comb(R - N + 1, 2)


def T(b):
    N, a, n = 2 * b + 1, b, 1
    R = comb(N, 2)
    E = comb(R, 2)
    return (N - a - 2) * E - 3 * R - n * ms(N) - (md(N, Fr(5, 2)) + (a - 1) * md(N, Fr(7, 2)) if a >= 1 else 0)


def half_zero(e, l):
    """j-indices of the half-integral exponents -7/2 + j of F_k at 0."""
    mm = list(range(2 - 4 * l, 4))            # (-,-): (1+cx)^(-5/2) x^(-4l-3/2) Pol_(<4l+2)
    if e == 0:
        pm = []
    elif l >= 1:
        pm = list(range(2 * e - 4 * e * l, 4 * e))   # (+,-): limit of the 7/2 and 3/2 extensions
    else:
        pm = list(range(2, 2 * e + 2))               # (+,-) at l = 0: the 3/2 extension alone
    if pm:
        # premises of the Toeplitz merge: the monomial block starts at or below the (-,-) block and
        # the (-,-) block fits inside the merged range (offset + length <= monomial length)
        off = mm[0] - pm[0]
        if off < 0 or (l >= 1 and off + len(mm) > len(pm)):
            raise SystemExit(f"e={e} l={l}: merge premises fail")
    lo = min(mm + pm)
    return list(range(lo, lo + len(mm) + len(pm)))   # overlaps resolved upward (Toeplitz step)


def far(b, k):
    e, l = k - 1, b - k
    z_int = list(range(-(Ro(l) + 2), -2)) + list(range(0, Rn(e) + 4 * e + 1))
    z_half = [j - 7 * H for j in half_zero(e, l)]
    i_int = list(range(-(Rn(e) - 1), 1)) + list(range(3, Ro(l) + 4 * l + 6))
    i_half = [9 * H - 4 * e + i for i in range(4 * e * l + 6 * e)]
    return z_int + z_half, i_int + i_half


def near_inf(b, k):
    l = b - k
    ints = list(range(-(Rn(k) - 1), 1)) + list(range(3, Ro(l) + 3))
    if l >= 1:
        half = [9 * H - 4 * k + i for i in range(4 * k * l + 2 * k)]
    else:  # only (1+az)^(-3/2) Pol_(<2k): orders 5/2 - 2k + i
        half = [5 * H - 2 * k + i for i in range(2 * k)]
    return ints + half


def main(out):
    lines = []
    for b in range(1, 15):
        N = 2 * b + 1
        R = comb(N, 2)
        B = comb(R, 2)
        att = T(b) + (ms(N) - B) + (md(N, Fr(5, 2)) - B) + (b - 1) * (md(N, Fr(7, 2)) - B)
        if att != -(R * R + 2 * R):
            raise SystemExit(f"b={b}: attainment identity fails")
        Sc = md(N, Fr(7, 2))
        tot = 0
        parts = []
        for k in range(1, b + 1):
            z, i = far(b, k)
            ni = near_inf(b, k)
            for L, nm in ((z, "F0"), (i, "Finf"), (ni, "Einf")):
                if len(L) != R or len(set(L)) != R:
                    raise SystemExit(f"b={b} k={k} {nm}: {len(L)} entries, {len(set(L))} distinct, R={R}")
            Sck = Sc if k >= 2 else md(N, Fr(5, 2))
            nF = B - Sck - sum(z) - sum(i)
            nk = sum(z) + sum(ni)
            if nF.denominator != 1 or nk.denominator != 1 or nF < 0 or nk < 0:
                raise SystemExit(f"b={b} k={k}: bad counts {nF} {nk}")
            l = b - k
            e = k - 1
            if k >= 2:
                cf = (6 + 4 * l - 16 * l * l - 4 * e + 4 * e * l + 24 * e * l * l + 4 * e * e + 8 * e * e * l
                      if l >= 1 else 8 * e * e - 4 * e + 2)
                if nF != cf:
                    raise SystemExit(f"b={b} k={k}: closed form fails")
            pred = 4 * k * (4 * l * l - 1) if l >= 1 else 0
            if k == 1:
                pred = 0
            parts.append((k, int(nF), int(nk), pred))
            tot += nF + nk
        ok = tot == T(b) and all(p[2] == p[3] for p in parts) and parts[0][1] == 0
        lines.append(f"b={b} N={N} T={T(b)} sum={tot} {'OK' if ok else 'MISMATCH'}; attainment identity OK; "
                     f"(k, #F_k, #neck_k, predicted neck): {parts}")
        if not ok:
            lines.append("FAILURE")
    txt = "\n".join(lines) + "\n"
    sys.stdout.write(txt)
    if out:
        with open(out, "w") as f:
            f.write(txt)


if __name__ == "__main__":
    main(sys.argv[sys.argv.index("--out") + 1] if "--out" in sys.argv else None)
