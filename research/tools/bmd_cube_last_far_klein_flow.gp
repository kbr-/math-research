\\ Klein lift and KP flow of the last even-peeling far space F_(b-1) (3 October 2026; cycle bmd-20261003-zo).
\\ In x (c = 1, doubles at x = 0 and -1) the blocks are (1+x)^g x^b P_<cnt for
\\   [g, b, cnt] = [0,0,R_e], [-3,0,1], [0,-3,1], [-7/2,0,4e], [0,-7/2,4e], [-5/2,-7/2,4]  (R_e = e(2e-1)).
\\ With s = (t - 1/t)/2, c = (t + 1/t)/2 one has x = s^2, 1 + x = c^2, so D = c^7 s^7 times each function is a
\\ Laurent polynomial in t.  The theta-Wronskian (theta = t d/dt) is D^d (dx/dtheta)^binom(d,2) W_x o x, and dx/dtheta
\\ vanishes only at t = +-1, +-i; so off t in {0, oo, +-1, +-i} its zeros are the 4 preimages of each far point,
\\ with the same multiplicities (as in lem:cube-far-klein-tau).
\\ Question (Calogero-Moser lead, flow formulation): under the centred even KP flow a_m t^m -> a_m z^(m^2) t^m (which
\\ keeps the Klein symmetries), do zeros leave the branch preimages, i.e. is the rigid member a resonant point of
\\ its flow line?  Reports, for z = 1 (control: 4 deg W_(b-1) far zeros) and z = 2, 3, the branch valuations,
\\ the number of zeros off the branch preimages and whether they are simple.
OUT = getenv("OUT");
emit(s) = print(s); if (OUT != 0 && OUT != "", write(OUT, s));
Rn(n) = n * (2 * n - 1);
blocks(e) = [[0, 0, Rn(e)], [-3, 0, 1], [0, -3, 1], [-7/2, 0, 4 * e], [0, -7/2, 4 * e], [-5/2, -7/2, 4]];
kleinlift(e) = {
  my(s = (t - 1/t) / 2, c = (t + 1/t) / 2, L = List());
  foreach (blocks(e), B, for (j = 0, B[3] - 1, listput(L, c^(2 * B[1] + 7) * s^(2 * B[2] + 2 * j + 7))));
  Vec(L);
}
flow(f, z) = {
  my(K = 200, P = f * t^K, g = 0);
  for (i = 0, poldegree(P, t), my(a = polcoef(P, i, t)); if (a, my(m = i - K); g += a * z^(m^2) * t^m));
  g;
}
thetaW(V) = {
  my(d = #V, M = matrix(d, d));
  for (j = 1, d, my(h = V[j]); for (i = 1, d, M[i, j] = h; h = t * deriv(h, t)));
  matdet(M);
}
{
for (e = 1, 2,
  my(V = kleinlift(e), d = #V);
  emit(Str("e=", e, ": dimension ", d, " (R_b = ", Rn(e + 2), ")"));
  foreach ([1, 2, 3], z,
    my(W = thetaW(apply(f -> flow(f, z), V)), P = numerator(W), v0, v1, v2, Q, g);
    P = P / t^valuation(P, t);
    v1 = 0; while (P % (t^2 - 1) == 0, P /= (t^2 - 1); v1++);
    v2 = 0; while (P % (t^2 + 1) == 0, P /= (t^2 + 1); v2++);
    g = gcd(P, deriv(P));
    emit(Str("  z=", z, ": (t^2-1)-valuation ", v1, ", (t^2+1)-valuation ", v2, ", zeros off branch preimages ",
      poldegree(P), ", deg gcd(P, P') = ", poldegree(g),
      if (poldegree(subst(P, t, -t) - P) < 0, ", even", ""),
      if (poldegree(P - t^poldegree(P) * subst(P, t, 1/t)) < 0 || poldegree(P + t^poldegree(P) * subst(P, t, 1/t)) < 0, ", reciprocal", "")))));
}
