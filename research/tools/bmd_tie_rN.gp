\\ Tie coefficient from the explicit functional (7 October 2026; cycle bmd-20261007-c).  By
\\ thm:cube-tie-window-general-functional and thm:cube-tie-single-series-block, at x = c, y = 1, s = d = binom(m,2),
\\ N = d + 2m, the square tie minor is det N * r_N / rho_N with det N = K c^(md) (c-1)^(m^2) and
\\ r_N / rho_N = sum_i p_i (rho_(N-i)/rho_N) t_(N-i); here computed with the exponent lambda kept as the variable 'L.
\\ Prints, for each m, the stripped tie polynomial L_m(c; lambda) and the factorizations of its coefficients in lambda.
\\ Env MS (list of m), OUT.
OUT = getenv("OUT");
emit(s) = print(s); if (OUT != 0 && OUT != "", write(OUT, s));
bb(k) = if (k < 0, 0, prod(j = 0, k - 1, -'L - j) / k!);
{
\\ STARTS=[...] (optional): window starts s in place of binom(m,2); with GEG=1 the test is then r_(s+2m) / G_s.
foreach(eval(getenv("MS")), m,
 foreach(if (getenv("STARTS") != 0 && getenv("STARTS") != "", eval(getenv("STARTS")), [m * (m - 1) / 2]), s0,
  my(d = s0, N = d + 2 * m, P = ((1 + 'c * 'T) * (1 + 'T))^m, r = 0);
  if (s0 != m * (m - 1) / 2, emit(Str("start s=", s0)));
  for (i = 0, 2 * m,
    my(k = N - i, tk = sum(a = 0, k, bb(a) * bb(k - a) * 'c^a), ratio = k! / N! * prod(j = 1, i, N - j + 'L - m + 1));
    r += polcoef(P, i, 'T) * ratio * tk);
  \\ cycle bmd-20261007-d: record the stripped powers v (of c) and w (of c-1); the conjecture's form has v = m, w = 0
  my(vv = valuation(r, 'c), ww = 0);
  r = r / 'c^vv;
  while (subst(r, 'c, 1) == 0, r = r / ('c - 1); ww++);
  if (getenv("GEG") == "1", emit(Str("m=", m, " s=", s0, ": stripped powers v=", vv, " w=", ww, " (v = m: ", vv == m, ")")));
  \\ GEG=1: test r_N/rho_N = kappa(lambda) * c^m * (c-1)^0 * G_d(c), G_d = sum_k binom(d,k) (L)_k (L)_(d-k) c^k
  \\ (proportional to t_d, the coefficient of T^d in ((1+cT)(1+T))^(-L)); prints the quotient's c-degree.
  if (getenv("GEG") == "1",
    my(G = sum(k = 0, d, binomial(d, k) * prod(j = 0, k - 1, 'L + j) * prod(j = 0, d - k - 1, 'L + j) * 'c^k), q = r / G);
    emit(Str("m=", m, ": r / G_d is free of c: ", poldegree(numerator(q), 'c) == 0 && poldegree(denominator(q), 'c) == 0, "; quotient ", factor(q))));
  if (getenv("GEG") == "1", next);
  my(cs = Vecrev(r));
  emit(Str("m=", m, ": degree in c ", poldegree(r, 'c), "; coefficients of c^k (k = 0..) factored in lambda:"));
  for (k = 1, #cs, emit(Str("  k=", k - 1, ": ", factor(cs[k]))));
));
}
quit;
