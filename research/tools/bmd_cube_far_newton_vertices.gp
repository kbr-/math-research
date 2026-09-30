\\ Newton polygon vertices of the far polynomials W_k (30 September 2026; bmd-20260930-zl).
\\ Question: do the segments with large prime slope denominators, seen in review2-tests.txt, end at the extreme
\\ coefficients W_k(0) and lead(W_k)?  For (b,k) = (3,2),(4,2),(4,3) at c = 1 (exact over Q, with the definitions
\\ of bmd_cube_peeling_review2_tests.gp repeated below), print for every prime p <= deg the vertices
\\ (i, v_p(a_i)) of the lower convex hull of the points (i, v_p(a_i)), a_i = [x^i] W_k, whenever some segment has
\\ reduced slope denominator at least deg/4.
OUT = getenv("OUT");
emit(s) = print(s); if (OUT != 0 && OUT != "", write(OUT, s));
Rn(n) = n * (2 * n - 1);
md(N, c) = my(K = 2 * N - 4); -c * K + binomial(K, 2) - 3 + binomial(binomial(N - 2, 2), 2);
sum0(e, l) = -sum(j = 3, Rn(l) + 2, j) + sum(j = 0, Rn(e) + 4 * e, j) + sum(i = 4 * e - 4 * e * l, 4 * e + 4 * l - 1, i - 7/2);
sumatinf(e, l) = -binomial(Rn(e), 2) + sum(j = 3, Rn(l) + 4 * l + 3, j) + sum(i = -4 * e * l, 4 * e - 1, 7/2 - i);
blocks(e, l) = [[0, 0, Rn(e)], [-3, 0, 1], [0, -(Rn(l) + 2), Rn(l)], [-7/2, 0, 4 * e], [-5/2, 1/2 - 4 * l, 4 * l], [0, -7/2 + 4 * e - 4 * e * l, 4 * e * l]];
rowq(ga, be, j, c, x0, R) = {
  my(u = vector(R, a, binomial(be + j, a - 1) * x0^(j - a + 1)), r = c / (1 + c * x0));
  my(v = vector(R, s, binomial(ga, s - 1) * r^(s - 1)));
  vector(R, m, sum(a = 1, m, u[a] * v[m + 1 - a]));
}
Dq(e, l, c, x0) = {
  my(R = Rn(e + l + 1), rows = List());
  foreach (blocks(e, l), bl, for (j = 0, bl[3] - 1, listput(rows, rowq(bl[1], bl[2], j, c, x0, R))));
  matdet(Mat(Vec(rows)~));
}
Wexact(b, k) = {
  my(N = 2 * b, R = Rn(b), B = binomial(R, 2), Sc = md(N, 7/2), e = k - 1, l = b - k, c = 1);
  my(w0 = sum0(e, l) - B, wc = Sc - B, nF = B - Sc - sum0(e, l) - sumatinf(e, l));
  my(Sb = sum(i = 1, 6, blocks(e, l)[i][2] * blocks(e, l)[i][3]), Sg = sum(i = 1, 6, blocks(e, l)[i][1] * blocks(e, l)[i][3]));
  my(xs = vector(nF + 2, i, i + 1), ys = vector(nF + 2, i, Dq(e, l, c, xs[i]) * xs[i]^(Sb - w0) * (1 + c * xs[i])^(Sg - wc)));
  my(P = polinterpolate(xs[1..nF + 1], ys[1..nF + 1], 'x));
  if (subst(P, 'x, xs[nF + 2]) != ys[nF + 2], error("interpolation"));
  P;
}
hull(pts) = {
  my(h = List());
  foreach (pts, q,
    while (#h >= 2 && (h[#h][2] - h[#h - 1][2]) * (q[1] - h[#h - 1][1]) >= (q[2] - h[#h - 1][2]) * (h[#h][1] - h[#h - 1][1]), listpop(h));
    listput(h, q));
  Vec(h);
}
main() = {
  foreach ([[3, 2], [4, 2], [4, 3]], bk,
    my(P = Wexact(bk[1], bk[2]), d = poldegree(P), co = vector(poldegree(P) + 1, i, polcoef(P, i - 1)));
    emit(Str("b=", bk[1], " k=", bk[2], ": degree ", d));
    forprime (p = 2, d,
      my(pts = List());
      for (i = 0, d, if (co[i + 1] != 0, listput(pts, [i, valuation(co[i + 1], p)])));
      my(h = hull(Vec(pts)), big = List());
      for (j = 1, #h - 1, my(sl = (h[j + 1][2] - h[j][2]) / (h[j + 1][1] - h[j][1]));
        if (denominator(sl) >= d / 4, listput(big, [h[j][1], h[j + 1][1], sl])));
      if (#big, emit(Str("  p=", p, " vertices ", h, "; large-denominator segments [from, to, slope] ", Vec(big))))));
}
main();
quit
