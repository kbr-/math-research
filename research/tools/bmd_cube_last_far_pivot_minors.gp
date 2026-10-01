\\ Closed forms of the remaining pivot minors of prop:cube-last-far-eisenstein-branch (3 October 2026; cycle bmd-20261003-zzz).
\\ Tested statement (lem:cube-last-far-pivot-minors), n = R_e, k = 4e, C = {-3} u {-7/2 + j : j < k}:
\\  (i)  integral minor at 0 = det of the coefficients of x^(n+i), i = 0..k, in (1+x)^-3 and (1+x)^(-7/2) x^j (j < k);
\\       integral minor at -1 = the same for s^(n+i), s = 1+x, in x^-3 = (s-1)^-3 and x^(-7/2+j) = (s-1)^(-7/2+j);
\\       both have absolute value |V(C)| prod_{c in C} |c^(falling n)| / prod_{i=0}^{k} (n+i)!;
\\  (ii) half-integral minor at -1 = det of the coefficients of s^(k-1+i), i < 4, in s (s-1)^(j-7/2) (j < 4), of absolute
\\       value 12 prod_{j<4} |(j-7/2)^(falling k-1)| / prod_{i<4} (k-1+i)!.
\\ Exact check for e = 1..8 by direct determinants, and the window primes max(d, 2n) < p <= 2n+8e+7 dividing each minor.
OUT = getenv("OUT");
emit(s) = print(s); if (OUT != 0 && OUT != "", write(OUT, s));
Rn(n) = n * (2 * n - 1);
ff(a, r) = prod(s = 0, r - 1, a - s);
vdm(v) = prod(i = 1, #v, prod(j = i + 1, #v, v[j] - v[i]));
gb(a, s) = if (s < 0, 0, ff(a, s) / s!);
\\ coefficient of s^m in (s-1)^c = (-1)^c (1-s)^c: |.| = |binom(c, m)|; we keep the sign (-1)^m and drop the column phase
{
for (e = 1, 8,
  my(n = Rn(e), k = 4 * e, d = Rn(e + 2), C = concat([-3], vector(k, j, -7/2 + j - 1)));
  my(I0 = matdet(matrix(k + 1, k + 1, i, j, if (j == 1, gb(-3, n + i - 1), gb(-7/2, n + i - 1 - (j - 2))))));
  my(I1 = matdet(matrix(k + 1, k + 1, i, j, (-1)^(n + i - 1) * gb(C[j], n + i - 1))));
  my(Ic = abs(vdm(C)) * prod(j = 1, #C, abs(ff(C[j], n))) / prod(i = 0, k, (n + i)!));
  my(H1 = matdet(matrix(4, 4, i, j, (-1)^(k - 1 + i - 1) * gb(j - 1 - 7/2, k - 1 + i - 1))));
  my(Hc = 12 * prod(j = 0, 3, abs(ff(j - 7/2, k - 1))) / prod(i = 0, 3, (k - 1 + i)!));
  my(lo = max(d, 2 * n), hi = 2 * n + 8 * e + 7, badI = [], badH = []);
  forprime (p = lo + 1, hi, if (valuation(Ic, p) != 0, badI = concat(badI, p)); if (valuation(Hc, p) != 0, badH = concat(badH, p)));
  emit(Str("e=", e, ": |integral minor at 0| = closed form: ", abs(I0) == Ic, "; |integral minor at -1| = closed form: ", abs(I1) == Ic,
    "; |half minor at -1| = closed form: ", abs(H1) == Hc, "; window (", lo, ", ", hi, "]: primes dividing the integral minors ", badI,
    " (2n+1, 2n+3, 2n+5 = ", [2 * n + 1, 2 * n + 3, 2 * n + 5], "), dividing the half minor ", badH)));
}
