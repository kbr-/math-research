\\ Cheap tests of the far-polynomial route review (3 October 2026; cycle bmd-20261003-n)
\\ (1) Filaseta combination: for each prime p <= deg R + 2, a factor of R over Q_p takes from each Newton segment of
\\     slope a/b (lowest terms) a multiple of b roots; so the possible factor degrees over Q are the intersection over p
\\     of the sets of sums of such multiples.  Irreducibility certificate iff only {0, deg} remain.
\\ (2) Galois group of R_(2,3) (degree 6) with polgalois.
OUT = getenv("OUT");
emit(s) = print(s); if (OUT != 0 && OUT != "", write(OUT, s));
thetastep(p, alpha, beta, e) = { (1 - 'w) * ('w * deriv(p, 'w) + (beta - e) * p) - alpha * 'w * p; }
stripw(N) = { while (subst(N, 'w, 0) == 0, N = N / 'w); while (subst(N, 'w, 1) == 0, N = N / ('w - 1)); N; }
wr(cls) = {
  my(d = sum(i = 1, #cls, #cls[i][3]), M = matrix(d, d), row = 0);
  foreach(cls, c, my(a = c[1], b = c[2]);
    foreach (c[3], f, row++; my(g = f);
      for (m = 1, d, M[row, m] = g; g = deriv(g, 'w) + (a / 'w + b / ('w - 1)) * g)));
  stripw(numerator(matdet(M)));
}
far(n, k) = {
  my(hh = 1/2, C = n * (n - 1) / 2, P = (k - 1) * (k - 2) / 2, E = concat(vector(C + P + 2, t, t - 1 - C), vector((k - 1) * n, t, hh - (n - 1) + t - 1)), q = #E);
  my(P3 = vector(k - 1, j, my(p = 'w^(j - 1), al = hh); for (i = 1, q, p = thetastep(p, al, 0, E[i]); al--); p));
  my(P4 = vector(n, j, my(p = 'w^(j - 1), al = hh); for (i = 1, q, p = thetastep(p, al, hh - (n - 1), E[i]); al--); p));
  my(R = wr([[0, 0, P3], [hh, 0, apply(p -> p * 'w^(-(n - 1)), P4)]]));
  R / content(R);
}
\\ allowed factor degrees at p: subset sums of segment contributions, segment of length L and slope denominator b
\\ contributes any multiple of b up to L
allowed(Q, p) = {
  my(S = newtonpoly(Q, p), d = poldegree(Q), A = vector(d + 1), segs = List(), c = 1);
  for (i = 2, #S + 1, if (i <= #S && S[i] == S[i - 1], c++, listput(segs, [denominator(S[i - 1]), c]); c = 1));
  A[1] = 1;
  foreach(segs, s, my(B = vector(d + 1)); for (x = 0, d, if (A[x + 1], forstep(y = 0, s[2], s[1], if (x + y <= d, B[x + y + 1] = 1)))); A = B);
  A;
}
main() = {
  foreach(eval(getenv("CASES")), v, my(R = far(v[1], v[2]), d = poldegree(R), A = vector(d + 1, i, 1));
    forprime(p = 2, d + 2, my(a = allowed(R, p)); A = vector(d + 1, i, A[i] && a[i]));
    my(deg = select(x -> x > 0 && x < d, vector(d + 1, i, if (A[i], i - 1, -1))));
    emit(Str("(n,k)=", v, ": deg ", d, "; proper factor degrees not excluded by Newton polygons at p <= deg+2: ", deg)));
  my(R = far(2, 3));
  emit(Str("Galois group of R_(2,3) (degree 6): ", polgalois(R)));
}
main();
quit
