\\ Reduced expansion for the cherry over a double root (7 October 2026; cycle bmd-20261007-zw).
\\ Rows as in bmd_cherry_double_windows.gp: block I = (V_q, and d_beta V for the double root), block E = U_eps (same).
\\ Reduction: E'(d V) = U d V + c_1 eps (lambda V + beta d V), which removes the r = 1 term of U d V (identity
\\ c_(t+1)(t+1) = -(lambda+t) c_t); a row operation, so every maximal minor is unchanged.
\\ Test: at every window [-j, 2M-1-j], compare the exact valuation with the two-block Laplace bound
\\   min over column splits S of  val det(I-block on S) + val det(E-block on complement),
\\ for the original E-block and for the reduced one.  Equality of the reduced bound with the exact valuation means no
\\ cancellation between Laplace terms after the reduction.
default(parisizemax, 2 * 10^9);
OUT = getenv("OUT");
emit(str) = print(str); if (OUT != 0 && OUT != "", write(OUT, str));
lam = 3/2;
cc(n) = if (n < 0, 0, binomial(-lam, n));
P = 1000003;
vv(x) = if (x == 0, oo, valuation(x, P));
build(roots, a, b, cols, red) = {
  my(R = 80, eps0 = -P^b / (1 + P^b), n = #cols, rI = List(), rE = List());
  foreach(roots, r, my(bb = P^(a + r[1]) * r[2]);
    my(V = vector(n, u, my(t = cols[u]); if (t >= 0, cc(t) * bb^t, 0)));
    my(UV = vector(n, u, my(t = cols[u]); sum(s = max(1, -t), R, cc(s) * eps0^s * if (t + s >= 0, cc(t + s) * bb^(t + s), 0))));
    listput(rI, V); listput(rE, UV);
    if (r[3],
      my(dV = vector(n, u, my(t = cols[u]); if (t >= 1, cc(t) * t * bb^(t - 1), 0)));
      my(UdV = vector(n, u, my(t = cols[u]); sum(s = max(1, -t), R, cc(s) * eps0^s * if (t + s >= 1, cc(t + s) * (t + s) * bb^(t + s - 1), 0))));
      listput(rI, dV);
      listput(rE, if (red, UdV + cc(1) * eps0 * (lam * V + bb * dV), UdV))));
  [Mat(Vec(rI)~), Mat(Vec(rE)~)];
}
laplacebound(I, E) = {
  my(M = #I[, 1], n = #I, best = oo);
  forsubset([n, M], S, my(Sv = Vec(S), C = select(u -> !setsearch(Set(Sv), u), [1 .. n]));
    my(v1 = vv(matdet(vecextract(I, "..", Sv)))); if (v1 < oo, my(v2 = vv(matdet(vecextract(E, "..", C)))); best = min(best, v1 + v2)));
  best;
}
{
foreach([
    [[[0, 3, 1], [2, -2, 0]], 1, 2], [[[0, 3, 1], [1, -2, 0], [3, 5, 0]], 1, 1], [[[0, 3, 0], [1, -2, 1], [3, 5, 0]], 1, 1],
    [[[0, 3, 0], [1, -2, 0], [2, 5, 1]], 1, 1], [[[0, 3, 1], [1, -2, 0], [3, 5, 0]], 1, 3], [[[0, 3, 0], [2, -2, 1], [3, 5, 0]], 2, 1]], c,
  my(roots = c[1], a = c[2], b = c[3], M = #roots + 1, out = List());
  for (j = 0, M, my(cols = [-j .. 2*M - 1 - j], B0 = build(roots, a, b, cols, 0), B1 = build(roots, a, b, cols, 1));
    my(ex = vv(matdet(matconcat([B0[1]; B0[2]]))), ex1 = vv(matdet(matconcat([B1[1]; B1[2]]))));
    listput(out, [j, ex, ex1 == ex, laplacebound(B0[1], B0[2]), laplacebound(B1[1], B1[2])]));
  emit(Str("roots ", roots, ", (a,b) = (", a, ",", b, "): [j, exact, reduced minor equal, original Laplace bound, reduced Laplace bound] = ", Vec(out))));
}
quit
