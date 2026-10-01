\\ Newton polygons of the last even-peeling far polynomials (3 October 2026; cycle bmd-20261003-zj).
\\ Hypothesis tested (Eisenstein-type certificate): for each e there is a prime p(e) at which the primitive W_(b-1) in Z[x]
\\ (c = 1, b = e + 2) has Newton-polygon segments of slope u/v in lowest terms with v large; a segment of slope u/v and
\\ length v forces an irreducible factor of degree divisible by v over Q_p, so its v roots are distinct conjugates.
\\ Prints, for each prime p <= 400, the segments (slope, length) whose denominator is >= 5, and the total length so covered.
OUT = getenv("OUT");
emit(s) = print(s); if (OUT != 0 && OUT != "", write(OUT, s));
Rn(n) = n * (2 * n - 1);
farW(e, l, c) = {
  my(bl = [[0, 0, Rn(e)], [-3, 0, 1], [0, -(Rn(l) + 2), Rn(l)], [-7/2, 0, 4 * e], [-5/2, 1/2 - 4 * l, 4 * l], [0, -7/2 + 4 * e - 4 * e * l, 4 * e * l]]);
  my(d = sum(i = 1, 6, bl[i][3]), M = matrix(d, d), row = 0);
  foreach (bl, b, for (j = 0, b[3] - 1, row++; my(g = 'x^j);
    for (m = 1, d, M[row, m] = g; g = deriv(g, 'x) + (b[2] / 'x + b[1] * c / (1 + c * 'x)) * g)));
  my(N = numerator(matdet(M)));
  while (subst(N, 'x, 0) == 0, N = N / 'x); while (subst(N, 'x, -1/c) == 0, N = N / (1 + c * 'x));
  N = N * denominator(content(N)); N / content(N);
}
segs(P, p) = {
  my(s = newtonpoly(P, p), out = List(), i = 1, n = #s);
  while (i <= n, my(j = i); while (j < n && s[j + 1] == s[i], j++);
    listput(out, [s[i], j - i + 1]); i = j + 1);
  Vec(out);
}
main() = {
  for (e = 1, 3,
    my(W = farW(e, 1, 1), d = poldegree(W));
    emit(Str("e=", e, " b=", e + 2, " deg ", d, ":"));
    forprime (p = 2, 400,
      my(S = segs(W, p), big = select(t -> denominator(t[1]) >= 5, S));
      if (#big, emit(Str("  p=", p, ": segments with denominator >= 5 ", big, "; covered ", vecsum(apply(t -> t[2], big)), " of ", d)))));
}
default(parisizemax, 4000000000);
main();
