\\ Cheap tests of the route review bmd-20260929-zb (29 September 2026).
\\ (a) Factorization over Q of the non-branch Wronskian polynomial of the N = 5 middle component at c3 = -3,
\\     kappa = 1/100 (does it split into pieces, as a structural mechanism would suggest?).
\\ (b) Superregularity of a generic 2 x 3 product block: rows (1 + s_i/S)^(-3/2)(1 + t_j S)^(-3/2) with random
\\     rational constants of size about 1/10 (no scale separation), coefficient columns e in [-5, 5]; counts the
\\     6 x 6 minors that vanish exactly.
OUT = getenv("OUT");
emit(s) = print(s); if (OUT != 0 && OUT != "", write(OUT, s));
be(n) = binomial(-3/2, n);
wronsk(fl) = {
  my(n = #fl, P = matrix(n, n));
  for (i = 1, n, my(L = sum(j = 1, #fl[i], fl[i][j][2] * deriv(fl[i][j][1], S) / fl[i][j][1]), p = 1); for (k = 1, n, P[k, i] = p; p = deriv(p, S) + p * L));
  numerator(matdet(P));
}
row(s, t, L, K) = vector(2 * L + 1, c, my(ee = c - L - 1); sum(a = max(0, -ee), K, my(b = a + ee); if (b > K, 0, be(a) * be(b) * s^a * t^b)));
main() = {
  my(c = -3, l = -3/2, ph = 1 + c * S, kap = 1/100);
  my(fl = [[[S, 0]], [[ph, l]], [[S, 1], [ph, l]], [[S, -3]], [[S, l], [ph, l]], [[S, l - 1], [ph, l]],
           [[S, l - 1]], [[S, l]], [[S, l + 1]], [[S, l - 2], [S^4 + kap, 1]]]);
  my(q = wronsk(fl));
  while (subst(q, S, 0) == 0, q = q / S);
  while (subst(q, S, -1 / c) == 0, q = q / (S + 1 / c));
  my(f = factor(q));
  emit(Str("(a) N=5 middle component: degree ", poldegree(q), "; irreducible factor degrees over Q: ", vector(#f~, i, [poldegree(f[i, 1]), f[i, 2]])));
  setrand(5);
  my(sv = vector(2, i, (random(90) + 10) / 1000), tv = vector(3, j, (random(90) + 10) / 1000), rows = List(), L = 5, K = 16);
  foreach (sv, s, foreach (tv, t, listput(rows, row(s, t, L, K))));
  my(A = matrix(6, 2 * L + 1, i, j, rows[i][j]), tot = 0, zero = 0);
  forsubset([2 * L + 1, 6], E, tot++; if (matdet(matrix(6, 6, i, j, A[i, E[j]])) == 0, zero++));
  emit(Str("(b) generic 2x3 product block (truncated at degree ", K, "): ", tot, " minors on columns in [-5,5], exactly zero: ", zero));
}
main();
