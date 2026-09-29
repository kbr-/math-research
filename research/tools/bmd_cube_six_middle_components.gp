\\ Simplicity of the N = 6 caterpillar middle components (29 September 2026; cycle bmd-20260929-z).
\\ Tested statement: the limit spaces predicted from the computed far-near windows,
\\   scale 2 (F=2, n=3): <1,S,S^2> + phi<1,S,S^2> + <S^-3> + S^-l phi<1,S^-1> + S^-l<S^-2..S^3>,
\\   scale 3 (F=3, n=2): <1> + phi<1,S> + S^-3<1,S^-1,S^-2> + S^-l phi<1,S^-1,S^-2> + S^-l<S^-3..S^2>,
\\ (l = 3/2, phi = (1 + c S)^-l) have 14 non-branch Weierstrass points each, all simple, at c = -3.
OUT = getenv("OUT");
emit(s) = print(s); if (OUT != 0 && OUT != "", write(OUT, s));
wronsk(fl) = {
  my(n = #fl, P = matrix(n, n));
  for (i = 1, n, my(L = sum(j = 1, #fl[i], fl[i][j][2] * deriv(fl[i][j][1], S) / fl[i][j][1]), p = 1); for (k = 1, n, P[k, i] = p; p = deriv(p, S) + p * L));
  numerator(matdet(P));
}
nb(fl, c) = {
  my(q = wronsk(fl));
  while (subst(q, S, 0) == 0, q = q / S);
  while (subst(q, S, -1 / c) == 0, q = q / (S + 1 / c));
  [poldegree(q), poldegree(gcd(q, deriv(q))) == 0];
}
main() = {
  my(c = -3, l = -3/2, ph = 1 + c * S);
  my(two = concat([[[[S, k]] | k <- [0, 1, 2]], [[[S, k], [ph, l]] | k <- [0, 1, 2]], [[[S, -3]]],
                   [[[S, l + k], [ph, l]] | k <- [0, -1]], [[[S, l + k]] | k <- [-2 .. 3]]]));
  my(three = concat([[[[S, 0]]], [[[S, k], [ph, l]] | k <- [0, 1]], [[[S, -3 + k]] | k <- [0, -1, -2]],
                     [[[S, l + k], [ph, l]] | k <- [0, -1, -2]], [[[S, l + k]] | k <- [-3 .. 2]]]));
  emit(Str("scale 2 (F=2, n=3): dimension ", #two, "; [non-branch degree, squarefree] = ", nb(two, c), "; predicted degree 14"));
  emit(Str("scale 3 (F=3, n=2): dimension ", #three, "; [non-branch degree, squarefree] = ", nb(three, c), "; predicted degree 14"));
}
main();
