\\ Two-double step test (7 October 2026; cycle bmd-20261007-q).  Tested prediction: for a double root A = 1 over a
\\ cluster C = x*{B (double), simple roots s_k} with generic fixed shape, the extended two-double matrix
\\ [W0; U; V] (R+1 rows: confluent pair rows with the (A,B) block replaced by (1+T)^(-7/2)(1+BT)^(-7/2) Pol_(<=4),
\\ which equals W0's (A,B) part plus U, V by cor:cube-two-double-base-condition) on columns 0..R+1 has its Taylor
\\ minor (columns 0..R) of least x-valuation among the R+2 maximal minors, with nonzero leading coefficient.
\\ lambda = 3/2.  Prints, for each maximal minor (omitted column), its x-valuation.
OUT = getenv("OUT");
emit(s) = print(s); if (OUT != 0 && OUT != "", write(OUT, s));
bn(x, k) = if (k < 0, 0, binomial(x, k));
H(X, Y, k) = sum(n = 0, k, bn(-3/2, n) * bn(-3/2, k - n) * X^n * Y^(k - n));
HX(X, Y, k) = sum(n = 1, k, bn(-3/2, n) * n * X^(n - 1) * bn(-3/2, k - n) * Y^(k - n));
hh(X, k) = bn(-3, k) * X^k;
ext(B, i, k) = sum(a = 0, k - i, bn(-7/2, a) * bn(-7/2, k - i - a) * B^(k - i - a));
{
foreach([[2, [-2]], [5, [-2, 3]], [7, [-2, 3, 5]]], cs,
  my(b = cs[1], ss = cs[2], Ms = #ss, B = 'x * b, S = apply(t -> 'x * t, ss), N = Ms + 4, R = N * (N - 1) / 2, ncol = R + 2, rows = List(), A, v);
  for (i = 1, Ms, for (j = i + 1, Ms, listput(rows, vector(ncol, c, H(S[i], S[j], c - 1)))));
  for (i = 1, Ms, listput(rows, vector(ncol, c, H(S[i], 1, c - 1))); listput(rows, vector(ncol, c, HX(1, S[i], c - 1))));
  for (i = 1, Ms, listput(rows, vector(ncol, c, H(S[i], B, c - 1))); listput(rows, vector(ncol, c, HX(B, S[i], c - 1))));
  listput(rows, vector(ncol, c, hh(1, c - 1))); listput(rows, vector(ncol, c, hh(B, c - 1)));
  for (i = 0, 4, listput(rows, vector(ncol, c, ext(B, i, c - 1))));
  A = matrix(#rows, ncol, r, c, rows[r][c]);
  emit(Str("B = x*", b, ", simple x*", ss, ": N = ", N, ", R = ", R, ", rows ", #rows, " (R+1 = ", R + 1, ")"));
  v = vector(ncol, om, my(D = matdet(vecextract(A, "..", setminus(vector(ncol, c, c), [om])))); if (D == 0, oo, valuation(D, 'x)));
  emit(Str("   x-valuation of the minor omitting column j (j = 0..R+1): ", v));
  emit(Str("   Taylor minor (omit R+1): ", v[ncol], "; least valuation ", vecmin(v), if (v[ncol] == vecmin(v), "; Taylor attains it", "; Taylor does NOT attain it"))));
}
