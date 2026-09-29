\\ Symbolic control of the second-order identity in lem:cube-double-cluster-osculating-limit (29 September 2026;
\\ cycle bmd-20260929-zzk). F(x,y) = phi(x) phi(y), phi(a) = (1 + aT)^(-3/2), kappa = (2/3)(x - y). With the divided
\\ differences A = (F(x+h,y) - F)/h, B = (F(x,y+k) - F)/k, C = (F(x+h,y+k) - F(x+h,y) - F(x,y+k) + F)/(hk) and
\\ E = A - B - kappa C, tested statement:
\\   (0) the Laplace equation F_x - F_y - kappa F_xy = 0;
\\   (1) G = E - [(5/6)(h - k) + 5/(108 kappa)(h^2 + k^2)] C + 1/(36 kappa)(h^2 F_xx + k^2 F_yy) has no term of total
\\       degree < 3 in (h, k), coefficientwise in T^0..T^M, with x, y symbolic;
\\   (2) negative control: the same with the h k cross term 1/(36 kappa) h k F_xy added is not O(3).
M = 8;
phi(a) = sum(n = 0, M, binomial(-3/2, n) * a^n * T^n);
F(a, b) = truncate(phi(a) * phi(b) + O(T^(M + 1)));
Fxy = F(x, y);
kap = 2/3 * (x - y);
L = deriv(Fxy, x) - deriv(Fxy, y) - kap * deriv(deriv(Fxy, x), y);
\\ only the coefficients of T^0..T^M are exact (T has lower variable priority than x, so products are not truncated)
print("(0) Laplace equation holds through T^M: ", vector(M + 1, n, polcoef(L, n - 1, T)) == vector(M + 1));
A = (F(x + h, y) - Fxy) / h; B = (F(x, y + k) - Fxy) / k;
C = (F(x + h, y + k) - F(x + h, y) - F(x, y + k) + Fxy) / (h * k);
E = A - B - kap * C;
G = E - (5/6 * (h - k) + 5 / (108 * kap) * (h^2 + k^2)) * C + 1 / (36 * kap) * (h^2 * deriv(deriv(Fxy, x), x) + k^2 * deriv(deriv(Fxy, y), y));
lowdeg(P) = { my(num = numerator(P), m = oo);
  for (n = 0, M, my(c = polcoef(num, n, T));
    if (c != 0, my(s = substvec(c, [h, k], [e * h, e * k])); m = min(m, valuation(s, e))));
  m; }
print("(1) least total (h,k)-degree in G: ", lowdeg(G));
G2 = G + 1 / (36 * kap) * h * k * deriv(deriv(Fxy, x), y);
print("(2) control with an added h k term: least degree ", lowdeg(G2));
