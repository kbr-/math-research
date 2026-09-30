\\ Weight-zero hypothesis for a cluster shape (30 September 2026; cycle bmd-20260930-zza).
\\ A cluster of m roots with shape b has weight 0 at its mark exactly when 1, v and the binom(m,2) functions
\\ sqrt((1 - b_i v)(1 - b_j v)) are ordinary at v = 0: their Taylor matrix in v^0..v^(binom(m,2)+1) is nonsingular
\\ (lem:cube-multicluster-spine-classes, item 1; mark weight dictionary part (2)).  Exact rational arithmetic.
OUT = getenv("OUT");
emit(s) = print(s); if (OUT != 0 && OUT != "", write(OUT, s));
main() = {
  foreach ([[-5, -2, 0, 1, 2, 4], [-5, -3, -1, 1, 3, 5]], b,
    my(m = #b, C = m * (m - 1) / 2, K = C + 2, F = List([1 + O(x^K), x + O(x^K)]));
    for (i = 1, m, for (j = i + 1, m, listput(F, ((1 - b[i] * x) * (1 - b[j] * x) + O(x^K))^(1/2))));
    my(M = matrix(K, K, r, c, polcoef(F[r], c - 1)));
    emit(Str("shape ", b, ": ", K, " functions, Taylor determinant nonzero: ", matdet(M) != 0)));
}
main();
quit
