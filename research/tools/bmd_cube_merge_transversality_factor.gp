\\ Factorization of the merge window condition (1 October 2026; cycle bmd-20261001-w).
\\ For g_j = (1 + b_j s)^(1/2), j = 1..K, U = sum_j Pol_(<n)(s) g_j, the determinant of the L x L matrix with
\\ rows s^i g_j (i < n; entries on the coefficients 0..L-a-1) and rows g_j (entries G_0..G_(a-1) in a negative
\\ block, then the coefficients of (g_j - g_j(0))/s) equals det(Taylor matrix of U) * D_a up to sign; D_a != 0
\\ iff X_a = U + s^-1 G_(>=a) is ordinary at 0.  Exact factorization over Q in the symbols b_1..b_K.
OUT = getenv("OUT");
emit(s) = print(s); if (OUT != 0 && OUT != "", write(OUT, s));
dd(n, K, a) = {
  my(M = n * K, L = M + K, b = vector(K, j, eval(Str("b", j))));
  my(g = vector(K, j, vector(L + 2, r, binomial(1/2, r - 1) * b[j]^(r - 1))));
  my(X = matrix(L, L), row = 0);
  for (j = 1, K, for (i = 0, n - 1, row++; for (t = 0, L - a - 1, X[row, a + 1 + t] = if (t - i >= 0, g[j][t - i + 1], 0))));
  for (j = 1, K, row++; for (r = 0, a - 1, X[row, r + 1] = g[j][r + 1]);
    for (t = 0, L - a - 1, X[row, a + 1 + t] = g[j][t + 2]));
  factor(matdet(X));
}
main() = {
  for (a = 1, 3, emit(Str("n=1 K=3 a=", a, ": ", dd(1, 3, a))));
  for (a = 1, 3, emit(Str("n=2 K=3 a=", a, ": ", dd(2, 3, a))));
}
main();
