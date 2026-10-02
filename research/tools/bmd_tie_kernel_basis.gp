\\ Minimal kernel basis of the confluent tie window (7 October 2026; cycle bmd-20261007-zp).
\\ Exact over Q: the right kernel of W^c(c) at degree bound nu1 (and nu2), from the linearized system; prints, for
\\ m = 1, 2, 3, a basis vector of each Forney degree with its entries factored, and two tests of the Fuchsian bridge:
\\ (i) d/dc-stability of the kernel: is W'(c) N(c) = 0 (then the kernel would carry a first-order connection)?
\\ (ii) the 2x2 minors of the minimal basis N: their gcd (1 for a minimal basis) and the factorization of one minor.
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
\\ kernel vectors of c-degree <= delta, exactly, as polynomial vectors
kervecs(W, delta) = {
  my(nr = #W[, 1], nc = #W, dW = vecmax(apply(e -> if (e == 0, 0, poldegree(e, 'c)), concat(Vec(W)))), M, K);
  M = matrix(nr * (delta + dW + 1), nc * (delta + 1));
  for (r = 1, nr, for (j = 1, nc, my(e = W[r, j]); if (e != 0,
    for (t = 0, poldegree(e, 'c), my(co = polcoef(e, t, 'c)); if (co != 0,
      for (s = 0, delta, M[(r - 1) * (delta + dW + 1) + t + s + 1, (j - 1) * (delta + 1) + s + 1] = co))))));
  K = matker(M);
  vector(#K, i, vector(nc, j, sum(s = 0, delta, K[(j - 1) * (delta + 1) + s + 1, i] * 'c^s))~);
}
{
foreach([[1, 3, 4], [2, 7, 7], [3, 12, 13]], cs,
  my(m = cs[1], W = winmat(m), V1 = kervecs(W, cs[2]), u = V1[1], v);
  v = if (cs[3] == cs[2], V1[2], my(V2 = kervecs(W, cs[3])); select(x -> matrank(Mat([u, x])) == 2, V2)[1]);
  u = u / content(u); v = v / content(v);
  my(N = Mat([u, v]), Wd = deriv(W, 'c), w = 3 * m + 5, g = 0);
  emit(Str("m = ", m, ": kernel dims at degree ", cs[2], ": ", #V1, "; W N = 0: ", W * N == 0, "; W'(c) N = 0: ", Wd * N == 0));
  for (i = 1, w, for (j = i + 1, w, g = gcd(g, matdet(vecextract(N, [i, j], [1, 2])))));
  emit(Str("   gcd of the 2x2 minors of N: ", factor(g)));
  emit(Str("   degrees of the entries of u: ", apply(e -> if (e == 0, -1, poldegree(e, 'c)), u~)));
  emit(Str("   entries of u, factored: ", apply(e -> if (e == 0, 0, factor(e)), u~)));
  emit(Str("   minor (first two columns) of N, factored: ", factor(matdet(vecextract(N, [1, 2], [1, 2]))))));
}
quit
