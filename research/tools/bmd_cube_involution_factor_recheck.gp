\\ Recheck of the involution identification of the six-root repeated factor (30 September 2026).
\\ bmd_cube_involution_factor.gp (29 September) compared J(u), built in the variable u, with the
\\ repeated factor G read from n6-repeated-factor-data.gp, which is a polynomial in x; PARI compares
\\ polynomials in different variables as unequal and takes their gcd as a constant, so its
\\ "J monic equals G: 0" and "gcd degree: 0" test nothing. This script repeats the comparison with both in u.
\\ Tested statement: on each line a(u) = alpha + u beta over F_p, p = 2^61 - 1, the monic exponent-four
\\ factor of D_nc equals the monic form of J(u) = prod over the 15 perfect matchings {ij,kl,mn} of
\\ det[1, a_i+a_j, a_i a_j; 1, a_k+a_l, a_k a_l; 1, a_m+a_n, a_m a_n].
\\ Input: DATA.gp from bmd_cube_repeated_factor_hyperplanes.py (seven lines, G in u) and the
\\ 29 September data file (G in x), both read here.
\\ Control: J against the exponent-one part is not available; instead J is compared with G of a
\\ different line, which must fail.
p = 2^61 - 1;
OUT = getenv("OUT");
emit(s) = print(s); if (OUT != 0 && OUT != "", write(OUT, s));
matchings(S) = {
  my(res = List(), rest);
  if (#S == 0, return([[]]));
  for (t = 2, #S,
    rest = vector(#S - 2); my(c = 0);
    for (s = 2, #S, if (s != t, c++; rest[c] = S[s]));
    foreach (matchings(rest), m, listput(res, concat([[S[1], S[t]]], m))));
  Vec(res);
}
M = matchings([1, 2, 3, 4, 5, 6]);
Jline(al, be) = {
  my(a = vector(6, i, Mod(al[i], p) + Mod(be[i], p) * 'u));
  my(J = prod(r = 1, #M, my(m = M[r]); matdet(matrix(3, 3, x, y, [1, a[m[x][1]] + a[m[x][2]], a[m[x][1]] * a[m[x][2]]][y]))));
  J / pollead(J);
}
monic(g) = my(h = Mod(1, p) * g); h / pollead(h);
main() = {
  read("research/results/bmd-20260930-r/lines/data.gp");
  emit(Str("matchings: ", #M));
  for (l = 1, #G,
    my(J = Jline(A[l, ], B[l, ]), g = monic(G[l]));
    emit(Str("line ", l, " (seed ", SEEDS[l], "): deg J = ", poldegree(J), ", J == G: ", J == g,
      "; control J == G of line ", l % #G + 1, ": ", J == monic(G[l % #G + 1]))));
  read("research/results/bmd-20260929-a/n6-repeated-factor-data.gp");
  my(g = monic(substpol(G, 'x, 'u)), J = Jline(alpha, beta));
  emit(Str("29 September data (G in variable ", variable(G), ", substituted into u): J == G: ", J == g));
}
main();
