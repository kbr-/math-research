\\ Are the peeling far polynomials W_k and the merge far polynomials R_(n,k) the same family? (3 October 2026;
\\ cycle bmd-20261003-ze.)  Degree coincidence: deg W_k = 48 at (b,k) = (4,2) and deg R_(4,4) = 48.  A Moebius bijection of
\\ the roots defined over Q is Galois-equivariant, so at a prime where both are squarefree of full degree the factor patterns
\\ (Frobenius cycle types) agree.  Compare the factor-degree
\\ patterns of R_(4,4) and of W_k at (4,2) (c = 2; the far-components script uses c = -3 at k = 2, which only rescales x since W_k(x; c) is proportional to W_k(cx; 1)) modulo several primes p.
OUT = getenv("OUT");
emit(s) = print(s); if (OUT != 0 && OUT != "", write(OUT, s));
thetastep(p, alpha, beta, e) = { (1 - 'w) * ('w * deriv(p, 'w) + (beta - e) * p) - alpha * 'w * p; }
strip(N, v) = { while (subst(N, v, 0) == 0, N = N / v); while (subst(N, v, 1) == 0, N = N / (v - 1)); N / pollead(N); }
wr(cls) = {
  my(d = sum(i = 1, #cls, #cls[i][3]), M = matrix(d, d), row = 0);
  foreach(cls, c, my(a = c[1], b = c[2]);
    foreach (c[3], f, row++; my(g = f);
      for (m = 1, d, M[row, m] = g; g = deriv(g, 'w) + (a / 'w + b / ('w - 1)) * g)));
  strip(numerator(matdet(M)), 'w);
}
farR(n, k) = {
  my(C = n * (n - 1) / 2, P = (k - 1) * (k - 2) / 2, E = concat(vector(C + P + 2, t, t - 1 - C), vector((k - 1) * n, t, 1/2 - (n - 1) + t - 1)), q = #E);
  my(P3 = vector(k - 1, j, my(p = 'w^(j - 1), al = 1/2); for (i = 1, q, p = thetastep(p, al, 0, E[i]); al--); p));
  my(P4 = vector(n, j, my(p = 'w^(j - 1), al = 1/2); for (i = 1, q, p = thetastep(p, al, 1/2 - (n - 1), E[i]); al--); p));
  wr([[0, 0, P3], [1/2, 0, apply(p -> p * 'w^(-(n - 1)), P4)]]);
}
\\ peeling far W_k over Q at (e,l) = (1,2), c = 2: exact Wronskian of the six blocks, factors x and 1+cx removed
Rn(n) = n * (2 * n - 1);
farW(e, l, c) = {
  my(bl = [[0, 0, Rn(e)], [-3, 0, 1], [0, -(Rn(l) + 2), Rn(l)], [-7/2, 0, 4 * e], [-5/2, 1/2 - 4 * l, 4 * l], [0, -7/2 + 4 * e - 4 * e * l, 4 * e * l]]);
  \\ log-derivative form: f = x^be (1+cx)^ga P(x); rows via the operator d + be/x + ga c/(1+cx)
  my(d = sum(i = 1, 6, bl[i][3]), M = matrix(d, d), row = 0);
  foreach (bl, b, for (j = 0, b[3] - 1, row++; my(g = 'x^j);
    for (m = 1, d, M[row, m] = g; g = deriv(g, 'x) + (b[2] / 'x + b[1] * c / (1 + c * 'x)) * g)));
  my(N = numerator(matdet(M)));
  while (subst(N, 'x, 0) == 0, N = N / 'x); while (subst(N, 'x, -1/c) == 0, N = N / (1 + c * 'x));
  N / pollead(N);
}
pat(P, p) = { my(F = factormod(P * denominator(content(P)), p)); vecsort(vector(#F~, i, poldegree(F[i, 1])), , 0); }
main() = {
  my(R = farR(4, 4), W = farW(1, 2, 2));
  emit(Str("deg R_(4,4) = ", poldegree(R), ", deg W_(4,2) = ", poldegree(W)));
  forprime (p = 101, 160, emit(Str("p=", p, ": R_(4,4) pattern ", pat(R, p), "; W pattern ", pat(W, p))));
}
default(parisizemax, 4000000000);
main();
