\\ The N = 7 caterpillar middle components (29 September 2026; route review bmd-20260929-zb, falsification test).
\\ Tested predictions (prop:cube-caterpillar-component-count with the q-adic windows of
\\ bmd_cube_two_cluster_window_test.gp): the limit spaces
\\   scale 2 (F=2, n=4, window [-3,4]):
\\     Pol_<6 + phi Pol_<4 + <S^-3> + S^-l phi <1,S^-1> + S^-l <S^-3..S^4>,
\\   scale 3 (F=3, n=3, window [-4,4]):
\\     Pol_<3 + phi Pol_<3 + S^-3 <1,S^-1,S^-2> + S^-l phi <1,S^-1,S^-2> + S^-l <S^-4..S^4>,
\\ (l = 3/2, phi = (1 + c S)^-l, c = -3) have 24 and 30 non-branch Weierstrass points, and they are simple.
\\ Also prints the roots' moduli and arguments (reality/structure check for the route review's leads).
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
  q;
}
report(name, fl, c, pred) = {
  my(q = nb(fl, c), z = polroots(q));
  emit(Str(name, ": dimension ", #fl, "; non-branch degree ", poldegree(q), " (predicted ", pred, "); squarefree ", poldegree(gcd(q, deriv(q))) == 0,
    "; real roots ", #[w | w <- z, abs(imag(w)) < 1e-20]));
  emit(Str("  |S| sorted: ", apply(w -> round(w * 1000) / 1000., vecsort(apply(abs, z)))));
}
main() = {
  my(c = -3, l = -3/2, ph = 1 + c * S);
  my(two = concat([[[[S, k]] | k <- [0 .. 5]], [[[S, k], [ph, l]] | k <- [0 .. 3]], [[[S, -3]]],
                   [[[S, l + k], [ph, l]] | k <- [0, -1]], [[[S, l + k]] | k <- [-3 .. 4]]]));
  my(three = concat([[[[S, k]] | k <- [0 .. 2]], [[[S, k], [ph, l]] | k <- [0 .. 2]], [[[S, -3 + k]] | k <- [0, -1, -2]],
                     [[[S, l + k], [ph, l]] | k <- [0, -1, -2]], [[[S, l + k]] | k <- [-4 .. 4]]]));
  report("N=7 scale 2 (F=2, n=4)", two, c, 24);
  report("N=7 scale 3 (F=3, n=3)", three, c, 30);
}
main();
