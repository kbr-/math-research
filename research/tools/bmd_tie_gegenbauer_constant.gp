\\ Gegenbauer identity constant (7 October 2026; cycle bmd-20261007-g).  Tests whether
\\   sum_(i<=2m) p_i rho^(m)_(s+2m-i) t_(s+2m-i) = K_m * c^m * rho^(-m)_s * t_s
\\ with K_m independent of s, where p_i are the coefficients of ((1+cT)(1+T))^m, t_k those of ((1+cT)(1+T))^(-L),
\\ rho^(j)_k = Gamma(k+1)/Gamma(k+L-j+1).  The ratio LHS / (c^m rho^(-m)_s t_s) is computed exactly as a rational
\\ function of L (symbolic exponent) and printed for each s.  Env MS, SS (lists), OUT.
OUT = getenv("OUT");
emit(s) = print(s); if (OUT != 0 && OUT != "", write(OUT, s));
bb(k) = if (k < 0, 0, prod(j = 0, k - 1, -'L - j) / k!);
tk(k) = sum(a = 0, k, bb(a) * bb(k - a) * 'c^a);
\\ rho^(j)_k as an explicit rational function of L, relative to the common factor 1/Gamma(L+1): Gamma(L+1)/Gamma(k+L-j+1)
\\ = 1 / prod_(i=1..k-j) (L+i) for k-j >= 0, and prod_(i=0..j-k-1)(L-i) otherwise.
rho(j, k) = k! * if (k - j >= 0, 1 / prod(i = 1, k - j, 'L + i), prod(i = 0, j - k - 1, 'L - i));
{
foreach(eval(getenv("MS")), m,
  my(P = ((1 + 'c * 'T) * (1 + 'T))^m, res = List());
  foreach(eval(getenv("SS")), s,
    my(N = s + 2 * m, lhs = sum(i = 0, 2 * m, polcoef(P, i, 'T) * rho(m, N - i) * tk(N - i)), q = lhs / ('c^m * rho(-m, s) * tk(s)));
    listput(res, [s, q]));
  emit(Str("m=", m, ": ratio free of c and s: ", #Set(apply(x -> x[2], Vec(res))) == 1 && poldegree(numerator(res[1][2]), 'c) == 0,
    "; K_m = ", factor(res[1][2]))));
}
quit;
