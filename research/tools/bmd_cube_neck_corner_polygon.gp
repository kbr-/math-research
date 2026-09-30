\\ Newton polygons of neck corners from their support function (1 October 2026; cycle bmd-20261001-j).
\\ Setting of bmd_cube_neck_corner_order.gp (lem:cube-neck-corner-tropical-bound): neck (m,n), x = lambda s,
\\ y = lambda' s'; intrinsic Pluecker vector P of the divided-difference basis.  Along lambda = rho t^w1,
\\ lambda' = rho' t^w2 with generic rho, rho', the t-order of P is the support function
\\ h(w) = min { w.v : v in Newt(P) } of the Newton polygon of P in (lambda, lambda') (equality at generic
\\ coefficients), computed as the flat-limit cost sum of the product basis minus the Vandermonde orders
\\ w1 n binom(m,2) + w2 m binom(n,2).  The weighted tropical cost (lower bound) is computed alongside.
\\ Vertices: for consecutive rays w, w' of the fan (sorted by w2/w1 descending) the solution of w.v = h(w),
\\ w'.v = h(w') is the vertex between them when the fan separates the vertices; the script prints the
\\ candidates and checks that min over them reproduces h on every ray (a necessary consistency test).
\\ Question tested: m = 2 fit Newt = conv{ (j(j-1), (n+1-j)(n-j)) : 1 <= j <= n } + R_{>=0}^2, and the
\\ vertex structure of (3,3), (3,4), (4,4).  Control: the (2,3) values of the first run (T = 64).
default(threadsizemax, 300000000); default(parisizemax, 1000000000);
OUT = getenv("OUT");
emit(s) = print(s); if (OUT != 0 && OUT != "", write(OUT, s));
t; z;
T = 112; DEN = 112;
vecz(f) = my(p = simplify(f*z^DEN*(z-1)^DEN)); if(type(p) == "t_RFRAC" && poldegree(denominator(p), z) > 0, error("denominator")); Vecrev(p, 2*DEN + 2);
costsum(E) = {
  my(k = #E, rows = E, cost = vector(k), M, K, cc, piv, nr);
  for(iter = 1, 2000,
    M = matrix(k, 2*DEN+2, i, j, vecz(polcoef(rows[i], 0, t))[j]);
    K = matker(M~);
    if(#K == 0, return(vecsum(cost)));
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
hval(task) = {
  my(m = task[1], n = task[2], w1 = task[3], w2 = task[4]);
  my(S = [0, 1, 3/7, -5/3, 11/4], SP = [0, 1, -2/5, 7/3, 5/8, -7/2], E = List(), rho = 7/5, rhop = -9/4);
  for (i = 1, m, for (j = 1, n, listput(E, Af(rho * t^w1 * S[i]) * Bf(rhop * t^w2 * SP[j]))));
  costsum(Vec(E)) - w1 * n * binomial(m, 2) - w2 * m * binomial(n, 2);
}
export(t, z, T, DEN, vecz, costsum, Af, Bf, hval);
\\ tropical cost pairs (U-cost, V-cost) over all splits; the tropical support function is their min.
tpairs(m, n) = {
  my(R = List()); for (k = 0, m - 1, for (l = 0, n - 1, if (k + l > 0, listput(R, [k, l]))));
  my(N = #R, P = List());
  for (mask = 0, 2^N - 1,
    my(ks = List(), ls = List());
    for (i = 1, N, if (bittest(mask, i - 1), listput(ks, R[i][1]), listput(ls, R[i][2])));
    my(kv = vecsort(Vec(ks)), lv = vecsort(Vec(ls)), a = 0, b = 0);
    for (i = 1, #kv, a += max(0, i - kv[i]));
    for (i = 1, #lv, b += max(0, i - lv[i]));
    listput(P, [a, b]));
  Set(Vec(P));
}
vertices(W, H) = {
  my(V = List());
  for (i = 1, #W - 1,
    my(M = [W[i][1], W[i][2]; W[i+1][1], W[i+1][2]], v = matsolve(M, [H[i], H[i+1]]~));
    listput(V, [v[1], v[2]]));
  Set(Vec(V));
}
fitm2(n) = vector(n, j, [j*(j-1), (n+1-j)*(n-j)]);
supp(V, w) = vecmin(vector(#V, i, w[1]*V[i][1] + w[2]*V[i][2]));
{
  my(W = [[1,8],[1,6],[1,5],[1,4],[1,3],[2,5],[1,2],[3,5],[2,3],[3,4],[1,1],[4,3],[3,2],[5,3],[2,1],[5,2],[3,1],[4,1],[5,1],[6,1],[8,1]]);
  my(C = [[2,3],[2,5],[2,6],[3,3],[3,4],[4,4]]);
  my(tasks = List());
  foreach (C, mn, foreach (W, w, listput(tasks, [mn[1], mn[2], w[1], w[2]])));
  my(res = parapply(hval, Vec(tasks)), idx = 0);
  emit(Str("raw h for tasks ", Vec(tasks), ": ", res));
  foreach (C, mn, my(m = mn[1], n = mn[2], H = vector(#W), TP = tpairs(m, n), HT);
    for (i = 1, #W, idx++; H[i] = res[idx]);
    HT = vector(#W, i, supp(TP, W[i]));
    emit(Str("(m,n)=(", m, ",", n, ") weights ", W));
    emit(Str("  h        = ", H));
    emit(Str("  tropical = ", HT));
    my(V = vertices(W, H));
    emit(Str("  vertex candidates = ", V));
    emit(Str("  candidates reproduce h on every ray: ", vector(#W, i, supp(V, W[i])) == H));
    if (m == 2, my(F = fitm2(n)); emit(Str("  m=2 fit ", F, " reproduces h: ", vector(#W, i, supp(F, W[i])) == H))));
}
quit
