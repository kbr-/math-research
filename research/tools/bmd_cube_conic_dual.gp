\\ The rigid (trigonometric) form of the n = 2 conic determinants and their dual binomial series (bmd-r133).
\\
\\ Statement checked.  thm:cube-conic-duality: for n = 2 and any degree vector nu, in the coordinate mu of the
\\ conic with the points over T = infinity at 0 and infinity and the Klein group acting by mu -> -mu, 1/mu, -1/mu,
\\ V_nu is spanned by mu^m +- mu^(-m) over explicit frequency ranges, its dual (apolar) series S_nu in Poly_{2c} is
\\ spanned by the binomials mu^(c-m) -+ mu^(c+m) (or monomials) of the missing frequencies, and the non-collision
\\ zeros of Delta_nu(1, x) (a1 = 1, a2 = x) are the images under x = ((mu^2 - 1)/(mu^2 + 1))^2 = a2/a1 of the
\\ Weierstrass points of S_nu (the reciprocal image, also printed, gives the reversed polynomials),
\\ i.e. of the zeros of the Wronskian W(S_nu).  For each nu this script builds S_nu, factors W(S_nu), maps it to x by a
\\ resultant, and prints both next to the exact factorization of Delta_nu (bmd_cube_nu_factor_n2.gp).
\\ Frequencies: character (0,0): mu^m + mu^-m, m = 2k <= 2 nu_00; w1 = mu - 1/mu, character (1,0): mu^m - mu^-m, m odd
\\ <= 2 nu_10 + 1; w2 = mu + 1/mu, (0,1): mu^m + mu^-m, m odd <= 2 nu_01 + 1; (1,1): mu^m - mu^-m, m even, 2 <= m <=
\\ 2 nu_11 + 2.  c = max over present characters of the top frequency.
\\ Also, for d = 2..TRIPLEMAX (default 0 = skip): the triple-side quotient Q_d = W(S)/(mu^(8d-4) (t-1)^6 (t+1)),
\\ t = mu^4, for nu = (2d, 2d-2, 2d-2, 2d-4), with its degree, real roots, discriminant and value at t = -1.
\\ Usage: a driver file setting NUS=[...]; TRIPLEMAX=...; then read("research/tools/bmd_cube_conic_dual.gp"); quit;
NUS0 = NUS; NUS = []; if (type(TRIPLEMAX) == "t_POL", TRIPLEMAX = 0);
read("research/tools/bmd_cube_nu_factor_n2.gp");
NUS = NUS0;
dk(p, k) = { my(q = p); for (t = 1, k, q = deriv(q, 'm)); q };
wr(v) = { my(s = #v); matdet(matrix(s, s, i, j, dk(v[j], i - 1))) };
dualS(nu) = {
  my(tops = [2*nu[1], 2*nu[2] + 1, 2*nu[3] + 1, 2*nu[4] + 2], c = 0, S = List(), plus, minus);
  for (i = 1, 4, if (nu[i] >= 0, c = max(c, tops[i])));
  for (mm = 0, c,
    \\ which combos of mu^(c+mm), mu^(c-mm) does V contain?
    plus = if (mm % 2 == 0, nu[1] >= 0 && mm <= 2*nu[1], nu[3] >= 0 && mm <= 2*nu[3] + 1);
    minus = if (mm % 2 == 0, mm >= 2 && nu[4] >= 0 && mm <= 2*nu[4] + 2, nu[2] >= 0 && mm <= 2*nu[2] + 1);
    if (mm == 0, if (!plus, listput(S, 'm^c)); next);
    if (plus && !minus, listput(S, 'm^(c - mm) - 'm^(c + mm)));
    if (minus && !plus, listput(S, 'm^(c - mm) + 'm^(c + mm)));
    if (!plus && !minus, listput(S, 'm^(c - mm)); listput(S, 'm^(c + mm))));
  [c, Vec(S)];
}
{
  for (t = 1, #NUS,
    my(nu = NUS[t], cs = dualS(nu), W, R1, R2);
    W = wr(cs[2]); W = W / 'm^valuation(W, 'm);
    R1 = factor(polresultant(W, ('m^2 + 1)^2 * 'x - ('m^2 - 1)^2, 'm));
    R2 = factor(polresultant(W, ('m^2 - 1)^2 * 'x - ('m^2 + 1)^2, 'm));
    print("nu=", nu, " c=", cs[1], " dim S=", #cs[2], " W(S) factors: ", factor(W)[, 1]~, " mult ", factor(W)[, 2]~);
    print("   image x=((m^2-1)/(m^2+1))^2: ", R1[, 1]~, " mult ", R1[, 2]~);
    print("   image x=((m^2+1)/(m^2-1))^2: ", R2[, 1]~, " mult ", R2[, 2]~);
    my(F = factor(delta(nu))); print("   Delta_nu(1,x): ", F[, 1]~, " mult ", F[, 2]~));
}
{
  for (d = 2, TRIPLEMAX,
    my(S = dualS([2*d, 2*d-2, 2*d-2, 2*d-4])[2], W, Qt, Q, v);
    W = wr(S); v = valuation(W, 'm); W = W / 'm^v;
    Qt = substpol(W, 'm^4, 't); Q = Qt / ('t - 1)^6 / ('t + 1);
    print("triple side d=", d, ": valuation of W(S) = ", v, ", deg Q_d = ", poldegree(Q), ", real roots ", polsturm(Q),
          ", disc != 0: ", poldisc(Q) != 0, ", Q_d(-1) != 0: ", subst(Q, 't, -1) != 0));
}
