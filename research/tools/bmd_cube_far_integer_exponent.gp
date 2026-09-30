\\ Integer-exponent far spaces (2 October 2026; cycle bmd-20261002-d).
\\ F^(h)(n,k): the far space with the square roots replaced by integer powers h (so p = 2h-1 relates it to F(n,k)
\\ modulo p through the polynomial model of bmd_cube_far_modp.gp).  Question: is R^(h) over Q squarefree with a
\\ discriminant whose prime factors are all below 2h-1 (which would give R_(n,k) squarefree modulo p = 2h-1)?
\\ Output: degree over Q, squarefreeness, real roots, the largest discriminant prime below 10^5 and the size of the
\\ remaining cofactor.
OUT = getenv("OUT");
emit(s) = print(s); if (OUT != 0 && OUT != "", write(OUT, s));
default(parisizemax, 2000000000);
Rh(n, k, h) = {
  my(C = n * (n - 1) / 2, P = (k - 1) * (k - 2) / 2);
  my(cls = concat(concat(vector(C + 2 + P, t, 'w^(t - 1 - C)), vector((k - 1) * n, t, 'w^(h - (n - 1) + t - 1))),
    concat(vector(k - 1, t, (1 - 'w)^h * 'w^(t - 1)), vector(n, t, 'w^(h - (n - 1) + t - 1) * (1 - 'w)^h))));
  my(d = #cls, M = matrix(d, d, i, j, 0));
  for (i = 1, d, my(g = cls[i]); for (j = 1, d, M[i, j] = g; g = deriv(g, 'w)));
  my(N = numerator(matdet(M)));
  while (poldegree(N) > 0 && subst(N, 'w, 0) == 0, N = N / 'w);
  while (poldegree(N) > 0 && subst(N, 'w, 1) == 0, N = N / ('w - 1));
  N;
}
{
foreach([[2, 3], [3, 3]], v, for (h = 7, 16, my(p = 2 * h - 1, R = Rh(v[1], v[2], h), P = R / content(R), D = abs(poldisc(P)), f = factor(D, 10^5), mx = vecmax(f[, 1]));
  emit(Str(v, " h=", h, " p=2h-1=", p, (if (isprime(p), " prime", " composite")), " deg ", poldegree(R), " squarefree ", issquarefree(R), " real roots ", polsturm(R),
    " disc: largest factor below 10^5 ", vecmax(select(x -> x < 10^5, f[, 1]~)), ", fully factored ", ispseudoprime(mx) || mx < 10^5, " last factor digits ", #Str(mx)))));
}
