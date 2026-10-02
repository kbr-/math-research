\\ Generic full rank of the confluent tie window (7 October 2026; cycle bmd-20261007-zi).
\\ Tested statement (lem:cube-tie-window-generic-rank): for every m >= 1, the maximal minor of W^c(c) on its first
\\ 3m+3 columns (T^d..T^(d+3m+2), d = binom(m,2)) has c-order exactly m d + 4m, with lowest coefficient
\\ +- s_(d^m)(1^(3/2)) * (b_(2m+1) b_(2m-1) - b_(2m)^2) * E_m, b_r = binom(-3/2, r), where E_m is the
\\ determinant of the coefficients of T^(d+m)..T^(d+3m+2) of T^i (1+T)^(-5/2) (i <= 2m+1) and (1+T)^(-3)
\\ (nonsingular by thm:cube-two-exponent-window).  Checks m = 1..6 exactly.
OUT = getenv("OUT");
emit(s) = print(s); if (OUT != 0 && OUT != "", write(OUT, s));
bn(a, k) = if (k < 0, 0, binomial(a, k));
rowco(r, m, k) = {
  if (r <= 2 * m, return(bn(-5/2, k - (r - 1))));
  if (r <= 3 * m, my(n = r - 2 * m - 1); return(bn(-3/2, k - n) * 'c^max(k - n, 0)));
  if (r == 3 * m + 1, return(bn(-3, k)));
  if (r == 3 * m + 2, return(sum(a = 0, k, bn(-3/2, a) * bn(-3/2, k - a) * 'c^(k - a))));
  sum(a = 0, k - 1, bn(-5/2, a) * bn(-3/2, k - 1 - a) * 'c^(k - 1 - a));
}
rect(u, h, a) = prod(i = 0, h - 1, prod(j = 0, u - 1, (a + j - i) / ((u - 1 - j) + (h - 1 - i) + 1)));
b(r) = bn(-3/2, r);
{
for (m = 1, 6,
  my(d = m * (m - 1) / 2, n = 3 * m + 3);
  my(A = matrix(n, n, r, j, rowco(r, m, d + j - 1)), D = matdet(A), v = valuation(D, 'c), lc = polcoef(D, v, 'c));
  my(E = matdet(matrix(2 * m + 3, 2 * m + 3, r, j, my(k = d + m + j - 1); if (r <= 2 * m + 2, bn(-5/2, k - (r - 1)), bn(-3, k)))));
  my(pred = rect(d, m, 3/2) * (b(2*m + 1) * b(2*m - 1) - b(2*m)^2) * E);
  emit(Str("m = ", m, ": c-order ", v, " (predicted ", m * d + 4 * m, "), E_m != 0: ", E != 0, ", lowest coefficient = +-prediction: ", abs(lc) == abs(pred))));
}
quit
