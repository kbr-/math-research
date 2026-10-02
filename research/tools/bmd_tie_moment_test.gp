\\ Moment form of the confluent tie pure block (7 October 2026; cycle bmd-20261007-ze).
\\ Tests two consequences of lem:cube-tie-window-moments.
\\ (1) The pure block equals, entrywise, the signed Pochhammer matrix of the functionals l_a(s^p) = (a)_p/p! and
\\     l_b^c(s^p) = c^p (b)_p/p! (the coefficient identity; m <= 4).
\\ (2) The Angelesco configuration c < 0: real roots of H_m in (-oo, 0), (0, 1), (1, oo), m = 2..5.  A negative root
\\     shows that the Angelesco normality theorem, which needs positive integrable weights, does not transfer.
OUT = getenv("OUT");
emit(str) = print(str); if (OUT != 0 && OUT != "", write(OUT, str));
bn(x, k) = if (k < 0, 0, binomial(x, k));
la(a, p) = if (p < 0, 0, gamma(a + p) / (gamma(a) * gamma(p + 1)));
strip01(f) = { if (f == 0, return(0)); while (subst(f, 'c, 0) == 0, f /= 'c); while (subst(f, 'c, 1) == 0, f /= ('c - 1)); f / content(f); }
pure(m) = { my(d = m * (m - 1) / 2);
  matrix(3*m, 3*m, r, j, my(k = d + j - 1); if (r <= 2*m, bn(-5/2, k - (r - 1)), my(n = r - 2*m - 1); bn(-3/2, k - n) * 'c^max(k - n, 0))); }
\\ moment matrix with exact Pochhammer ratios (a)_p / p! in place of the Gamma quotient
poch(a, p) = if (p < 0, 0, prod(z = 0, p - 1, a + z) / p!);
moment(m) = { my(d = m * (m - 1) / 2);
  matrix(3*m, 3*m, r, j, my(k = d + j - 1);
    if (r <= 2*m, my(i = r - 1); (-1)^(k - i) * poch(5/2, k - i), my(n = r - 2*m - 1); (-1)^(k - n) * poch(3/2, k - n) * 'c^max(k - n, 0))); }
{
for (m = 1, 4, emit(Str("(1) m = ", m, ": pure block equals moment matrix: ", pure(m) == moment(m))));
for (m = 2, 5, my(H = strip01(matdet(pure(m))));
  emit(Str("(2) m = ", m, ": H_m degree ", poldegree(H, 'c), ", real roots in (-oo,0), (0,1), (1,oo): ",
    polsturm(H, [-1 - vecmax(apply(abs, Vec(H))) / abs(pollead(H)), 0]), ", ", polsturm(H, [0, 1]), ", ", polsturm(H, [1, 1 + vecmax(apply(abs, Vec(H))) / abs(pollead(H))]))));
}
