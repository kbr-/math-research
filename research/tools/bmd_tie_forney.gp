\\ Forney indices of the right kernel of the confluent tie window (7 October 2026; cycle bmd-20261007-zl).
\\ W = W^c(c), (3m+3) x (3m+5), polynomial in c.  Its right kernel over Q(c) has dimension 2.  For a minimal polynomial
\\ basis (u, v) with degrees nu1 <= nu2 (Forney indices), the maximal minors of W equal lambda(c) times the complementary
\\ 2x2 minors of [u v] (up to sign), with lambda = gcd of the maximal minors, and nu1 + nu2 = max_(ij) deg D_ij - deg lambda.
\\ Computes, mod the prime p = 1000000007 (a computational choice): nu1 = least delta with a nonzero kernel vector of
\\ c-degree <= delta; the number of independent kernel vectors of degree <= delta for each delta up to nu1 + nu2;
\\ exactly over Q: max deg D_ij, and the c- and (c-1)-orders a, b of lambda (Z^W_m in {0,1} iff deg lambda = a + b).
\\ m = 1..4.
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
p = 1000000007;
\\ dimension of {x in F_p[c]^(cols) : deg x <= delta, W x = 0}
kdim(W, delta) = {
  my(nr = #W[, 1], nc = #W, dW = vecmax(apply(e -> if (e == 0, 0, poldegree(e, 'c)), concat(Vec(W)))), M);
  M = matrix(nr * (delta + dW + 1), nc * (delta + 1));
  for (r = 1, nr, for (j = 1, nc, my(e = W[r, j]); if (e != 0,
    for (t = 0, poldegree(e, 'c), my(co = polcoef(e, t, 'c)); if (co != 0,
      for (s = 0, delta, M[(r - 1) * (delta + dW + 1) + t + s + 1, (j - 1) * (delta + 1) + s + 1] = co))))));
  #matker(M * Mod(1, p));
}
{
for (m = 1, 4,
  my(W = winmat(m), w = 3 * m + 5, mx = 0, a = oo, b = oo, g = 0);
  for (i = 1, w, for (j = i + 1, w, my(D = matdet(vecextract(W, "..", select(t -> t != i && t != j, [1 .. w]))));
    if (D != 0, mx = max(mx, poldegree(D, 'c)); a = min(a, valuation(D, 'c)); b = min(b, valuation(D, 'c - 1)); g = gcd(g, D))));
  my(tot = mx - poldegree(g, 'c), dims = List(), nu1 = -1);
  for (delta = 0, tot, my(k = kdim(W, delta)); listput(dims, k); if (nu1 < 0 && k > 0, nu1 = delta));
  emit(Str("m = ", m, ": max deg D = ", mx, ", lambda = c^", a, " (c-1)^", b, " times degree ", poldegree(g, 'c) - a - b,
    "; nu1 + nu2 = ", tot, ", nu1 = ", nu1, ", nu2 = ", tot - nu1, "; kernel dimensions by degree bound 0..", tot, ": ", Vec(dims))));
}
quit
