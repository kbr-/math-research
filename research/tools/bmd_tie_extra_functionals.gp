\\ Moment form of the extra rows of the confluent tie window (7 October 2026; cycle bmd-20261007-zs).
\\ Tested statement (lem:cube-tie-window-moment-form): for x on the window columns k, with Z(s) = sum_k x_k (-1)^k s^k
\\ and the moment functionals l_a(s^j) = (a)_j / j! (0 for j < 0):
\\   sum_k x_k [T^k](1+T)^(-3)                      = (1/2) (s^2 Z)''(1)
\\   sum_k x_k [T^k]((1+T)(1+cT))^(-3/2)             = (l_(3/2) x l_(3/2)) [ (X Z(X) - cY Z(cY)) / (X - cY) ]
\\   sum_k x_k [T^k] T (1+T)^(-5/2) (1+cT)^(-3/2)    = -(l_(5/2) x l_(3/2)) [ (Z(X) - Z(cY)) / (X - cY) ]
\\ where the two-variable functionals act on polynomials in X, Y by l_a(X^i) l_b(Y^j).  Checks with random integer x,
\\ m = 1, 2, 3, symbolically in c.
OUT = getenv("OUT");
emit(s) = print(s); if (OUT != 0 && OUT != "", write(OUT, s));
bn(a, k) = if (k < 0, 0, binomial(a, k));
mom(a, j) = if (j < 0, 0, prod(z = 0, j - 1, a + z) / j!);
\\ apply l_a x l_b to a polynomial in X, Y
L2(a, b, F) = { my(s = 0, F1 = F); for (i = 0, poldegree(F1, 'X), my(G = polcoef(F1, i, 'X)); for (j = 0, poldegree(G, 'Y), s += mom(a, i) * mom(b, j) * polcoef(G, j, 'Y))); s; }
{
setrand(7);
for (m = 1, 3,
  my(d = m * (m - 1) / 2, w = 3 * m + 5, ks = vector(w, j, d + j - 1), x = vector(w, j, random(21) - 10), Z, ok = 1);
  Z = sum(j = 1, w, x[j] * (-1)^ks[j] * 's^ks[j]);
  my(r1 = sum(j = 1, w, x[j] * bn(-3, ks[j])), f1 = subst(deriv(deriv('s^2 * Z, 's), 's), 's, 1) / 2);
  my(r2 = sum(j = 1, w, x[j] * sum(a = 0, ks[j], bn(-3/2, a) * bn(-3/2, ks[j] - a) * 'c^(ks[j] - a))));
  my(ZX = subst(Z, 's, 'X), ZY = subst(Z, 's, 'c * 'Y));
  my(f2 = L2(3/2, 3/2, ('X * ZX - 'c * 'Y * ZY) / ('X - 'c * 'Y)));
  my(r3 = sum(j = 1, w, x[j] * sum(a = 0, ks[j] - 1, bn(-5/2, a) * bn(-3/2, ks[j] - 1 - a) * 'c^(ks[j] - 1 - a))));
  my(f3 = -L2(5/2, 3/2, (ZX - ZY) / ('X - 'c * 'Y)));
  emit(Str("m = ", m, ": (1+T)^(-3) row: ", r1 == f1, "; mixed row R2: ", r2 == f2, "; mixed row R3: ", r3 == f3)));
}
quit
