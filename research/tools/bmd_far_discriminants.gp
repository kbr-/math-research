\\ Discriminants of the merge far polynomials (5 October 2026; cycle bmd-20261005-m).  Question: like classical
\\ orthogonal polynomials (Stieltjes-Hilbert discriminant formula for Jacobi polynomials), does disc R_(n,k) factor into
\\ small primes only, suggesting a product formula that would prove simplicity for every k?  R_(n,k) is the non-branch
\\ part of the Wronskian of P3' + w^gamma P4' (lem:cube-far-euler-image), equal to that of lem:cube-far-pure-reduction.
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
foreach(eval(getenv("NK")), v,
  my(n = v[1], k = v[2], C = n * (n - 1) / 2, P = (k - 1) * (k - 2) / 2, t0 = getwalltime());
  my(E = concat(vector(C + P + 2, t, t - 1 - C), vector((k - 1) * n, t, 1/2 - (n - 1) + t - 1)));
  my(P3 = vector(k - 1, j, 'w^(j - 1) * closed(E, j - 1) / 'w^(P + 2)));
  my(P4 = vector(n, j, 'w^(j - 1) * closed(E, 1/2 - (n - 1) + j - 1) / 'w^((k - 1) * n)));
  my(gam = 3/2 - n + (k - 1) * n - P - 2, R = wr2([[0, P3], [gam, apply(p -> p, P4)]]));
  my(D = poldisc(R), f = factor(abs(numerator(D))));
  emit(Str("(n,k) = ", [n, k], ": deg R ", poldegree(R), ", irreducible ", polisirreducible(R), ", largest prime of disc numerator ", vecmax(f[, 1]),
    ", primes ", #f[, 1], ", digits of disc ", #digits(abs(numerator(D))), " (", getwalltime() - t0, " ms)")));
}
quit;
