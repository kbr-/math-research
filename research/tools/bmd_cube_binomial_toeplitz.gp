\\ Binomial Toeplitz determinants in the Eisenstein branch hypotheses (3 October 2026; cycle bmd-20261003-zzo).
\\ Test of the classical evaluation  det_{0<=i,j<m} binom(a, s+i-j) = prod_{i=0}^{m-1} binom(a+i, s) / binom(s+i, s)
\\ (MacMahon's box formula, via Lindstrom-Gessel-Viennot), for symbolic-free rational a, and its use for the
\\ half-integral 4x4 minor det[binom(-5/2, 4e+i-j)]_{i,j<4} of prop:cube-last-far-eisenstein-branch: prime factors of the
\\ numerator, against the window max(d, 2n) < p <= 2n + 8e + 7.
OUT = getenv("OUT");
emit(s) = print(s); if (OUT != 0 && OUT != "", write(OUT, s));
Rn(n) = n * (2 * n - 1);
gb(a, s) = if (s < 0, 0, prod(i = 0, s - 1, a - i) / s!);
lhs(a, s, m) = matdet(matrix(m, m, i, j, gb(a, s + i - j)));
rhs(a, s, m) = prod(i = 0, m - 1, gb(a + i, s) / gb(s + i, s));
{
my(bad = 0);
foreach ([-5/2, -7/2, -3, 1/3, 7/2, -11/2], a, for (s = 0, 12, for (m = 1, 6, if (lhs(a, s, m) != rhs(a, s, m), bad++))));
emit(Str("box formula det binom(a, s+i-j) = prod binom(a+i,s)/binom(s+i,s): mismatches over 6 values of a, s <= 12, m <= 6: ", bad));
for (e = 1, 12,
  my(M = lhs(-5/2, 4 * e, 4), n = Rn(e), d = Rn(e + 2), lo = max(d, 2 * n), hi = 2 * n + 8 * e + 7, f = factor(numerator(M)), big = select(p -> p > lo && p <= hi, f[, 1]~));
  emit(Str("e=", e, ": minor = ", M, "; largest prime of numerator ", if (#f~, vecmax(f[, 1]), 1), ", window (", lo, ", ", hi, "], window primes dividing it: ", big)));
}
