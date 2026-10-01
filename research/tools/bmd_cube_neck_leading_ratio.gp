\\ Ratio test for the neck leading product formula (3 October 2026; cycle bmd-20261003-t)
\\ Conjecture (conj:cube-neck-leading-product, refined): for an equal balanced split (k = (lw-c)/(l-1) integral),
\\   xi      = C_xi    * prod_(s<t) (beta_s - beta_t)^((w-k)^2),
\\   kappa_B = C_kappa * prod_(s<t) (beta_s - beta_t)^(k(2n+k)),
\\ with beta_1 = 0 and s, t over all species.  Test: the ratios xi / prod and kappa_B / prod are the same at several
\\ random rational points beta.  Definitions as in research/tools/bmd_cube_neck_leading_constant.gp (copied).
OUT = getenv("OUT");
emit(s) = print(s); if (OUT != 0 && OUT != "", write(OUT, s));
coef(s, k, beta) = if (s == 1 && beta[1] == 0, k == 0, binomial(-7/2, k) * beta[s]^k);
xi(l, w, c, nu, beta) = {
  my(N = l * w, A = matrix(N, N), col = 0);
  for (i = 0, c - 1, col++; for (s = 1, l, for (p = 0, w - 1, A[(s - 1) * w + p + 1, col] = if (i >= p, coef(s, i - p, beta), 0))));
  for (s = 2, l, for (j = 0, nu[s - 1] - 1, col++; A[(s - 1) * w + j + 1, col] = 1));
  matdet(A);
}
kap(l, w, c, n, nu, beta) = {
  my(M = n * l, K = l * w, ms = vector(M + K - c - n, t, n + t), rows = List());
  for (s = 2, l, for (e = -n, -1, listput(rows, vector(#ms, j, my(k = e + ms[j]); if (k >= 0, coef(s, k, beta), 0)))));
  for (s = 2, l, for (e = 0, nu[s - 1] - 1, listput(rows, vector(#ms, j, my(k = e + ms[j]); if (k >= 0, coef(s, k, beta), 0)))));
  my(A = matrix(#rows, #ms, a, b, rows[a][b]));
  matdet(A) / matdet(matrix((l - 1) * n, M - n, a, b, A[a, b]));
}
disc(beta, ex) = prod(s = 1, #beta, prod(t = s + 1, #beta, (beta[s] - beta[t])^ex));
main() = {
  setrand(3);
  foreach(eval(getenv("CASES")), cs, my(l = cs[1], n = cs[2], w = 4);
    for (k = 0, w, my(c = l * w - (l - 1) * k); if (c < w, next);
      my(nu = vector(l - 1, i, k), rx = List(), rk = List());
      for (trial = 1, 3, my(beta = concat([if (getenv("XIONLY"), (random(199) - 99) / (1 + random(7)), 0)], vector(l - 1, s, (random(199) - 99) / (1 + random(7)))));
        listput(rx, xi(l, w, c, nu, beta) / disc(beta, (w - k)^2));
        listput(rk, if (getenv("XIONLY"), 0, kap(l, w, c, n, nu, beta) / disc(beta, k * (2 * n + k)))));
      emit(Str("l=", l, " n=", n, " c=", c, " k=", k, ": xi ratio constant ", #Set(Vec(rx)) == 1, " (", rx[1], "); kappa_B ratio constant ", #Set(Vec(rk)) == 1, " (", rk[1], ")"))));
}
main();
quit
