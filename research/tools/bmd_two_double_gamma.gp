\\ Two-double leading polynomial (7 October 2026; cycle bmd-20261007-q).  Gamma(y_1..y_M, B) is the Taylor minor
\\ (columns 0..2M+4) of the rows (1+T) phi_(y_s), (1+T) T phi_(y_s) (s <= M, phi_y = (1+yT)^(-3/2)) and
\\ T^i (1+BT)^(-7/2) (i <= 4).  Tested statement: Gamma = c_M * prod_(s<s') (y_s'-y_s)^4 * prod_s (y_s-B)^(e)
\\ with c_M a nonzero constant.  Prints the factorization of Gamma for M = 1, 2, 3.
default(parisizemax, 2 * 10^9);
OUT = getenv("OUT");
emit(s) = print(s); if (OUT != 0 && OUT != "", write(OUT, s));
bn(x, k) = if (k < 0, 0, binomial(x, k));
\\ coefficient of T^k in (1+T) T^e (1+yT)^(-3/2)
cs(y, e, k) = bn(-3/2, k - e) * y^max(k - e, 0) + bn(-3/2, k - e - 1) * y^max(k - e - 1, 0);
cb(B, i, k) = bn(-7/2, k - i) * B^max(k - i, 0);
{
for (M = 1, 3,
  my(ys = vector(M, s, eval(Str("y", s))), K = 2 * M + 5, A = matrix(K, K), r = 0, G);
  for (s = 1, M, r++; for (c = 1, K, A[r, c] = cs(ys[s], 0, c - 1)); r++; for (c = 1, K, A[r, c] = cs(ys[s], 1, c - 1)));
  for (i = 0, 4, r++; for (c = 1, K, A[r, c] = cb('B, i, c - 1)));
  G = matdet(A);
  emit(Str("M = ", M, ": Gamma factors ", factor(G))));
}
