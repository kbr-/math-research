\\ The leading constant f of the neck windows at beta_1 = 0 (3 October 2026; cycle bmd-20261003-q)
\\ thm:cube-neck-hankel-leading-form: f = const * sum_nu xi(nu) kappa_B(nu), nu over orderings of the balanced split of
\\ lw - c into l-1 parts (species s = 2..l).  At beta_1 = 0 (phi_1 = 1):
\\   xi(nu)      = det of the functionals on (P_1..P_l) in Pol_(<w)^l: [x^i](sum_s P_s phi_s), i < c, and [x^j]P_s, j < nu_s;
\\   kappa_B(nu) = det A_nu / det A_cons, where A_nu is the square matrix of the functionals omega -> [y^e](omega phi_s),
\\                 s >= 2, -n <= e <= nu_s - 1, on omega in span(y^-m : n+1 <= m <= M+K-c) (the rows e < 0 encode
\\                 omega orthogonal to U, the monomials y^-1..y^-n are excluded by orthogonality to Pol_(<n)), and
\\                 A_cons its nu-independent constraint block on m <= M (so det A_nu = det A_cons * kappa_B(nu)).
\\ Question: is f != 0 at beta_1 = 0, beta_s rational, for l = 3, 4; do all terms xi*kappa_B have one sign at real beta?
OUT = getenv("OUT");
emit(s) = print(s); if (OUT != 0 && OUT != "", write(OUT, s));
coef(s, k, beta) = if (s == 1, k == 0, binomial(-7/2, k) * beta[s]^k);
orderings(parts) = { my(res = List()); forperm(vecsort(parts), p, listput(res, Vec(p))); Set(Vec(res)); }
balanced(Y, m) = { my(a = Y \ m, b = Y % m); vector(m, i, if (i <= b, a + 1, a)); }
xi(l, w, c, nu, beta) = {
  \\ rows: basis (s,p); columns: i < c Taylor of g, then (s, j < nu_s) for s = 2..l
  my(N = l * w, A = matrix(N, N), col = 0);
  for (i = 0, c - 1, col++; for (s = 1, l, for (p = 0, w - 1, A[(s - 1) * w + p + 1, col] = if (i >= p, coef(s, i - p, beta), 0))));
  for (s = 2, l, for (j = 0, nu[s - 1] - 1, col++; A[(s - 1) * w + j + 1, col] = 1));
  matdet(A);
}
anu(l, w, c, n, nu, beta) = {
  \\ rows ordered: all constraint rows (e < 0) by species, then the evaluation rows (e >= 0) by species
  my(M = n * l, K = l * w, ms = vector(M + K - c - n, t, n + t), rows = List());
  for (s = 2, l, for (e = -n, -1, listput(rows, vector(#ms, j, my(k = e + ms[j]); if (k >= 0, coef(s, k, beta), 0)))));
  for (s = 2, l, for (e = 0, nu[s - 1] - 1, listput(rows, vector(#ms, j, my(k = e + ms[j]); if (k >= 0, coef(s, k, beta), 0)))));
  my(A = matrix(#rows, #ms, a, b, rows[a][b]));
  [matdet(A), matdet(matrix((l - 1) * n, M - n, a, b, A[a, b]))];
}
main() = {
  foreach(eval(getenv("CASES")), cs, my(l = cs[1], n = cs[2], w = 4, beta = concat([0], cs[3]));
    for (c = w, l * w - 1, my(nus = orderings(balanced(l * w - c, l - 1)), terms = List(), f = 0);
      foreach(nus, nu, my(x = xi(l, w, c, nu, beta), A = anu(l, w, c, n, nu, beta), kb = A[1] / A[2]);
        listput(terms, x * kb); f += x * kb);
      emit(Str("l=", l, " n=", n, " beta=", beta, " c=", c, ": orderings ", #nus, ", f (up to a common constant) ", if (f == 0, "ZERO", "nonzero"),
        ", term signs ", apply(t -> sign(t), Vec(terms)), ", constraint determinant nonzero ", anu(l, w, c, n, nus[1], beta)[2] != 0))));
}
main();
quit
