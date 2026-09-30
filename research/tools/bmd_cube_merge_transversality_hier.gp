\\ Hierarchical specialization of the merge window condition (1 October 2026; review cycle bmd-20261001-x).
\\ Same determinant as bmd_cube_merge_transversality_factor.gp (det(Taylor matrix of U) * D_a up to sign),
\\ at beta_j = T^(j-1), exact over Q[T].  Question: is the leading coefficient in T nonzero, so that the
\\ hierarchical limit (roots at separated scales) is nondegenerate, and what is its T-degree?
OUT = getenv("OUT");
emit(s) = print(s); if (OUT != 0 && OUT != "", write(OUT, s));
dd(n, K, a) = {
  my(M = n * K, L = M + K, b = vector(K, j, 'T^(j - 1)));
  my(g = vector(K, j, vector(L + 2, r, binomial(1/2, r - 1) * b[j]^(r - 1))));
  my(X = matrix(L, L), row = 0);
  for (j = 1, K, for (i = 0, n - 1, row++; for (t = 0, L - a - 1, X[row, a + 1 + t] = if (t - i >= 0, g[j][t - i + 1], 0))));
  for (j = 1, K, row++; for (r = 0, a - 1, X[row, r + 1] = g[j][r + 1]);
    for (t = 0, L - a - 1, X[row, a + 1 + t] = g[j][t + 2]));
  matdet(X);
}
main() = {
  foreach([[1, 3], [1, 4], [2, 3], [2, 4], [3, 3], [3, 4], [1, 5]], v,
    my(n = v[1], K = v[2]);
    for (a = 1, K, my(d = dd(n, K, a));
      emit(Str("n=", n, " K=", K, " a=", a, ": deg_T=", poldegree(d, 'T), " lead=", pollead(d, 'T),
        " lowest order=", valuation(d, 'T), " zero=", d == 0))));
}
main();
