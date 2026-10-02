\\ Divisibility of the k = 1 kernel determinants (cycle bmd-20261009-u, 9 October 2026).
\\ Tested statement (candidate): for p = M - 1 (k = 1), the quotient D_{j}(u) / D_{0}(u) is a power series in u
\\ whose coefficients are polynomials in the roots y_1..y_M (symbolic), for the listed j, to order TT.
\\ D_T(u) = det[ negative columns n = 1..p | kernel columns K_u(z^i), i in T ] in coefficient space (z^0..z^{M-1}),
\\ negative column rem(sum_m c_m c_{n+m} u^(n+m) z^m, P), K_u(w) = sum_m u^m c_m rem(T_1^m(P w), P),
\\ as in prop:cube-kernel-arc-reduction. If true, omega(D_j) >= omega(D_0) on every arc (Gauss valuation).
\\ Recorded run: M = 2 only, where the quotient already fails to be polynomial. Runs at M = 3 (k = 1, 2)
\\ overflowed the default PARI stack and were dropped as unnecessary.
OUT = "research/results/bmd-20261009-u/k1-divisibility.txt";
Zv = varhigher("zz");
c(n) = binomial(-3/2, n);
T1(F) = { my(d = poldegree(F, Zv)); sum(i = 0, d, polcoef(F, i, Zv) * c(i + 1) / c(i) * Zv^(i + 1)) };
run(M, p, Ts, TT) = {
  my(Y = vector(M, s, eval(Str("y", s))), P = prod(s = 1, M, Zv - Y[s]), k = M - p);
  my(B = p * (p + 1) / 2 + p * (p - 1) / 2 + k, NU = B + TT);
  my(ncol = vector(p, n, my(r = lift(Mod(sum(m = 0, NU - n, c(m) * c(n + m) * 'u^(n + m) * Zv^m), P))); vector(M, s, polcoef(r, s - 1, Zv))));
  my(JM = vecmax(apply(vecmax, Ts)));
  my(kcol = vector(JM + 1, i, my(F = P * Zv^(i - 1), col = vector(M));
    for (m = 1, NU, F = T1(F); my(r = lift(Mod(F, P))); for (s = 0, M - 1, col[s + 1] += c(m) * polcoef(r, s, Zv) * 'u^m));
    col));
  my(D = vector(#Ts, t, my(T = Ts[t]); matdet(matrix(M, M, r, j, if(j <= p, ncol[j][r], kcol[T[j - p] + 1][r])))));
  my(lo = vector(#Ts, t, my(n = 0); while(polcoef(D[t], n, 'u) == 0 && n <= NU, n++); n));
  my(a0 = vector(TT + 1, n, polcoef(D[1], B + n - 1, 'u)));
  write(OUT, "M=", M, " p=", p, " k=", k, " B=", B, " orders B..B+", TT, "; lowest u-orders ", lo);
  write(OUT, "  lowest coefficient of D_T0: ", factor(a0[1]));
  for (t = 2, #Ts, my(a = vector(TT + 1, n, polcoef(D[t], B + n - 1, 'u)), qq = vector(TT + 1), ok = 1, first = -1);
    for (n = 1, TT + 1, my(s = a[n] - sum(i = 1, n - 1, qq[i] * a0[n - i + 1])); qq[n] = s / a0[1];
      if (type(qq[n]) == "t_RFRAC", ok = 0; if(first < 0, first = n - 1)));
    write(OUT, "  T=", Ts[t], ": quotient polynomial through order ", TT, ": ", if(ok, "yes", Str("no, first non-polynomial coefficient at order ", first)));
    write(OUT, "    q_0 = ", factor(qq[1])));
};
{
  run(2, 1, [[0], [1], [2], [3]], 6);
}
