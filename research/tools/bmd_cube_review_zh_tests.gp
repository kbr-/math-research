\\ Cheap tests of the route review bmd-20260929-zh (29 September 2026).
\\ (a) Falsification test: minimality for a five-root caterpillar cluster. For b_i = c_i q^i (i = 1..5, q = 1000003
\\     playing eps), computes the q-adic valuations of the pair-space Pluecker coordinates P_E (rows: the 10 pairs,
\\     columns: Taylor degrees) for E = {0..9} and for every other 10-subset E of {0..12}; the minimality condition
\\     predicts val P_{0..9} < val P_E for all of them.
\\ (b) Lead test: is the five-root Taylor determinant zero on the hyperplane b1 + b2 = b3 + b4 (a random rational
\\     point on it)? A nonzero value confirms that no disjoint pair-sum factor divides it.
OUT = getenv("OUT");
emit(s) = print(s); if (OUT != 0 && OUT != "", write(OUT, s));
q = 1000003;
coef(x, y, m) = sum(k = 0, m, binomial(-3/2, k) * binomial(-3/2, m - k) * x^k * y^(m - k));
rows(b, L) = { my(R = List()); for (i = 1, #b, for (j = i + 1, #b, listput(R, vector(L, m, coef(b[i], b[j], m - 1))))); Mat(Vec(R)~); }
main() = {
  my(c = [3, -7, 11, 5, -2], b = vector(5, i, c[i] * q^i), A = matrix(10, 13), R = rows(b, 13));
  A = matrix(10, 13, i, j, R[i, j]);
  my(v0 = valuation(matdet(matrix(10, 10, i, j, A[i, j])), q), worst = oo, cnt = 0, viol = 0);
  forsubset([13, 10], E, my(e = Vec(E)); if (e == [1 .. 10], next);
    my(d = matdet(matrix(10, 10, i, j, A[i, e[j]]))); cnt++;
    if (d != 0, my(v = valuation(d, q)); worst = min(worst, v); if (v <= v0, viol++)));
  emit(Str("(a) M=5 caterpillar cluster: val P_{0..9} = ", v0, "; other ", cnt, " coordinates on columns <= 12: min valuation ", worst, ", violations ", viol));
  my(bb = [3, -7, 11, 0, 5]); bb[4] = bb[1] + bb[2] - bb[3];
  my(B = rows(bb, 10), d = matdet(matrix(10, 10, i, j, B[i, j])));
  emit(Str("(b) roots ", bb, " with b1+b2=b3+b4: Taylor determinant ", if (d == 0, "zero", "nonzero")));
}
main();
