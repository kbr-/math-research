\\ Klein-four pullback of the far polynomials (2 October 2026; review cycle bmd-20261002-g).
\\ The cover u^2 = w, v^2 = w - 1 is the conic u^2 - v^2 = 1, parametrized by u = (t + 1/t)/2, v = (t - 1/t)/2, so
\\ w = (t + 1/t)^2 / 4 and F(n,k) pulls back to a space of Laurent polynomials in t.  The far points pull back to the
\\ roots of R(w(t)).  Question: does the numerator of R_(n,k)((t + 1/t)^2/4) factor over Q beyond the Galois-orbit
\\ splitting (a factor of degree 4 deg R if R's roots have no structure along the cover)?
OUT = getenv("OUT");
emit(s) = print(s); if (OUT != 0 && OUT != "", write(OUT, s));
default(parisizemax, 2000000000);
farR(n, k) = {
  my(C = n * (n - 1) / 2, P = (k - 1) * (k - 2) / 2);
  my(F = [[0, 0, vector(C + 2 + P, t, 'w^(t - 1 - C))], [1/2, 0, vector((k - 1) * n, t, 'w^(t - n))],
    [0, 1/2, vector(k - 1, t, 'w^(t - 1))], [1/2, 1/2, vector(n, t, 'w^(t - n))]]);
  my(d = sum(c = 1, 4, #F[c][3]), M = matrix(d, d), row = 0);
  for (c = 1, 4, my(a = F[c][1], b = F[c][2]);
    foreach (F[c][3], f, row++; my(g = f);
      for (m = 1, d, M[row, m] = g; g = deriv(g, 'w) + (a / 'w + b / ('w - 1)) * g)));
  my(N = numerator(matdet(M)));
  while (subst(N, 'w, 0) == 0, N = N / 'w);
  while (subst(N, 'w, 1) == 0, N = N / ('w - 1));
  N;
}
{
foreach([[2, 3], [3, 3], [2, 4]], v, my(R = farR(v[1], v[2]), S = numerator(subst(R, 'w, ('t + 1 / 't)^2 / 4)), f = factor(S));
  emit(Str("(n,k)=", v, " deg R=", poldegree(R), " pullback degree in t ", poldegree(S), " factor degrees over Q ", apply(x -> poldegree(x), f[, 1]~), " multiplicities ", f[, 2]~)));
}
