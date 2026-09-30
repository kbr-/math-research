\\ Far polynomials modulo p through a polynomial model (2 October 2026; cycle bmd-20261002-d).
\\ For an odd prime p, (1-w)^(1/2) = (1-w)^((p+1)/2) * ((1-w)^(-1/2))^p, and a p-th power has zero derivative in
\\ characteristic p.  So, modulo p, each class of F(n,k) is a p-th power (a constant for d/dw) times a space of
\\ Laurent polynomials: A1 = <w^-C..w^(1+P)>, A2p = w^((p+1)/2-(n-1)) Pol_(<(k-1)n), B3p = (1-w)^((p+1)/2) Pol_(<k-1),
\\ B4p = w^((p+1)/2-(n-1)) (1-w)^((p+1)/2) Pol_(<n).  Claim (lem:cube-far-modp-model): for p with W(F_p) != 0
\\ and p not dividing R(0)R(1), R_(n,k) mod p is the non-branch part of W(F_p) mod p.
\\ Test: compare with the exact R_(n,k) reduced mod p at several primes.
OUT = getenv("OUT");
emit(s) = print(s); if (OUT != 0 && OUT != "", write(OUT, s));
default(parisizemax, 2000000000);
strip(N) = { while (subst(N, 'w, 0) == 0, N = N / 'w); while (subst(N, 'w, 1) == 0, N = N / ('w - 1)); N / pollead(N); }
wr(cls) = {
  my(d = sum(i = 1, #cls, #cls[i][3]), M = matrix(d, d), row = 0);
  foreach(cls, c, my(a = c[1], b = c[2]);
    foreach (c[3], f, row++; my(g = f);
      for (m = 1, d, M[row, m] = g; g = deriv(g, 'w) + (a / 'w + b / ('w - 1)) * g)));
  strip(numerator(matdet(M)));
}
farR(n, k) = {
  my(C = n * (n - 1) / 2, P = (k - 1) * (k - 2) / 2);
  wr([[0, 0, vector(C + 2 + P, t, 'w^(t - 1 - C))], [1/2, 0, vector((k - 1) * n, t, 'w^(t - n))],
    [0, 1/2, vector(k - 1, t, 'w^(t - 1))], [1/2, 1/2, vector(n, t, 'w^(t - n))]]);
}
farRp(n, k, p) = {
  my(C = n * (n - 1) / 2, P = (k - 1) * (k - 2) / 2, h = (p + 1) / 2, u = Mod(1, p));
  my(cls = concat(concat(vector(C + 2 + P, t, 'w^(t - 1 - C)), vector((k - 1) * n, t, 'w^(h - (n - 1) + t - 1))),
    concat(vector(k - 1, t, (1 - 'w)^h * 'w^(t - 1)), vector(n, t, 'w^(h - (n - 1) + t - 1) * (1 - 'w)^h))) * u);
  my(d = #cls, M = matrix(d, d, i, j, 0));
  for (i = 1, d, my(g = cls[i]); for (j = 1, d, M[i, j] = g; g = deriv(g, 'w)));
  my(N = numerator(matdet(M)));
  while (poldegree(N) > 0 && subst(N, 'w, 0) == 0, N = N / 'w);
  while (poldegree(N) > 0 && subst(N, 'w, 1) == 0, N = N / ('w - 1));
  N / pollead(N);
}
{
foreach([[2, 3], [3, 3], [2, 4]], v, my(R = farR(v[1], v[2]), d = poldegree(R), dim = v[1] * (v[1] - 1) / 2 + 2 + (v[2] - 1) * (v[2] - 2) / 2 + v[2] * v[1] + v[2] - 1 - v[1] + v[1]);
  forprime(p = 29, 61, if (denominator(content(R)) % p != 0,
    my(Rp = farRp(v[1], v[2], p), ok = (Rp == R * Mod(1, p)));
    emit(Str("(n,k)=", v, " p=", p, ": polynomial model equals R mod p: ", ok, " (deg ", poldegree(Rp), " vs ", d, ")")))));
}
