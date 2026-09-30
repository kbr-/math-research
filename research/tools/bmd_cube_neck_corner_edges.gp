\\ Edge limits of neck corner Newton polygons (1 October 2026; cycle bmd-20261001-k).
\\ Setting of bmd_cube_neck_corner_limits.gp: neck (m,n), V = < A(x_i) B(y_j) >, x = lambda s, y = lambda' s',
\\ along lambda = rho t^w1, lambda' = rho' t^w2.  conj:cube-neck-corner-antidiagonal-polygon predicts edges
\\ [v_r, v_(r+1)] with vector (c, -(mn - c)); at the primitive normal w = (mn - c, c)/g, g = gcd(c, mn), the
\\ flat limit H lies in L((alpha+1)[0] + beta[1]), alpha = m - 1 + r, beta = mn - 1 - alpha.
\\ Questions tested, for each edge and several (rho, rho'):
\\  (i) pencil: does H contain L(alpha[0] + (beta-1)[1]) (dimension mn - 1)?  Then H is determined by the ratio
\\      kappa = c1/c0 of the top principal-part coefficients (z^-(alpha+1) at 0, (z-1)^-beta at 1) of any
\\      element of H outside L(alpha[0] + (beta-1)[1]);
\\  (ii) face form: kappa as a function of (rho, rho'): the ratios kappa(rho,rho')/kappa(1,1) are printed with
\\      the monomial law is tested by bmd_cube_neck_corner_edges_check.py; zero or infinite kappa at finite
\\      nonzero (rho, rho') would be a zero ratio of the edge form.
\\ Output per edge: the edge data, containment flags and kappa for each coefficient pair.
default(threadsizemax, 300000000); default(parisizemax, 1000000000);
OUT = getenv("OUT");
emit(s) = print(s); if (OUT != 0 && OUT != "", write(OUT, s));
t; z;
T = if (getenv("TT") != 0 && getenv("TT") != "", eval(getenv("TT")), 128); DEN = T;
vecz(f) = my(p = simplify(f*z^DEN*(z-1)^DEN)); if(type(p) == "t_RFRAC" && poldegree(denominator(p), z) > 0, error("denominator")); Vecrev(p, 2*DEN + 2);
reduce(E) = {
  my(k = #E, rows = E, cost = vector(k), M, K, cc, piv, nr);
  for(iter = 1, 4000,
    M = matrix(k, 2*DEN+2, i, j, vecz(polcoef(rows[i], 0, t))[j]);
    K = matker(M~);
    if(#K == 0, return([vecsum(cost), vector(k, i, polcoef(rows[i], 0, t))]));
    cc = K[,1];
    piv = 0; for(i = 1, k, if(cc[i] != 0 && (piv == 0 || cost[i] > cost[piv]), piv = i));
    nr = sum(i = 1, k, cc[i]*rows[i]);
    if(polcoef(nr, 0, t) != 0, error("relation not zero"));
    rows[piv] = nr/t; cost[piv]++;
    if(cost[piv] > T - 8, error("truncation too low")));
  error("no convergence");
}
Af(x) = sqrt(1 - x/z + O(t^(T+1)));
Bf(y) = sqrt(1 - y/(z-1) + O(t^(T+1)));
\\ task = [m, n, w1, w2, alpha, beta, rho, rho']; returns [h, containment rank ok, kappa]
edge(task) = {
  my(m = task[1], n = task[2], w1 = task[3], w2 = task[4], al = task[5], be = task[6], r1 = task[7], r2 = task[8]);
  my(S = [0, 1, 3/7, -5/3], SP = [0, 1, -2/5, 7/3], E = List());
  for (i = 1, m, for (j = 1, n, listput(E, Af(r1 * t^w1 * S[i]) * Bf(r2 * t^w2 * SP[j]))));
  my(R = reduce(Vec(E)), H = R[2], L = List([1]));
  for (i = 1, al, listput(L, z^-i)); for (j = 1, be - 1, listput(L, (z-1)^-j));
  my(Lv = Vec(L), MH = matrix(#H, 2*DEN+2, i, j, vecz(H[i])[j]), ML = matrix(#Lv, 2*DEN+2, i, j, vecz(Lv[i])[j]));
  my(rk = matrank(concat(MH~, ML~)));
  \\ top coefficients of each element of H
  my(top = vector(#H, i, [subst(simplify(H[i] * z^(al+1)), z, 0), subst(simplify(H[i] * (z-1)^be), z, 1)]));
  my(Tm = matrix(#H, 2, i, j, top[i][j]), kap = "undetermined");
  if (matrank(Tm) == 1, my(i0 = 0); for (i = 1, #H, if (top[i] != [0, 0], i0 = i; break));
    kap = if (top[i0][1] == 0, "infinite", top[i0][2] / top[i0][1]));
  [R[1] - w1 * n * binomial(m, 2) - w2 * m * binomial(n, 2), rk == m*n, matrank(Tm), kap];
}
export(t, z, T, DEN, vecz, reduce, Af, Bf, edge);
edgeparams(m, n) = {
  my(st = Set(vector(m + n - 2, s, sum(k = 0, m - 1, sum(l = 0, n - 1, k + l < s)))));
  select(c -> !setsearch(st, c), vector(m*n - 1, c, c));
}
{
  my(C = [[2,3],[2,4],[3,3],[3,4]], RR = [[1,1],[1,2],[1,3],[2,1],[1,-1],[3,-5]], tasks = List(), meta = List());
  foreach (C, mn, my(m = mn[1], n = mn[2], cs = edgeparams(m, n));
    for (r = 0, #cs - 1, my(c = cs[r+1], g = gcd(c, m*n), w = [(m*n - c)/g, c/g], al = m - 1 + r, be = m*n - 1 - al);
      listput(meta, [m, n, r, c, g, w, al, be]);
      foreach (RR, rr, listput(tasks, [m, n, w[1], w[2], al, be, rr[1], rr[2]]))));
  my(res = parapply(edge, Vec(tasks)), idx = 0);
  emit(Str("raw tasks ", Vec(tasks), ": ", res));
  foreach (meta, e,
    emit(Str("(m,n)=(", e[1], ",", e[2], ") edge r=", e[3], " c=", e[4], " lattice length g=", e[5], " normal w=", e[6], " between L(", e[7]+1, ",", e[8]-1, ") and L(", e[7], ",", e[8], "):"));
    foreach (RR, rr, idx++; my(x = res[idx]);
      emit(Str("   (rho,rho')=", rr, ": h=", x[1], " contains L(", e[7], ",", e[8]-1, "): ", x[2], " top rank ", x[3], " kappa=", x[4]))));
}
quit
