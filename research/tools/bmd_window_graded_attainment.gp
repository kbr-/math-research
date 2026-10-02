\\ Window graded attainment (8 October 2026; cycle bmd-20261008-zy).
\\ Tested statement (question): for the windows Lambda_p = [-p, 2M-1-p], 1 <= p <= M-1, k = M - p, does the
\\ u^(B_p+t) coefficient of P_Lambda attain the graded bound of thm:cube-graded-hankel-penalty,
\\ val = 2 val Vand(y) + g(max(k - t, 0)), for t = 0..k? Prints the excess per t (0 = attained).
\\ Points: integer polynomials in eta = q = 1000003 (cluster trees); q-adic reading (excess >= 0 is forced by the
\\ theorem; an excess > 0 here means non-attainment up to accidental q-divisibility).
OUT = "research/results/bmd-20261008-zy/window-graded-attainment.txt";
q = 1000003;
c(n) = if(n < 0, 0, binomial(-3/2, n));
vand(Y) = prod(a = 1, #Y, prod(b = a + 1, #Y, Y[b] - Y[a]));
vq(x) = if(x == 0, oo, valuation(x, q));
g(Y, k) = { my(best = oo); forsubset([#Y, k + 1], S, best = min(best, 2 * vq(vand(vecextract(Y, Vec(S)))))); best };
wintest(name, Y) = {
  my(M = #Y, V2 = 2 * vq(vand(Y)));
  for (p = 1, M - 1,
    my(k = M - p, L = vector(2 * M, i, -p - 1 + i), B = p * (p - 1) / 2 + p * (p + 1) / 2 + k, ex = vector(k + 1));
    my(X = matrix(2 * M, 2 * M, r, i, my(t = L[i]);
      if(r <= M, if(t >= 0, c(t) * Y[r]^t, 0),
        my(s = r - M); sum(m = max(1, -t), B + k + 1, c(m) * c(t + m) * Y[s]^(t + m) * 'u^m))));
    my(D = matdet(X));
    for (t = 0, k, ex[t + 1] = vq(polcoef(D, B + t, 'u)) - V2 - g(Y, max(k - t, 0)));
    write(OUT, name, " M=", M, " p=", p, " k=", k, ": g(k-t) for t=0..k: ", vector(k + 1, t, g(Y, max(k - t + 1, 0))), "; excess per t: ", ex));
};
{
  my(e = 'e);
  my(cfg = [
    ["cherry top", [1, 1 + e, 2, 5]],
    ["nested cherries", [1, 1 + e, 1 + e + e^3, 3]],
    ["two separated cherries", [1, 1 + e, 2, 2 + e^2]],
    ["tie over cherry", [2, 1, 3 * e, 3 * e + 5 * e^2]],
    ["cherry top", [1, 1 + e, 2, 5, 7]],
    ["nested cherries", [1, 1 + e, 1 + e + e^3, 3, 4]],
    ["tie over cherry", [2, 1, 3 * e, 3 * e + 5 * e^2, 7 * e^3]],
    ["three-root cluster", [1, 1 + e, 1 + 3 * e, 4, 6]],
    ["cherry over deep cherry", [1, 1 + e, 2 * e^2, 3 * e^3, 4]]]);
  foreach([1000003, 1000033], qq, q = qq; write(OUT, "prime ", q);
    for (i = 1, #cfg, wintest(cfg[i][1], subst(cfg[i][2], 'e, q))));
}
