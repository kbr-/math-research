\\ The discriminant of the N = 5 caterpillar middle component in its modulus (29 September 2026; cycle
\\ bmd-20260929-zd). After scaling S, the middle component depends only on mu = kappa c3^4; take c3 = 1,
\\ phi = (1 + S)^-l, and the far-near combination S^2 + mu S^-2. Computes the non-branch Wronskian polynomial
\\ q(S; mu) with mu symbolic, its discriminant D(mu) in S, and the factorization of D. Tested question: is D
\\ squarefree (apart from factors where deg q drops or a root reaches a branch value)? If so, the collisions of
\\ Weierstrass points inside this component are ordinary and transverse in mu.
OUT = getenv("OUT");
emit(s) = print(s); if (OUT != 0 && OUT != "", write(OUT, s));
wronsk(fl) = {
  my(n = #fl, P = matrix(n, n));
  for (i = 1, n, my(L = sum(j = 1, #fl[i], fl[i][j][2] * deriv(fl[i][j][1], S) / fl[i][j][1]), p = 1); for (k = 1, n, P[k, i] = p; p = deriv(p, S) + p * L));
  numerator(matdet(P));
}
main() = {
  my(l = -3/2, ph = 1 + S);
  my(fl = [[[S, 0]], [[ph, l]], [[S, 1], [ph, l]], [[S, -3]], [[S, l], [ph, l]], [[S, l - 1], [ph, l]],
           [[S, l - 1]], [[S, l]], [[S, l + 1]], [[S, l - 2], [S^4 + mu, 1]]]);
  my(q = wronsk(fl));
  q = subst(q, x, x);
  my(g = content(q, S)); q = q / g;
  while (polcoef(q, 0, S) == 0, q = q / S);
  while (subst(q, S, -1) == 0, q = q / (S + 1));
  q = q / content(q);
  emit(Str("q: degree ", poldegree(q, S), " in S, degree ", poldegree(q, mu), " in mu; leading coefficient in S ", factor(pollead(q, S)),
    "; value at S=0 ", factor(subst(q, S, 0)), "; value at S=-1 ", factor(subst(q, S, -1))));
  my(D = poldisc(q, S), f = factor(D));
  emit(Str("discriminant: degree ", poldegree(D, mu), " in mu; factors [degree, multiplicity]: ", vector(#f~, i, [poldegree(f[i, 1], mu), f[i, 2]])));
  emit(Str("  factors of multiplicity > 1: ", [f[i, 1] | i <- [1 .. #f~], f[i, 2] > 1]));
}
main();
