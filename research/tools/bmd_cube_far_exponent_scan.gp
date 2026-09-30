\\ Exponent continuation for the far polynomials (2 October 2026; cycle bmd-20261002-f).
\\ F^(lam)(n,k): the far space with every square root replaced by a lam-th power (lam = 1/2 is F(n,k)).
\\ For real lam the far polynomial R(lam; w) is real.  Along a real path, collisions of non-real roots are generically
\\ avoided (a complex equation is two real conditions), so the generic collision events are collisions of real
\\ roots, where the number of real roots changes by two and disc(R) changes sign.
\\ Question: on lam in [1/40, 1/2], how does the number of real roots and the sign of disc_w R(lam) behave, and does
\\ the degree of R(lam) stay constant?  Exact rational lam on a grid (step 1/40), exact arithmetic.
OUT = getenv("OUT");
emit(s) = print(s); if (OUT != 0 && OUT != "", write(OUT, s));
default(parisizemax, 2000000000);
farRl(n, k, lam) = {
  my(C = n * (n - 1) / 2, P = (k - 1) * (k - 2) / 2);
  my(F = [[0, 0, vector(C + 2 + P, t, 'w^(t - 1 - C))], [lam, 0, vector((k - 1) * n, t, 'w^(t - n))],
    [0, lam, vector(k - 1, t, 'w^(t - 1))], [lam, lam, vector(n, t, 'w^(t - n))]]);
  my(d = sum(c = 1, 4, #F[c][3]), M = matrix(d, d), row = 0);
  for (c = 1, 4, my(a = F[c][1], b = F[c][2]);
    foreach (F[c][3], f, row++; my(g = f);
      for (m = 1, d, M[row, m] = g; g = deriv(g, 'w) + (a / 'w + b / ('w - 1)) * g)));
  my(N = numerator(matdet(M)));
  while (subst(N, 'w, 0) == 0, N = N / 'w);
  while (subst(N, 'w, 1) == 0, N = N / ('w - 1));
  N;
}
scan(n, k) = {
  my(rows = List());
  for (j = 1, 20, my(lam = j / 40, R = farRl(n, k, lam), D = poldisc(R));
    listput(rows, [lam, poldegree(R), polsturm(R), sign(D), issquarefree(R)]));
  emit(Str("(n,k)=", [n, k], " [lam, deg, real roots, sign disc, squarefree]: ", Vec(rows)));
}
scan(2, 3);
scan(3, 3);
scan(2, 4);
