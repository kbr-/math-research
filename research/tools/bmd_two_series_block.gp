\\ Two-series block (7 October 2026; cycle bmd-20261007-n).  Tested statement (shape conjecture): for exponents a, b,
\\ lengths p, q and start s, the (p+q)-square matrix of the coefficients of T^s..T^(s+p+q-1) of the rows
\\ T^i (1+T)^(-a) (i < p) and T^n (1+cT)^(-b) (n < q) is K * c^(e) * (c-1)^(pq) with K a nonzero constant, as the
\\ single-series block theorem gives for p = q, a = b.  Printed: the determinant with powers of c and c-1 stripped
\\ (a constant if the shape holds), and the exponents.  Cases: the confluent tie block (a, b) = (5/2, 3/2), p = 2m,
\\ q = m, several starts s; controls p = q with a = b = 3/2 (known shape) and a generic pair (7/3, 3/2).
OUT = getenv("OUT");
emit(s) = print(s); if (OUT != 0 && OUT != "", write(OUT, s));
bn(x, k) = if (k < 0, 0, binomial(x, k));
blk(a, b, p, q, s) = matrix(p + q, p + q, r, j, my(k = s + j - 1); if (r <= p, bn(-a, k - (r - 1)), my(n = r - p - 1); bn(-b, k - n) * 'c^max(k - n, 0)));
desc(D) = { my(e0, e1, g);
  if (D == 0, return("0"));
  e0 = valuation(D, 'c); e1 = valuation(D, 'c - 1); g = D / ('c^e0 * ('c - 1)^e1);
  Str("c^", e0, " (c-1)^", e1, " * ", if (poldegree(g, 'c) == 0, Str("constant ", g), Str("polynomial of degree ", poldegree(g, 'c), ", factor degrees ", apply(poldegree, factor(g)[, 1]~)))); }
\\ QPRINT=1: instead, print the stripped factor Q (monic) of the confluent block for m = 2, 3 at three starts, to test
\\ whether Q depends on the start s.
{
if (getenv("QPRINT") == "1",
  for (m = 2, 3, foreach([m * (m - 1) / 2, m * (m - 1) / 2 + 1, m * (m - 1) / 2 + 3], s,
    my(D = matdet(blk(5/2, 3/2, 2 * m, m, s)), g = D / ('c^valuation(D, 'c) * ('c - 1)^valuation(D, 'c - 1)));
    emit(Str("Q, m = ", m, ", s = ", s, ": ", g / pollead(g, 'c))))); quit);
}
{
for (m = 1, 4, foreach([m * (m - 1) / 2, m * (m - 1) / 2 + 1, m * (m - 1) / 2 + 3], s,
  emit(Str("confluent block (5/2, 3/2), p = ", 2 * m, ", q = ", m, ", s = ", s, ": ", desc(matdet(blk(5/2, 3/2, 2 * m, m, s)))))));
for (m = 1, 3, emit(Str("control tie block (3/2, 3/2), p = q = ", m, ", s = ", m * (m - 1) / 2, ": ", desc(matdet(blk(3/2, 3/2, m, m, m * (m - 1) / 2))))));
for (m = 1, 3, emit(Str("control (7/3, 3/2), p = ", 2 * m, ", q = ", m, ", s = ", m * (m - 1) / 2, ": ", desc(matdet(blk(7/3, 3/2, 2 * m, m, m * (m - 1) / 2))))));
}
