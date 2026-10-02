\\ Excess-one sub-windows of the confluent tie window (8 October 2026; cycle bmd-20261008-d).
\\ W = W^c(c) = W(3/2, c), (3m+3) x (3m+5).  Dropping a column can only lower the rank, so if the (3m+3) x (3m+4)
\\ sub-window on columns T^d..T^(d+3m+3) (drop last) or T^(d+1)..T^(d+3m+4) (drop first) has full rank at every
\\ c not in {0, 1}, so does W.  Such a sub-window has a one-dimensional kernel, the Cramer vector of its 3m + 4 maximal
\\ minors (a type II Hermite-Pade problem at a normal index).  Question: are the two sub-windows free of special values
\\ off {0, 1}?  For m = 1..6: the gcd of the 3m + 4 minors of each sub-window, stripped of c and c - 1: its degree and the
\\ factor degrees, and the c- and (c-1)-orders of the gcd.
default(parisizemax, 4 * 10^9);
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
winmat(m) = { my(d = m * (m - 1) / 2); matrix(3 * m + 3, 3 * m + 5, r, j, rowco(r, m, d + j - 1)); }
st(q) = { q = q / 'c^valuation(q, 'c); while (subst(q, 'c, 1) == 0, q = q / ('c - 1)); q; }
{
for (m = 1, 6, my(W = winmat(m), w = #W, out = List());
  foreach([[1 .. w - 1], [2 .. w]], cols, my(V = vecextract(W, "..", cols), g = 0);
    my(Ds = vector(#V, j, matdet(vecextract(V, "..", select(t -> t != j, [1 .. #V])))));
    for (j = 1, #V, g = gcd(g, Ds[j]));
    my(s = st(g), F = if (poldegree(s, 'c) > 0, factor(s)[, 1]~, []), mx = vecmax(apply(D -> poldegree(D, 'c), Ds)));
    listput(out, [if (cols[1] == 1, "drop last", "drop first"), valuation(g, 'c), valuation(g, 'c - 1), poldegree(s, 'c), apply(f -> poldegree(f, 'c), F), mx, mx - poldegree(g, 'c), binomial(m + 3, 3)]));
  emit(Str("m = ", m, ": [sub-window, c-order, (c-1)-order, degree of gcd off {0,1}, factor degrees, max minor degree, kernel degree nu = max - deg gcd, binom(m+3,3)] = ", Vec(out))));
\\ Part 2: the kernel vector x(c) of the drop-last sub-window, made primitive in Q[c], as Y(s, c) = sum_j x_j(c) s^j:
\\ its c-degree, the factor bidegrees of Y over Q[s, c], and the factorization pattern of x_(j+1)/x_j (degrees of the
\\ numerator and denominator after cancellation), for m = 1..3.  A hypergeometric kernel would give low-degree ratios.
for (m = 1, 3, my(W = winmat(m), V = vecextract(W, "..", [1 .. #W - 1]), K = matker(V), x, Y, F, rat = List());
  x = K[, 1]; x = x * denominator(content(x)); x = x / content(x);
  Y = sum(j = 1, #x, x[j] * 's^(j - 1)); F = factor(Y);
  for (j = 1, #x - 1, if (x[j] != 0, my(r = x[j + 1] / x[j]); listput(rat, [poldegree(numerator(r), 'c), poldegree(denominator(r), 'c)])));
  emit(Str("m = ", m, " kernel: max c-degree ", vecmax(apply(e -> poldegree(e, 'c), x)), ", factors of Y(s, c) as [deg_s, deg_c, mult] = ",
    vector(#F[, 1], t, [poldegree(F[t, 1], 's), poldegree(F[t, 1], 'c), F[t, 2]]), ", consecutive ratio degrees [num, den] = ", Vec(rat))));
}
quit
