\\ Factorization-pattern sieve for the merge far polynomials (5 October 2026; cycle bmd-20261005-n).
\\ For primes p not dividing the leading coefficient or the discriminant, a rational factor of R has degree equal to a
\\ subset sum of the degrees in R's factorization mod p.  Intersecting over primes < PMAX; an irreducible reduction settles
\\ irreducibility at once.  Output: remaining factor degrees, the first prime with an irreducible reduction (if any), and the
\\ proportion of primes with irreducible reduction.  Env NK, PMAX.
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
{
my(PM = eval(getenv("PMAX")));
foreach(eval(getenv("NK")), v,
  my(n = v[1], k = v[2], C = n * (n - 1) / 2, P = (k - 1) * (k - 2) / 2, t0 = getwalltime());
  my(E = concat(vector(C + P + 2, t, t - 1 - C), vector((k - 1) * n, t, 1/2 - (n - 1) + t - 1)));
  my(P3 = vector(k - 1, j, 'w^(j - 1) * closed(E, j - 1) / 'w^(P + 2)));
  my(P4 = vector(n, j, 'w^(j - 1) * closed(E, 1/2 - (n - 1) + j - 1) / 'w^((k - 1) * n)));
  my(R = wr2([[0, P3], [3/2 - n + (k - 1) * n - P - 2, P4]]), d = poldegree(R), S = vector(d + 1, i, 1), firstirr = 0, nirr = 0, nused = 0);
  my(D = poldisc(R), lc = pollead(R));
  forprime (p = 3, PM, if (lc % p == 0 || D % p == 0, next); nused++;
    my(f = factormod(R, p), degs = List()); for (i = 1, #f[, 1], for (m = 1, f[i, 2], listput(degs, poldegree(f[i, 1]))));
    if (#degs == 1, nirr++; if (!firstirr, firstirr = p));
    my(A = vector(d + 1)); A[1] = 1; foreach(degs, g, forstep (a = d, 0, -1, if (A[a + 1] && a + g <= d, A[a + g + 1] = 1)));
    S = vector(d + 1, i, S[i] && A[i]));
  my(rest = select(a -> a > 0 && a < d, vector(d + 1, i, if (S[i], i - 1, -1))));
  emit(Str("(n,k) = ", [n, k], ": deg R ", d, "; factor degrees not excluded: ", rest, if (#rest == 0, " -> IRREDUCIBLE", ""),
    "; first prime with irreducible reduction: ", firstirr, "; irreducible reductions ", nirr, " of ", nused, " primes (", getwalltime() - t0, " ms)")));
}
quit;
