\\ Newton-polygon degree sieve for the merge far polynomials (5 October 2026; cycle bmd-20261005-n).
\\ Conjecture tested: conj:cube-merge-far-irreducible, R_(n,k) irreducible over Q for n >= 2, k >= 3 (implies far simplicity).
\\ Dumas: a factor of degree d has Newton polygon made of pieces of the segments of R's polygon, each piece a multiple of
\\ the segment's slope denominator in length.  Allowed degrees at p = subset sums of such pieces.  Intersecting over primes
\\ p < PMAX, if only 0 and deg R remain, R is irreducible.  Output: degree, remaining factor degrees, and the primes that
\\ removed degrees (with their slope denominators).  Env NK, PMAX.
default(parisizemax, 4000000000);
OUT = getenv("OUT");
emit(s) = print(s); if (OUT != 0 && OUT != "", write(OUT, s));
closed(E, s) = {
  my(q = #E, phi = x -> prod(i = 1, q, x - E[i]));
  sum(r = 0, q, sum(i = 0, r, (-1)^(r - i) * binomial(r, i) * phi(s + i)) * binomial(1/2, r) * (-1)^r * 'w^r * (1 - 'w)^(q - r));
}
strip(N) = { while (subst(N, 'w, 0) == 0, N = N / 'w); while (subst(N, 'w, 1) == 0, N = N / ('w - 1)); N / content(N); }
wr2(cls) = {
  my(d = sum(i = 1, #cls, #cls[i][2]), M = matrix(d, d), row = 0);
  foreach(cls, c, my(a = c[1]); foreach (c[2], f, row++; my(g = f);
    for (m = 1, d, M[row, m] = g; g = deriv(g, 'w) + (a / 'w) * g)));
  strip(numerator(matdet(M)));
}
allowed(R, p) = {
  my(d = poldegree(R), sl = newtonpoly(R, p), S = vector(d + 1), i = 1);
  S[1] = 1;
  while (i <= #sl, my(j = i); while (j < #sl && sl[j + 1] == sl[i], j++);
    my(L = j - i + 1, e = denominator(sl[i]), T = vector(d + 1));
    for (a = 0, d, if (S[a + 1], forstep (b = 0, L, e, if (a + b <= d, T[a + b + 1] = 1))));
    S = T; i = j + 1);
  S;
}
{
my(PM = eval(getenv("PMAX")));
foreach(eval(getenv("NK")), v,
  my(n = v[1], k = v[2], C = n * (n - 1) / 2, P = (k - 1) * (k - 2) / 2, t0 = getwalltime());
  my(E = concat(vector(C + P + 2, t, t - 1 - C), vector((k - 1) * n, t, 1/2 - (n - 1) + t - 1)));
  my(P3 = vector(k - 1, j, 'w^(j - 1) * closed(E, j - 1) / 'w^(P + 2)));
  my(P4 = vector(n, j, 'w^(j - 1) * closed(E, 1/2 - (n - 1) + j - 1) / 'w^((k - 1) * n)));
  my(R = wr2([[0, P3], [3/2 - n + (k - 1) * n - P - 2, P4]]), d = poldegree(R), S = vector(d + 1, i, 1), useful = List());
  forprime (p = 2, PM, my(A = allowed(R, p), before = sum(i = 2, d, S[i])); S = vector(d + 1, i, S[i] && A[i]);
    if (sum(i = 2, d, S[i]) < before, listput(useful, [p, vecmax(apply(denominator, newtonpoly(R, p)))])));
  my(rest = select(a -> a > 0 && a < d, vector(d + 1, i, if (S[i], i - 1, -1))));
  emit(Str("(n,k) = ", [n, k], ": deg R ", d, "; factor degrees not excluded by primes < ", PM, ": ", rest,
    if (#rest == 0, " -> IRREDUCIBLE by the sieve", ""), "; primes that removed degrees [p, max slope denominator]: ", Vec(useful), " (", getwalltime() - t0, " ms)")));
}
quit;
