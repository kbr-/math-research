\\ Rate dependence of a two-cluster neck limit (review test).
\\ Statement tested: the flat limit of the span of sqrt((z-a_i)(z-a_j)), i in a cluster of
\\ size m at q = 0, j in a cluster of size n at q' = 1, along the arc a_i = t*s_i,
\\ a_j = 1 + r*t*s'_j, is independent of the rate ratio r.  Elements are divided by
\\ S = sqrt(z(z-1)); coefficients are rational in z and in the symbolic ratio r.
\\ Output: for each r-specialization, the limit space as polynomials in z after clearing
\\ the denominator z^T (z-1)^T, and whether it equals the generic-r limit.

T = 12;           \\ t-adic precision
DEN = 12;         \\ denominator exponent bound

t; z; r;   \\ variable priority t > z > r

\\ element (1 - x/z)^(1/2) (1 - y/(z-1))^(1/2) with x = t*sx, y = r*t*sy, as t-series
elt(sx, sy, rr) = sqrt(1 - sx*t/z + O(t^(T+1))) * sqrt(1 - rr*sy*t/(z-1) + O(t^(T+1)));

\\ coefficient vector of a rational function of z over the constants, after multiplying by D
vecz(f) = my(p = simplify(f*z^DEN*(z-1)^DEN)); if(type(p) == "t_RFRAC" && poldegree(denominator(p), z) > 0, error("denominator ", denominator(p))); Vecrev(p, 2*DEN + 2);

