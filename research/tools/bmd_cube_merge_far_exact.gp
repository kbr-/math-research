\\ Exact far polynomials of a merge (1 October 2026; cycle bmd-20261001-z).
\\ F(n,k) = <w^-C..w^(1+P)> + w^(1/2) w^-(n-1) Pol_(<(k-1)n) + (w-1)^(1/2) Pol_(<k-1) + (w(w-1))^(1/2) w^-(n-1) Pol_(<n)
\\ (thm:cube-merge-far-count).  Each class c has factor phi_c = w^a (w-1)^b, a, b in {0, 1/2}; derivatives act
\\ on the rational part by D_c = d/dw + a/w + b/(w-1).  The Wronskian is prod(phi) times a rational function whose
\\ numerator, stripped of w and w-1, is the far polynomial R_(n,k).  Question: is R_(n,k) hypergeometric (a
\\ multiple of 2F1(-d, B; G; w), i.e. a Jacobi polynomial), and how does it factor over Q?
OUT = getenv("OUT");
emit(s) = print(s); if (OUT != 0 && OUT != "", write(OUT, s));
farclasses(n, k) = {
  my(C = n * (n - 1) / 2, P = (k - 1) * (k - 2) / 2);
  [[0, 0, vector(C + 2 + P, t, 'w^(t - 1 - C))], [1/2, 0, vector((k - 1) * n, t, 'w^(t - n))],
   [0, 1/2, vector(k - 1, t, 'w^(t - 1))], [1/2, 1/2, vector(n, t, 'w^(t - n))]];
}
farR(n, k) = {
  my(F = farclasses(n, k), d = sum(c = 1, 4, #F[c][3]), M = matrix(d, d), row = 0);
  for (c = 1, 4, my(a = F[c][1], b = F[c][2]);
    foreach (F[c][3], f, row++; my(g = f);
      for (m = 1, d, M[row, m] = g; g = deriv(g, 'w) + (a / 'w + b / ('w - 1)) * g)));
  my(W = matdet(M), N = numerator(W));
  while (subst(N, 'w, 0) == 0, N = N / 'w);
  while (subst(N, 'w, 1) == 0, N = N / ('w - 1));
  N / pollead(N);
}
\\ hypergeometric test: y = R solves w(1-w) y'' + (G - (A + B + 1) w) y' - A B y = 0 with A = -deg R
hyper(R) = {
  my(dg = poldegree(R), A = -dg, x = 'x, y = 'y);
  my(E = 'w * (1 - 'w) * deriv(deriv(R)) + ('G - (A + 'S + 1) * 'w) * deriv(R) - A * 'S * R);
  my(eqs = Vec(E), sol = 0);
  \\ E is linear in G and S; solve from two coefficients, then test all
  my(M = matrix(#eqs, 2, i, j, polcoef(eqs[i], 1, [ 'G, 'S][j])), v = vector(#eqs, i, -subst(subst(eqs[i], 'G, 0), 'S, 0)));
  iferr(sol = matinverseimage(M, v~), err, sol = []);
  if (#sol == 0, return("no hypergeometric fit"));
  Str("fits 2F1(", A, ", ", sol[2], "; ", sol[1], "; w)");
}
main() = {
  foreach([[2, 3], [3, 3], [2, 4], [4, 3]], v,
    my(R = farR(v[1], v[2]), fa = factor(R));
    emit(Str("(n,k)=", v, " deg R=", poldegree(R), " squarefree=", issquarefree(R),
      " factor degrees=", apply(poldegree, fa[, 1]~), " multiplicities=", fa[, 2]~, "; ", hyper(R)));
    emit(Str("  R = ", R)));
}
main();
\\ Newton polygons (Dumas): for primes p < 200, the largest denominator of a slope of the p-adic Newton polygon
\\ of R; a slope with denominator e forces every Q-factor containing a root of that segment to have degree >= e.
newton() = {
  foreach([[2, 3], [3, 3], [2, 4], [4, 3]], v,
    my(R = farR(v[1], v[2]), best = [0, 0]);
    forprime(p = 2, 200, my(sl = newtonpoly(R, p), e = vecmax(apply(t -> denominator(t), sl)));
      if (e > best[1], best = [e, p]));
    emit(Str("(n,k)=", v, " deg R=", poldegree(R), " largest slope denominator ", best[1], " at p=", best[2])));
}
newton();
