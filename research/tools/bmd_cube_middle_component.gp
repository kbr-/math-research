\\ The middle component of the N = 5 caterpillar (29 September 2026; cycle bmd-20260929-y).
\\ Tested statement: at scale |T| ~ eps^-2 (S = eps^2 T, visible root a3 = c3 eps^2), the normalized pair space
\\ tends to V = <1> + phi<1,S> + <S^-3> + S^-l phi<1,S^-1> + S^-l <S^-1, 1, S, S^2 + kappa S^-2>, l = 3/2,
\\ phi = (1 + c3 S)^-l, where the far-near block has two minimizing exponent sets {-2..1}, {-1..2} and
\\ kappa = -p1/p2 is the ratio of their leading Pluecker coefficients. Its Weierstrass points predict the
\\ scale-2 exponents 2 + log|S0|/log(1/eps) of the saved caterpillar run (c = (1,2,-3,5,-7), eps = 1e-6, 1e-8).
\\ Prints kappa, the non-branch degree of the Wronskian of V (predicted 12), squarefreeness, and the
\\ predicted exponents at both eps.
OUT = getenv("OUT");
emit(s) = print(s); if (OUT != 0 && OUT != "", write(OUT, s));
\p 60
be(n) = binomial(-3/2, n);
row(s, t, L, K) = vector(2 * L + 1, c, my(ee = c - L - 1); sum(a = max(0, -ee), K, my(b = a + ee); if (b > K, 0, be(a) * be(b) * s^a * t^b)));
wronsk(fl) = {
  my(n = #fl, P = matrix(n, n));
  for (i = 1, n, my(L = sum(j = 1, #fl[i], fl[i][j][2] * deriv(fl[i][j][1], S) / fl[i][j][1]), p = 1); for (k = 1, n, P[k, i] = p; p = deriv(p, S) + p * L));
  numerator(matdet(P));
}
main() = {
  my(c = [1, 2, -3, 5, -7], L = 4, K = 12);
  my(sv = [e^2 / c[1], e / c[2]], tv = [c[4] * e, c[5] * e^2], rows = List());
  foreach (sv, s, foreach (tv, t, listput(rows, row(s, t, L, K))));
  my(A = matrix(4, 2 * L + 1, i, j, rows[i][j]), col = x -> x + L + 1);
  my(d1 = matdet(matrix(4, 4, i, j, A[i, col([-2, -1, 0, 1][j])])), d2 = matdet(matrix(4, 4, i, j, A[i, col([-1, 0, 1, 2][j])])));
  my(v1 = valuation(d1, e), v2 = valuation(d2, e), kap = -polcoef(d1, v1, e) / polcoef(d2, v2, e));
  emit(Str("valuations ", [v1, v2], "; kappa = ", kap));
  my(l = -3/2, ph = 1 + c[3] * S);
  my(fl = [[[S, 0]], [[ph, l]], [[S, 1], [ph, l]], [[S, -3]], [[S, l], [ph, l]], [[S, l - 1], [ph, l]],
           [[S, l - 1]], [[S, l]], [[S, l + 1]], [[S, l - 2], [S^4 + kap, 1]]]);
  my(q = wronsk(fl));
  while (subst(q, S, 0) == 0, q = q / S);
  while (subst(q, S, -1 / c[3]) == 0, q = q / (S + 1 / c[3]));
  my(z = polroots(q));
  emit(Str("non-branch degree ", poldegree(q), " (predicted 12); squarefree ", poldegree(gcd(q, deriv(q))) == 0));
  foreach ([10^-6, 10^-8], eps, emit(Str("eps=", eps, ": predicted scale-2 exponents ", apply(x -> round(x * 1000) / 1000., vecsort(vector(#z, i, 2 + log(abs(z[i])) / log(1 / eps)))))));
}
main();
