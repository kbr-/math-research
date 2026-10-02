\\ The confluent tie window with the exponent lambda as a parameter (8 October 2026; cycle bmd-20261008-a, route review).
\\ W(L, c): rows T^i (1+T)^(-L-1) (i < 2m), T^n (1+cT)^(-L) (n < m), (1+T)^(-2L), ((1+T)(1+cT))^(-L),
\\ T (1+T)^(-L-1) (1+cT)^(-L); columns T^d .. T^(d+3m+4), d = binom(m, 2).  At L = 3/2 this is W^c(c).
\\ Question: is the absence of special values off c in {0, 1} (the Forney bound) a property of lambda = 3/2 only,
\\ or of every non-integer lambda?  Part A: the gcd G(L, c) in Q[L, c] of all maximal minors, factored (m = 2; m = 3 timed out at 900 s and is covered by part B: a non-vertical curve component would show at every lambda).
\\ Part B: for fixed rational lambda, the gcd of the maximal minors in Q[c], stripped of c and c - 1 (m = 2..5).
default(parisizemax, 4 * 10^9);
OUT = getenv("OUT");
emit(s) = print(s); if (OUT != 0 && OUT != "", write(OUT, s));
bn(a, k) = if (k < 0, 0, binomial(a, k));
rowco(r, m, k, L) = {
  if (r <= 2 * m, return(bn(-L - 1, k - (r - 1))));
  if (r <= 3 * m, my(n = r - 2 * m - 1); return(bn(-L, k - n) * 'c^max(k - n, 0)));
  if (r == 3 * m + 1, return(bn(-2 * L, k)));
  if (r == 3 * m + 2, return(sum(a = 0, k, bn(-L, a) * bn(-L, k - a) * 'c^(k - a))));
  sum(a = 0, k - 1, bn(-L - 1, a) * bn(-L, k - 1 - a) * 'c^(k - 1 - a));
}
winmat(m, L) = { my(d = m * (m - 1) / 2); matrix(3 * m + 3, 3 * m + 5, r, j, rowco(r, m, d + j - 1, L)); }
strip01(g) = { g = g / 'c^valuation(g, 'c); while (subst(g, 'c, 1) == 0, g = g / ('c - 1)); g; }
\\ gcd of all maximal minors; with early = 1 it stops once the gcd has no root off {0, 1} (enough for part B)
mingcd(W, early) = {
  my(w = #W, g = 0);
  for (i = 1, w, for (j = i + 1, w, g = gcd(g, matdet(vecextract(W, "..", select(t -> t != i && t != j, [1 .. w]))));
    if (early && g != 0 && poldegree(strip01(g), 'c) == 0, return(g))));
  g;
}
{
for (m = 2, 2,
  my(G = mingcd(winmat(m, 'L), 0), F = factor(G));
  emit(Str("Part A, m = ", m, ": gcd of maximal minors in Q[L, c] factors as ", F)));
foreach([1/2, 3/2, 5/2, 7/2, 1/3, 2/3, 1/4, -1/2, -3/2, 1/5], lam,
  my(res = List());
  for (m = 2, 5, my(g0 = mingcd(winmat(m, lam), 1)); if (g0 == 0, listput(res, [m, "all minors zero"]); next);
    my(g = strip01(g0)); listput(res, [m, poldegree(g, 'c), if (poldegree(g, 'c) > 0, factor(g)[, 1]~, [])]));
  emit(Str("Part B, lambda = ", lam, ": [m, degree of gcd off {0,1}, its factors] = ", Vec(res))));
\\ Part C: the lambda-top form of the minor on the first 3m + 3 columns.  Prediction: degree E = sum k - sum s_r in L,
\\ top coefficient det[x_r^(k - s_r) / (k - s_r)!] with nodes x = -1 (f rows), -c (g rows), -2, -1-c, -1-c and shifts
\\ s = i, n, 0, 0, 1, which is a confluent Vandermonde with roots only at c in {0, 1, 2, -1}.
for (m = 2, 3,
  my(d = m * (m - 1) / 2, W = winmat(m, 'L), D = matdet(vecextract(W, "..", [1 .. 3 * m + 3])), E, ld, top, xs, ss);
  E = sum(k = d, d + 3 * m + 2, k) - (m * (2 * m - 1) + m * (m - 1) / 2 + 1);
  xs = concat([vector(2 * m, i, -1), vector(m, i, -'c), [-2, -1 - 'c, -1 - 'c]]);
  ss = concat([vector(2 * m, i, i - 1), vector(m, i, i - 1), [0, 0, 1]]);
  ld = matdet(matrix(3 * m + 3, 3 * m + 3, r, j, my(e = d + j - 1 - ss[r]); if (e < 0, 0, xs[r]^e / e!)));
  top = polcoef(D, E, 'L);
  emit(Str("Part C, m = ", m, ": deg_L D = ", poldegree(D, 'L), ", E = ", E, ", top coefficient = leading determinant: ",
    top == ld, ", its factors in c: ", factor(ld)[, 1]~)));
}
quit
