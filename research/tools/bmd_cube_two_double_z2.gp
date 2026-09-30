\\ Symbolic check of the proof of thm:cube-two-double-cross-limit (30 September 2026; cycle bmd-20260930-zv).
\\ With symbolic b1, b2, c1, c2, p1, p2 and X = v1/S^2, Y = v2/T^2 (S = (A+B)/2, T = (C+D)/2), it forms
\\ Z2 = XY - r eps (X - Y) - (t - s) r^2 eps^2 (X - Y), r = 1/(p1 - p2), and checks that its coefficients of
\\ eps^0..eps^3 vanish and that its eps^4 coefficient equals
\\ -r^2 (g1 u1^2 + g2 u2^2) + r^3 ((s - t)^2 + g1 + g2)(u1 - u2).  It also checks the exact identity
\\ (A - B)/2 = beta v1 / S, beta = (b2 - b1)/4, to order eps^4 (as (A - B)(A + B)/4 = beta v1).  The series
\\ variable eps is PARI's highest-priority variable x; u1, u2 are independent symbols U1, U2, and
\\ u_i = 1/(z - p_i) is substituted only into the eps-coefficients.
OUT = getenv("OUT");
emit(s) = print(s); if (OUT != 0 && OUT != "", write(OUT, s));
K = 4;
sq(w) = sum(a = 0, K, binomial(1/2, a) * w^a) + O(x^(K + 1));
main() = {
  my(u1 = 1 / ('z - 'p1), u2 = 1 / ('z - 'p2), r = 1 / ('p1 - 'p2), U(f) = substvec(f, ['U1, 'U2], [u1, u2]));
  my(A = sq(-'b1 * x * 'U1), B = sq(-'b2 * x * 'U1), C = sq(-'c1 * x * 'U2), D = sq(-'c2 * x * 'U2));
  my(S = (A + B) / 2, T = (C + D) / 2, X = x * 'U1 / S^2, Y = x * 'U2 / T^2);
  my(s = ('b1 + 'b2) / 2, t = ('c1 + 'c2) / 2, g1 = ('b1 - 'b2)^2 / 16, g2 = ('c1 - 'c2)^2 / 16);
  emit(Str("Delta identity holds to order eps^4: ", truncate((A - B) * (A + B) / 4 - ('b2 - 'b1) / 4 * x * 'U1) == 0));
  my(Z2 = X * Y - r * x * (X - Y) - (t - s) * r^2 * x^2 * (X - Y));
  for (k = 0, 3, emit(Str("eps^", k, " coefficient of Z2 vanishes: ", U(polcoef(Z2, k)) == 0)));
  my(pred = -r^2 * (g1 * u1^2 + g2 * u2^2) + r^3 * ((s - t)^2 + g1 + g2) * (u1 - u2));
  emit(Str("eps^4 coefficient equals the stated formula: ", U(polcoef(Z2, 4)) - pred == 0));
  \\ negative control: with the eps^2 correction omitted, the eps^3 coefficient must be nonzero when s != t
  my(Z1 = X * Y - r * x * (X - Y));
  emit(Str("control: eps^3 coefficient of Z1 is (t - s) r^2 (u1 - u2): ", U(polcoef(Z1, 3)) - (t - s) * r^2 * (u1 - u2) == 0));
}
main();
quit
