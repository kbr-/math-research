\\ Top degree in c of the confluent tie window (7 October 2026; cycle bmd-20261007-zn).
\\ Tested statement (lem:cube-tie-window-top-degree): every maximal minor of W^c(c) has degree at most
\\ delta_m = m d + 3m^2 + 6m + 6 (d = binom(m,2)), with equality for the minor on the last 3m+3 columns.  Checks the
\\ last-columns minor for m = 1..6 (the maximum over all minors for m <= 4 is in research/results/bmd-20261007-zl/forney.txt).
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
{
for (m = 1, 6,
  my(d = m * (m - 1) / 2, n = 3 * m + 3, A = matrix(n, n, r, j, rowco(r, m, d + 2 + j - 1)));
  emit(Str("m = ", m, ": last-columns minor degree ", poldegree(matdet(A), 'c), " (predicted ", m * d + 3 * m^2 + 6 * m + 6, ")")));
}
quit
