\\ Limit spaces at the vertices of neck corner Newton polygons (1 October 2026; cycle bmd-20261001-j).
\\ Setting of bmd_cube_neck_corner_polygon.gp: neck (m,n), V = < A(x_i) B(y_j) >, A(x) = (1 - x/z)^(1/2),
\\ B(y) = (1 - y/(z-1))^(1/2), x = lambda s, y = lambda' s', along lambda = rho t^w1, lambda' = rho' t^w2.
\\ The flat limit of V as t -> 0 is spanned by the t^0 coefficients of the reduced rows of the cost-sum
\\ algorithm.  Every element is a rational function regular at infinity with poles only at 0 and 1, so the
\\ limit lies in L(alpha[0] + beta[1]), alpha, beta its largest pole orders; it equals that complete linear
\\ system exactly when alpha + beta + 1 = mn.
\\ Question tested: is the limit at every weight in the open normal cone of a vertex a complete linear system
\\ L(alpha[0] + beta[1]) with alpha + beta = mn - 1 (proved on the two axes: L(n(m-1)[0] + (n-1)[1]) and
\\ L((m-1)[0] + m(n-1)[1])), and do the vertices correspond to alpha?  Two coefficient pairs (rho, rho')
\\ separate vertex limits (independent of rho) from edge limits.
default(threadsizemax, 300000000); default(parisizemax, 1000000000);
OUT = getenv("OUT");
emit(s) = print(s); if (OUT != 0 && OUT != "", write(OUT, s));
t; z;
T = if (getenv("TT") != 0 && getenv("TT") != "", eval(getenv("TT")), 96); DEN = T;
vecz(f) = my(p = simplify(f*z^DEN*(z-1)^DEN)); if(type(p) == "t_RFRAC" && poldegree(denominator(p), z) > 0, error("denominator")); Vecrev(p, 2*DEN + 2);
poles(f) = my(p = simplify(f*z^DEN*(z-1)^DEN)); [DEN - valuation(p, z), DEN - valuation(subst(p, z, z + 1), z)];
reduce(E) = {
  my(k = #E, rows = E, cost = vector(k), M, K, cc, piv, nr);
  for(iter = 1, 2000,
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
\\ returns [h, alpha, beta, [alpha, beta] with the second coefficient pair]
lim(task) = {
  my(m = task[1], n = task[2], w1 = task[3], w2 = task[4]);
  my(S = [0, 1, 3/7, -5/3], SP = [0, 1, -2/5, 7/3], out = List());
  foreach (RR, rr,
    my(E = List());
    for (i = 1, m, for (j = 1, n, listput(E, Af(rr[1] * t^w1 * S[i]) * Bf(rr[2] * t^w2 * SP[j]))));
    my(R = reduce(Vec(E)), P = vector(m*n, i, poles(R[2][i])));
    listput(out, [R[1] - w1 * n * binomial(m, 2) - w2 * m * binomial(n, 2), vecmax(vector(#P, i, P[i][1])), vecmax(vector(#P, i, P[i][2]))]));
  Vec(out);
}
RR = if (getenv("PAIRS") == "1", [[7/5, -9/4]], [[7/5, -9/4], [-3/2, 5/7]]);
export(t, z, T, DEN, RR, vecz, poles, reduce, Af, Bf, lim);
{
  my(W = List());
  for (i = 1, 6, for (j = 1, 6, if (gcd(i, j) == 1, listput(W, [i, j]))));
  W = vecsort(Vec(W), (a, b) -> sign(b[2]/b[1] - a[2]/a[1]));
  my(C = [[2,3],[2,4],[3,3],[3,4]], tasks = List(), cs = getenv("CASES"));
  if (cs != 0 && cs != "", C = eval(cs));
  if (getenv("HALF") == "1", W = select(w -> w[2] >= w[1], W));
  foreach (C, mn, foreach (W, w, listput(tasks, [mn[1], mn[2], w[1], w[2]])));
  my(res = parapply(lim, Vec(tasks)), idx = 0);
  emit(Str("raw [h, alpha, beta] x two coefficient pairs for tasks ", Vec(tasks), ": ", res));
  foreach (C, mn, my(m = mn[1], n = mn[2]);
    emit(Str("(m,n)=(", m, ",", n, "), mn - 1 = ", m*n - 1, "; per weight w: h, limit poles (alpha,beta) for two coefficient pairs, complete if alpha+beta = mn-1"));
    foreach (W, w, idx++; my(r = res[idx], note = "");
      if (#r == 1, r = [r[1], r[1]]; note = " (one coefficient pair)");
      if (r[1][1] != r[2][1], note = Str(note, " (h differs: ", r[2][1], ")"));
      if (r[1][2] + r[1][3] == m*n - 1 && r[1][2..3] == r[2][2..3], note = Str(note, "  complete"));
      emit(Str("  w=", w, " h=", r[1][1], " poles ", r[1][2..3], " / ", r[2][2..3], note))));
}
quit
