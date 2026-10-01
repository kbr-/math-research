\\ Factorization of the neck leading constant at beta_1 = 0 (3 October 2026; cycle bmd-20261003-s)
\\ Question: for l = 3 (and l = 4 where feasible), is f_lead = sum_nu xi(nu) kappa_B(nu) at beta_1 = 0, as a rational
\\ function of the symbolic beta_2, ..., beta_l, a product of powers of the beta_s, of their differences and a rational
\\ constant (a product formula, which would prove f_lead != 0 for generic beta in every window)?
\\ Definitions as in research/tools/bmd_cube_neck_leading_constant.gp (copied).
OUT = getenv("OUT");
emit(s) = print(s); if (OUT != 0 && OUT != "", write(OUT, s));
coef(s, k, beta) = if (s == 1, k == 0, binomial(-7/2, k) * beta[s]^k);
orderings(parts) = { my(res = List()); forperm(vecsort(parts), p, listput(res, Vec(p))); Set(Vec(res)); }
balanced(Y, m) = { my(a = Y \ m, b = Y % m); vector(m, i, if (i <= b, a + 1, a)); }
xi(l, w, c, nu, beta) = {
  my(N = l * w, A = matrix(N, N), col = 0);
  for (i = 0, c - 1, col++; for (s = 1, l, for (p = 0, w - 1, A[(s - 1) * w + p + 1, col] = if (i >= p, coef(s, i - p, beta), 0))));
  for (s = 2, l, for (j = 0, nu[s - 1] - 1, col++; A[(s - 1) * w + j + 1, col] = 1));
  matdet(A);
}
anu(l, w, c, n, nu, beta) = {
  my(M = n * l, K = l * w, ms = vector(M + K - c - n, t, n + t), rows = List());
  for (s = 2, l, for (e = -n, -1, listput(rows, vector(#ms, j, my(k = e + ms[j]); if (k >= 0, coef(s, k, beta), 0)))));
  for (s = 2, l, for (e = 0, nu[s - 1] - 1, listput(rows, vector(#ms, j, my(k = e + ms[j]); if (k >= 0, coef(s, k, beta), 0)))));
  my(A = matrix(#rows, #ms, a, b, rows[a][b]));
  [matdet(A), matdet(matrix((l - 1) * n, M - n, a, b, A[a, b]))];
}
main() = {
  foreach(eval(getenv("CASES")), cs, my(l = cs[1], n = cs[2], w = 4, beta = concat([0], vector(l - 1, s, eval(Str("'b", s + 1)))));
    for (c = w, l * w, my(nus = orderings(balanced(l * w - c, l - 1)), f = 0);
      foreach(nus, nu, my(A = anu(l, w, c, n, nu, beta)); f += xi(l, w, c, nu, beta) * A[1] / A[2]);
      my(F = factor(numerator(f)), G = factor(denominator(f)));
      emit(Str("l=", l, " n=", n, " c=", c, ": orderings ", #nus, "; numerator factors ", F, "; denominator factors ", G))));
}
default(parisizemax, 4000000000);
main();
quit
