\\ Provenance copy: the version of research/tools/bmd_cube_neck_corner_polygon.gp that produced
\\ neck-corner-polygon.txt (first run of cycle bmd-20261001-j, command
\\ env OUT=research/results/bmd-20261001-j/neck-corner-polygon.txt gp -q research/tools/bmd_cube_neck_corner_polygon.gp).
\\ The committed script is the later fan version.
\\ Newton polygons of neck corners from their support function (1 October 2026; cycle bmd-20261001-j).
\\ Setting of bmd_cube_neck_corner_order.gp (lem:cube-neck-corner-tropical-bound): neck (m,n), x = lambda s,
\\ y = lambda' s'; intrinsic Pluecker vector P of the divided-difference basis.  Along lambda = rho t^w1,
\\ lambda' = rho' t^w2 with generic rho, rho', the t-order of P is the support function h(w) of the Newton polygon
\\ of P in (lambda, lambda') (equality at generic coefficients), computed as the flat-limit cost sum of the
\\ product basis minus the Vandermonde orders w1 n binom(m,2) + w2 m binom(n,2).  Also the weighted tropical cost.
\\ Output: h at the weights (1,1), (1,2), (2,1), (1,3), (3,1), (2,3), (3,2), (1,4), (4,1) for several necks.
OUT = getenv("OUT");
emit(s) = print(s); if (OUT != 0 && OUT != "", write(OUT, s));
t; z;
T = 64; DEN = 64;
vecz(f) = my(p = simplify(f*z^DEN*(z-1)^DEN)); if(type(p) == "t_RFRAC" && poldegree(denominator(p), z) > 0, error("denominator")); Vecrev(p, 2*DEN + 2);
costsum(E) = {
  my(k = #E, rows = E, cost = vector(k), M, K, cc, piv, nr);
  for(iter = 1, 600,
    M = matrix(k, 2*DEN+2, i, j, vecz(polcoef(rows[i], 0, t))[j]);
    K = matker(M~);
    if(#K == 0, return(vecsum(cost)));
    cc = K[,1];
    piv = 0; for(i = 1, k, if(cc[i] != 0 && (piv == 0 || cost[i] > cost[piv]), piv = i));
    nr = sum(i = 1, k, cc[i]*rows[i]);
    if(polcoef(nr, 0, t) != 0, error("relation not zero"));
    rows[piv] = nr/t; cost[piv]++);
  error("no convergence");
}
Af(x) = sqrt(1 - x/z + O(t^(T+1)));
Bf(y) = sqrt(1 - y/(z-1) + O(t^(T+1)));
wtrop(m, n, w1, w2) = {
  my(R = List()); for (k = 0, m - 1, for (l = 0, n - 1, if (k + l > 0, listput(R, [k, l]))));
  my(best = oo, N = #R);
  for (mask = 0, 2^N - 1,
    my(ks = List(), ls = List());
    for (i = 1, N, if (bittest(mask, i - 1), listput(ks, R[i][1]), listput(ls, R[i][2])));
    my(kv = vecsort(Vec(ks)), lv = vecsort(Vec(ls)), c = 0);
    for (i = 1, #kv, c += w1 * max(0, i - kv[i]));
    for (i = 1, #lv, c += w2 * max(0, i - lv[i]));
    best = min(best, c));
  best;
}
hval(m, n, s, sp, w1, w2) = {
  my(E = List(), rho = 7/5, rhop = -9/4);
  for (i = 1, m, for (j = 1, n, listput(E, Af(rho * t^w1 * s[i]) * Bf(rhop * t^w2 * sp[j]))));
  costsum(Vec(E)) - w1 * n * binomial(m, 2) - w2 * m * binomial(n, 2);
}
{
  my(S = [0, 1, 3/7, -5/3, 11/4], SP = [0, 1, -2/5, 7/3, 5/8]);
  my(W = [[1,1],[1,2],[2,1],[1,3],[3,1],[2,3],[3,2],[1,4],[4,1]]);
  foreach ([[2,2],[2,3],[2,4],[2,5],[3,3],[3,4]], mn, my(m = mn[1], n = mn[2], line = Str("(m,n)=(", m, ",", n, "): h(w) [tropical]:"));
    foreach (W, w, line = Str(line, " (", w[1], ",", w[2], "):", hval(m, n, S[1..m], SP[1..n], w[1], w[2]), "[", wtrop(m, n, w[1], w[2]), "]"));
    emit(line));
}
quit
