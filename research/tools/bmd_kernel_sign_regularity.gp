\\ Sign-regularity of the kernel determinants (cycle bmd-20261009-t, 9 October 2026).
\\ D_T(u) = det[standard negative columns | K_u(z^i), i in T] in coefficient space, as in bmd_monomial_minimality.gp.
\\ Tested statement (candidate, positivity lead of the kernel exchange review): at real roots and real u in a range,
\\ sign D_T is the same for all k-sets T (for fixed M, p, roots, u). Configurations: random positive roots, random
\\ roots of mixed sign, clusters near collision; u in {1/1000, 1/100, 1/20, 1/5}; M = 3, 4, 5; T in [0, 6].
\\ Exact rational evaluation of the truncated series at u (truncation NU = B + 16), and the sign is accepted only
\\ when the truncation error bound is small: the last computed coefficient's term is below 1e-6 of |D_T(u)|.
OUT = "research/results/bmd-20261009-t/kernel-sign-regularity.txt";
Zv = varhigher("zz");
c(n) = binomial(-3/2, n);
T1(F) = { my(d = poldegree(F, Zv)); sum(i = 0, d, polcoef(F, i, Zv) * c(i + 1) / c(i) * Zv^(i + 1)) };
cols(Y, p, NU, IMAX) = {
  my(M = #Y, P = prod(s = 1, M, Zv - Y[s]));
  my(ncol = vector(p, n, my(r = lift(Mod(sum(m = 0, NU - n, c(m) * c(n + m) * 'u^(n + m) * Zv^m), P))); vector(M, s, polcoef(r, s - 1, Zv))));
  my(kc = vector(IMAX + 1, a, my(F = P * Zv^(a - 1), col = vector(M));
    for (m = 1, NU, F = T1(F); my(r = lift(Mod(F, P))); for (s = 0, M - 1, col[s + 1] += c(m) * polcoef(r, s, Zv) * 'u^m)); col));
  [ncol, kc]
};
run(name, Y) = {
  my(M = #Y, line = Str(name, " roots ", Y, ":"));
  for (p = 1, M - 1, my(k = M - p, B = p * (p + 1) / 2 + p * (p - 1) / 2 + k, NU = B + 16, C = cols(Y, p, NU, 6));
    foreach([1/1000, 1/100, 1/20, 1/5], uu, my(pos = 0, neg = 0, unsure = 0);
      forsubset([7, k], S, my(T = Vec(S) - vector(k, a, 1));
        my(D = matdet(matrix(M, M, r, j, if(j <= p, C[1][j][r], C[2][T[j - p] + 1][r]))));
        my(val = subst(D, 'u, uu), tail = abs(polcoef(D, NU, 'u)) * uu^NU);
        if(val == 0 || tail > abs(val) * 10^-6, unsure++, if(val > 0, pos++, neg++)));
      line = Str(line, " [p=", p, " u=", uu, ": +", pos, " -", neg, if(unsure, Str(" ?", unsure), ""), "]")));
  write(OUT, line);
};
{
  setrand(11);
  foreach([3, 4, 5], M,
    for (r = 1, 3, run("positive", vecsort(vector(M, s, (random(40) + 1) / 7))));
    for (r = 1, 3, run("mixed sign", vecsort(vector(M, s, (random(81) - 40) / 7))));
    if(M >= 4, run("near collision", vecsort(concat([1, 1 + 1/50, 2, 2 + 1/40], vector(M - 4, s, 3 + s))))));
}
