\\ Order at c = 1 of the confluent tie window (7 October 2026; cycle bmd-20261007-zm).
\\ Tested statement (lem:cube-tie-window-order-at-one): the square minor of W^c(c) on its first 3m+3 columns has
\\ (c-1)-order exactly m^2+m+2, and every maximal minor has (c-1)-order at least m^2+m+2.  Checks m = 1..6 for the
\\ square minor, and all maximal minors for m <= 4 (forney.txt of cycle zl records the minimum b_m for m <= 4).
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
  my(d = m * (m - 1) / 2, n = 3 * m + 3, A = matrix(n, n, r, j, rowco(r, m, d + j - 1)));
  emit(Str("m = ", m, ": square minor (c-1)-order ", valuation(matdet(A), 'c - 1), " (predicted ", m^2 + m + 2, ")")));
for (m = 1, 4,
  my(d = m * (m - 1) / 2, w = 3 * m + 5, W = matrix(3 * m + 3, w, r, j, rowco(r, m, d + j - 1)), lo = oo);
  for (i = 1, w, for (j = i + 1, w, my(D = matdet(vecextract(W, "..", select(t -> t != i && t != j, [1 .. w]))));
    if (D != 0, lo = min(lo, valuation(D, 'c - 1)))));
  emit(Str("m = ", m, ": least (c-1)-order over all maximal minors ", lo)));
}
quit
