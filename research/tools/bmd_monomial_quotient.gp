\\ Schur-type quotients of the kernel block (cycle bmd-20261009-k, 9 October 2026); variant of
\\ bmd_monomial_minimality.gp. Tested statement (candidate): S_T = D_T / D_{T0} is a power series in u whose
\\ coefficients are integral (q-adic valuation >= 0) up to order TT, for every k-set T in [0, 6].
\\ D_T(u) = det[ negative columns n = 1..p | kernel columns K_u(z^i), i in T ] in coefficient space (z^0..z^{M-1}),
\\ with negative column rem(sum_m c_m c_{n+m} u^(n+m) z^m, P) and K_u(w) = sum_m u^m c_m rem(T_1^m(P w), P).
\\ Tested statement (candidate): for every k-set T of nonnegative integers and every n,
\\   val [u^n] D_T >= val [u^n] D_{T0},  T0 = {0, ..., k-1}   (k = M - p).
\\ By Cauchy-Binet over the kernel basis this implies standard-negative order minimality. Also records the
\\ single-shift form: val [u^n] D_T >= val [u^n] D_{T - i + (i-1)} whenever i-1 is not in T.
\\ T ranges over k-subsets of [0, 6]; orders n up to B + 5, B = binom(p+1,2) + binom(p,2) + k. q-adic, q = 1000003.
OUT = "research/results/bmd-20261009-k/monomial-quotient.txt";
q = 1000003;
c(n) = binomial(-3/2, n);
vq(x) = if(x == 0, oo, valuation(x, q));
T1(F) = { my(d = poldegree(F, 'z)); sum(i = 0, d, polcoef(F, i, 'z) * c(i + 1) / c(i) * 'z^(i + 1)) };
run(name, Y) = {
  my(M = #Y, P = prod(s = 1, M, 'z - Y[s]), IMAX = 6, TT = 5);
  my(res = List());
  for (p = 1, M - 1, my(k = M - p, B = p * (p + 1) / 2 + p * (p - 1) / 2 + k, NU = B + TT);
    my(ncol = vector(p, n, my(r = lift(Mod(sum(m = 0, NU - n, c(m) * c(n + m) * 'u^(n + m) * 'z^m), P))); vector(M, s, polcoef(r, s - 1, 'z))));
    my(kcol = vector(IMAX + 1, i, my(F = P * 'z^(i - 1), col = vector(M));
      for (m = 1, NU, F = T1(F); my(r = lift(Mod(F, P))); for (s = 0, M - 1, col[s + 1] += c(m) * polcoef(r, s, 'z) * 'u^m));
      col));
    my(Dv = Map());
    forsubset([IMAX + 1, k], S, my(T = Vec(S) - vector(k, a, 1));
      my(A = matrix(M, M, r, j, if(j <= p, ncol[j][r], kcol[T[j - p] + 1][r])), D = matdet(A));
      mapput(Dv, T, D));
    my(T0 = [0 .. k - 1], D0 = mapget(Dv, T0), bad = 0, tot = 0, ex = List(), minv = oo);
    foreach(Mat(Dv)[, 1], T, my(S = (mapget(Dv, T) + O('u^(B + TT + 1))) / (D0 + O('u^(B + TT + 1)))); tot++;
      for (j = 0, TT, my(v = vq(polcoef(S, j, 'u))); minv = min(minv, v); if(v < 0, bad++; if(#ex < 4, listput(ex, [T, j, v])))));
    my(v0 = minv, badshift = 0);
    listput(res, [p, tot, v0, bad, badshift, ex]));
  write(OUT, name, " M=", M, ":");
  foreach(res, r, write(OUT, "  p=", r[1], ": ", r[2], " sets T, least valuation of a quotient coefficient ", r[3], "; negative valuations ", r[4]);
    foreach(r[6], x, write(OUT, "   negative [T, order, val] = ", x)));
};
{
  my(e = q);
  my(cfg = [
    ["nested cherries", [1, 1 + e, 1 + e + e^3, 3]],
    ["two separated cherries", [1, 1 + e, 2, 2 + e^2]],
    ["caterpillar cluster", [1, 1 + e, 1 + e + e^2, 1 + e + e^2 + e^3]],
    ["nested cherries over a cherry", [1, 1 + e, 1 + e + e^3, 3, 3 + e^2]]]);
  for (i = 1, #cfg, run(cfg[i][1], cfg[i][2]));
}
