\\ Running-minimum form of kernel monomial minimality (cycle bmd-20261009-p, 9 October 2026); variant of
\\ bmd_monomial_minimality.gp (cycle bmd-20261009-k). Tested statement (candidate):
\\   val [u^n] D_T >= min_{n' <= n} val [u^(n')] D_{T0} for every k-set T in [0, 6] and n <= B + 5.
\\ The plain form (n' = n only) is counted for comparison; the single-shift columns are not used here.
\\ D_T(u) = det[ negative columns n = 1..p | kernel columns K_u(z^i), i in T ] in coefficient space (z^0..z^{M-1}),
\\ with negative column rem(sum_m c_m c_{n+m} u^(n+m) z^m, P) and K_u(w) = sum_m u^m c_m rem(T_1^m(P w), P).
\\ Tested statement (candidate): for every k-set T of nonnegative integers and every n,
\\   val [u^n] D_T >= val [u^n] D_{T0},  T0 = {0, ..., k-1}   (k = M - p).
\\ By Cauchy-Binet over the kernel basis this implies standard-negative order minimality. Also records the
\\ single-shift form: val [u^n] D_T >= val [u^n] D_{T - i + (i-1)} whenever i-1 is not in T.
\\ T ranges over k-subsets of [0, 6]; orders n up to B + 5, B = binom(p+1,2) + binom(p,2) + k. q-adic, q = 1000003.
OUT = "research/results/bmd-20261009-p/monomial-running-minimum.txt";
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
      mapput(Dv, T, vector(TT + 1, j, vq(polcoef(D, B + j - 1, 'u)))));
    my(T0 = [0 .. k - 1], v0 = mapget(Dv, T0), bad = 0, badshift = 0, tot = 0, ex = List());
    my(r0 = vector(TT + 1, j, vecmin(v0[1..j])));
    foreach(Mat(Dv)[, 1], T, my(v = mapget(Dv, T)); tot++;
      for (j = 1, TT + 1, if(v[j] < v0[j], badshift++); if(v[j] < r0[j], bad++; if(#ex < 4, listput(ex, [T, j - 1, v[j], r0[j]]))));
      );
    listput(res, [p, tot, v0, bad, badshift, ex]));
  write(OUT, name, " M=", M, ":");
  foreach(res, r, write(OUT, "  p=", r[1], ": ", r[2], " sets T, D_T0 valuations ", r[3], "; running-minimum violations ", r[4], ", plain-form violations ", r[5]);
    foreach(r[6], x, write(OUT, "   violation [T, t, val, val T0] = ", x)));
};
{
  my(e = q);
  my(cfg = [
    ["two cherries symmetric about 0", [1, 1 + e, -1, -1 - e + e^2]],
    ["pair and cherry, e_1 = eta", [1, -1 + e, 2, -2 + e^2]],
    ["nested cluster at +-1, e_1 = eta", [1, 1 + e^2, -1 + e, -1 + e + e^3]],
    ["symmetric pair, M = 2", [1, -1 + e]]]);
  for (i = 1, #cfg, run(cfg[i][1], cfg[i][2]));
}