\\ flat limit of the span of a list of t-series elements; returns (costs, limit vectors)
flatlim(E) = {
  my(k = #E, rows = vector(k, i, E[i]), cost = vector(k), M, K, c, piv, nr);
  for(iter = 1, 200,
    M = matrix(k, 2*DEN+2, i, j, vecz(polcoef(rows[i], 0, t))[j]);
    K = matker(M~);
    if(#K == 0, return([cost, vector(k, i, vecz(polcoef(rows[i], 0, t)))]));
    c = K[,1];
    \\ replace the row with the highest cost among those in the relation
    piv = 0; for(i = 1, k, if(c[i] != 0 && (piv == 0 || cost[i] > cost[piv]), piv = i));
    nr = sum(i = 1, k, c[i]*rows[i]);
    if(polcoef(nr, 0, t) != 0, error("relation not zero"));
    rows[piv] = nr/t; cost[piv]++;
  );
  error("no convergence");
}

samespace(A, B) = matrank(matconcat([Mat(A~), Mat(B~)])) == matrank(Mat(A~)) && matrank(Mat(A~)) == matrank(Mat(B~));

neck(sh1, sh2, rr) = {
  my(E = List());
  for(i = 1, #sh1, for(j = 1, #sh2, listput(E, elt(sh1[i], sh2[j], rr))));
  flatlim(Vec(E));
}

run() = {
  my(sh1 = [-1, 1], sh2 = [-1, 1], gen, res, rs = [2, 3, -1, 1, 1/2, I, -I, 5/7]);
  gen = neck(sh1, sh2, 3/11);
  print("(2,2) centered shapes; generic ratio 3/11: costs ", gen[1]);
  for(i = 1, #rs,
    res = neck(sh1, sh2, rs[i]);
    print("r = ", rs[i], ": costs ", res[1], " same as generic: ", samespace(res[2], gen[2])));
  \\ symbolic ratio: find the r where the generic limit changes
  res = neck(sh1, sh2, 'r);
  print("symbolic r costs: ", res[1]);
  print("limit vectors (symbolic r), content-free:");
  for(i = 1, #res[2], print("  ", content(res[2][i]), "  ", res[2][i]/content(res[2][i])));
}
run();

\\ Part 2: the tie polynomial (gcd of the 4x4 minors of the symbolic-r limit) and arcs with
\\ unequal exponents, compared with the generic limit.
eltg(sx, sy, cx, kx, cy, ky) = sqrt(1 - cx*sx*t^kx/z + O(t^(T+1))) * sqrt(1 - cy*sy*t^ky/(z-1) + O(t^(T+1)));
arc(sh1, sh2, cx, kx, cy, ky) = my(E = List()); for(i = 1, #sh1, for(j = 1, #sh2, listput(E, eltg(sh1[i], sh2[j], cx, kx, cy, ky)))); flatlim(Vec(E));
run2() = {
  my(sh1 = [-1, 1], sh2 = [-1, 1], res, M, g, gen);
  res = neck(sh1, sh2, 'r);
  M = matrix(#res[2], #res[2][1], i, j, res[2][i][j]); g = 0;
  forsubset([#M, 4], S, g = gcd(g, numerator(matdet(matrix(4, 4, i, j, M[i, S[j]])))));
  print("gcd of 4x4 minors in r: ", factor(g));
  gen = neck(sh1, sh2, 3/11);
  for(k = 2, 4, foreach([1, -1, 2], c,
    res = arc(sh1, sh2, 1, 1, c, k);
    print("l = t, m = ", c, " t^", k, ": costs ", res[1], " same as generic: ", samespace(res[2], gen[2]));
    res = arc(sh1, sh2, c, k, 1, 1);
    print("l = ", c, " t^", k, ", m = t: costs ", res[1], " same as generic: ", samespace(res[2], gen[2]))));
}
run2();

\\ Part 3: larger necks.  Arcs x_i = cx t^kx (s_i + t u_i), y_j = cy t^ky (s'_j + t u'_j), with
\\ shape drift u, u' (u = 0 for pure arcs); each limit is compared with the linear limit
\\ (kx = ky = 1, cx = cy = 1, no drift).
eltd(x, y) = sqrt(1 - x/z + O(t^(T+1))) * sqrt(1 - y/(z-1) + O(t^(T+1)));
arcd(sh1, sh2, cx, kx, u1, cy, ky, u2) = {
  my(E = List());
  for(i = 1, #sh1, for(j = 1, #sh2,
    listput(E, eltd(cx*t^kx*(sh1[i] + t*u1[i]), cy*t^ky*(sh2[j] + t*u2[j])))));
  flatlim(Vec(E));
}
run3() = {
  my(cases = [[[-1, 1], [-1, 0, 2]], [[-1, 0, 2], [-2, 1, 3]], [[-1, 1], [-3, -1, 1, 4]]],
     arcs = [[1, 1, 1, 1], [1, 1, 2, 1], [2, 1, 1, 1], [1, 1, 1, 2], [1, 2, 1, 1], [1, 1, 1, 3],
             [1, 3, 1, 1], [1, 2, 1, 3], [-3, 1, 2, 1], [1, 1, -1, 2]],
     sh1, sh2, gen, res, z1, z2, u1, u2);
  foreach(cases, cs, sh1 = cs[1]; sh2 = cs[2];
    z1 = vector(#sh1); z2 = vector(#sh2);
    gen = arcd(sh1, sh2, 1, 1, z1, 1, 1, z2);
    print("(", #sh1, ",", #sh2, ") shapes ", sh1, " ", sh2, ": linear costs ", gen[1], " total ", vecsum(gen[1]));
    foreach(arcs, a,
      res = arcd(sh1, sh2, a[1], a[2], z1, a[3], a[4], z2);
      print("  x = ", a[1], " t^", a[2], ", y = ", a[3], " t^", a[4], ": total cost ", vecsum(res[1]), " same: ", samespace(res[2], gen[2])));
    \\ shape drift
    u1 = vector(#sh1, i, i^2 - 2); u2 = vector(#sh2, j, 3 - j^2);
    foreach([[1, 1, 1, 1], [1, 1, 1, 2], [1, 2, 1, 1]], a,
      res = arcd(sh1, sh2, a[1], a[2], u1, a[3], a[4], u2);
      print("  drift, x = t^", a[2], ", y = t^", a[4], ": total cost ", vecsum(res[1]), " same: ", samespace(res[2], gen[2]))));
}
T = 30; DEN = 30;
run3();
