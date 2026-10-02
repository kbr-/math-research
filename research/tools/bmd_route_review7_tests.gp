\\ Tests of the route review of 8 October 2026 (cycle bmd-20261008-e) on the excess-one tie sub-window V(c)
\\ (columns T^d..T^(d+3m+3) of W^c(c)).
\\ A: the reduced matrix M(c) = R(c) B of lem:cube-tie-constant-row-reduction, B the echelon basis of ker C (identity on
\\    the last m + 3 columns): c-degrees, c-orders and irreducible factor degrees of its entries (m = 2, 3).
\\ B: the Wronskian of the coordinates of the primitive kernel vector x(c) (span dimension n + 1 = m + 3): its degree,
\\    which must be (n+1)(nu-n), its orders at 0 and 1, and the number of real roots and of roots in (0, 1) (m = 2, 3).
\\ C: the block of the c-free rows C and the m g-rows (3m + 1 rows, without the two product rows) on the same columns:
\\    the gcd of its maximal minors, stripped of c and c - 1 (m = 2..4).
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
dn(f, k) = { for (i = 1, k, f = deriv(f, 'c)); f; }
st(q) = { q = q / 'c^valuation(q, 'c); while (subst(q, 'c, 1) == 0, q = q / ('c - 1)); q; }
{
for (m = 2, 3, my(W = winmat(m), V = vecextract(W, "..", [1 .. #W - 1]), N = #V,
    Crows = concat([1 .. 2 * m], [3 * m + 1]), Rrows = concat([2 * m + 1 .. 3 * m], [3 * m + 2, 3 * m + 3]),
    C = vecextract(V, Crows, ".."), R = vecextract(V, Rrows, ".."), B, M, info = List());
  \\ echelon basis: solve C[:, first 2m+1] y = -C[:, rest] e_t
  my(C1 = vecextract(C, "..", [1 .. 2 * m + 1]), C2 = vecextract(C, "..", [2 * m + 2 .. N]));
  B = matconcat([-matsolve(C1, C2); matid(N - 2 * m - 1)]);
  M = R * B;
  for (r = 1, #M[, 1], for (t = 1, #M, my(e = M[r, t]);
    listput(info, if (e == 0, [r, t, "zero"], [r, t, poldegree(e, 'c), valuation(e, 'c), valuation(e, 'c - 1),
      apply(f -> poldegree(f, 'c), factor(st(e))[, 1]~)]))));
  emit(Str("A, m = ", m, ": M(c) is ", #M[, 1], " x ", #M, "; entries [row, col, degree, c-order, (c-1)-order, factor degrees] = ", Vec(info))));
for (m = 2, 3, my(W = winmat(m), V = vecextract(W, "..", [1 .. #W - 1]), K = matker(V), x, nu, Bs, n, Wr, s);
  x = K[, 1]; x = x * denominator(content(x)); x = x / content(x); nu = vecmax(apply(e -> poldegree(e, 'c), x));
  \\ a basis of the span of the coordinates
  my(M0 = matrix(#x, nu + 1, j, t, polcoef(x[j], t - 1, 'c)), I = matindexrank(M0)[1]);
  Bs = vector(#I, i, x[I[i]]); n = #Bs - 1;
  Wr = matdet(matrix(n + 1, n + 1, i, j, dn(Bs[j], i - 1)));
  s = st(Wr);
  emit(Str("B, m = ", m, ": n = ", n, ", nu = ", nu, ", deg Wronskian = ", poldegree(Wr, 'c), " (predicted ", (n + 1) * (nu - n),
    "), orders at 0 and 1: ", [valuation(Wr, 'c), valuation(Wr, 'c - 1)], ", real roots ", polsturm(s), " of ", poldegree(s, 'c),
    ", in (0,1): ", polsturm(s, [0, 1]), ", squarefree: ", poldegree(gcd(s, deriv(s, 'c)), 'c) == 0)));
for (m = 2, 4, my(W = winmat(m), V = vecextract(W, "..", [1 .. #W - 1]), rows = concat([1 .. 3 * m], [3 * m + 1]),
    P = vecextract(V, rows, ".."), w = #P, g = 0);
  forsubset([w, w - #P[, 1]], S, my(cols = select(t -> !setsearch(Set(Vec(S)), t), [1 .. w]));
    g = gcd(g, matdet(vecextract(P, "..", cols))); if (g != 0 && poldegree(st(g), 'c) == 0, break));
  emit(Str("C, m = ", m, ": C and g-rows (", #P[, 1], " x ", w, "): gcd of maximal minors off {0,1} has degree ", poldegree(st(g), 'c))));
}
quit
