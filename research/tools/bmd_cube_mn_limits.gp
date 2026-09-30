\\ Exact flat limits of (m,n) two-cluster classes with m, n >= 3 (30 September 2026; cycle bmd-20260930-zzc).
\\ Products (1 - b_j eps u1)^(1/2)(1 - c_k eps u2)^(1/2), u1 = 1/z, u2 = 1/(z-1), rational shapes; valuation reduction
\\ over Q[[eps]] in the coordinates u1^a, u2^c (as in bmd_cube_two_n_extras.gp).  Prints the reduced orders, the
\\ cluster-cost-bound costs (thm:cube-cluster-cost-bound: s + 2 ceil(s/(m-1)) - 2 at a cluster of size m, s at
\\ poles below the cluster size), the pole-dimension function dim{f in L : pole <= x at 0, <= y at 1}
\\ (tables only; limit functions are not printed).  Shapes: two choices for (3,3), (3,4); one elsewhere.
OUT = getenv("OUT");
emit(s) = print(s); if (OUT != 0 && OUT != "", write(OUT, s));
coords(a, c, K) = {
  my(F = 1 / ('z^a * ('z - 1)^c), v = vector(2 * K + 1));
  my(s0 = F + O('z^1)); for (k = 1, K, v[k] = polcoef(s0, -k, 'z));
  my(t = subst(F, 'z, 1 + 'y) + O('y^1)); for (k = 1, K, v[K + k] = polcoef(t, -k, 'y));
  v[2 * K + 1] = if (a + c == 0, 1, 0); v;
}
flat(b, c, K) = {
  my(n1 = #b, n2 = #c, D = 2 * K + 1, rows = List(), CO = matrix(K + 1, K + 1));
  for (a = 0, K, for (cc = 0, K - a, CO[a + 1, cc + 1] = coords(a, cc, K)));
  for (j = 1, n1, for (k = 1, n2, my(r = vector(D));
    for (a = 0, K, for (cc = 0, K - a, r += binomial(1/2, a) * (-b[j])^a * binomial(1/2, cc) * (-c[k])^cc * 'e^(a + cc) * CO[a + 1, cc + 1]));
    listput(rows, r)));
  my(R = Mat(Vec(rows)~), n = n1 * n2, vals = vector(n), iter = 0);
  while (1, iter++; if (iter > 20000, error("no convergence"));
    for (i = 1, n, vals[i] = vecmin(vector(D, t, if (R[i, t] == 0, oo, valuation(R[i, t], 'e)))));
    my(L = matrix(n, D, i, t, polcoef(R[i, t], vals[i], 'e)), ker = matker(L~));
    if (#ker == 0, break);
    my(w = ker[, 1], i0 = 0, best = -oo);
    for (i = 1, n, if (w[i] != 0 && vals[i] > best, best = vals[i]; i0 = i));
    R[i0, ] = sum(i = 1, n, w[i] * 'e^(best - vals[i]) * R[i, ]);
    for (t = 1, D, R[i0, t] = truncate(R[i0, t] + O('e^(K + 1)))));
  [vals, matrix(n, D, i, t, polcoef(R[i, t], vals[i], 'e))];
}
cost(s, m) = if (m == 1, oo, s + 2 * ceil(s / (m - 1)) - 2);
report(b, c, K) = {
  my(m = #b, n = #c, res = flat(b, c, K), vals = res[1], L = res[2], N = m * n);
  my(costs = List([0])); for (s = 1, 3 * K, listput(costs, cost(s, m)); listput(costs, cost(s, n)));
  costs = vecsort(Vec(costs))[1..N];
  emit(Str("(m,n)=(", m, ",", n, ") b=", b, " c=", c, ": orders ", vecsort(vals), " (sum ", vecsum(vals), "); cheapest costs ", costs, " (sum ", vecsum(costs), ")"));
  \\ pole dimension function
  my(X = 0, Y = 0); for (i = 1, N, for (t = 1, K, if (L[i, t] != 0, X = max(X, t)); if (L[i, K + t] != 0, Y = max(Y, t))));
  emit(Str("  max poles (", X, ", ", Y, ")"));
  for (x = 0, X, emit(Str("   x=", x, ": ", vector(Y + 1, yy, my(y = yy - 1, cols = concat(vector(K - x, t, x + t), vector(K - y, t, K + y + t))); N - matrank(matrix(N, #cols, i, t, L[i, cols[t]]))))));
}
main() = {
  my(K = if (getenv("K"), eval(getenv("K")), 24));
  \\ env PREDICT=1: held-out sizes (5,5), (4,6), (3,7), predicted before this run (cycle entry): limits
  \\ H^0(O(12p1+12p2)); a hyperplane of H^0(O(11p1+13p2)) containing H^0(O(10p1+12p2)); H^0(O(8p1+12p2))
  \\ env GENERIC=1: (3,4) at the shapes of the two-cluster check (seed 0: b = (-3/7, 5/7, -1), c = (2/5, -1, 8/5, -11/5))
  \\ and at three further rational shape pairs, to decide which shapes are generic
  if (getenv("GENERIC"), foreach ([[[-3/7, 5/7, -1], [2/5, -1, 8/5, -11/5]], [[2/3, -5/4, 7/9], [3/7, -2/5, 11/6, -1/8]], [[-7/11, 3/13, 5/2], [9/7, -4/3, 1/10, 13/5]], [[1/2, -3, 17/7], [-5/6, 2/9, 7/4, -3/11]]], bc, report(bc[1], bc[2], K)); return);
  if (getenv("PREDICT"), foreach ([[[-3, -1, 0, 2, 5], [-4, -2, 1, 3, 4]], [[-2, -1, 1, 3], [-5, -2, 0, 1, 3, 4]], [[-1, 0, 2], [-6, -3, -1, 0, 2, 4, 5]]], bc, report(bc[1], bc[2], K)); return);
  foreach ([[[-1, 0, 2], [-2, 1, 3]], [[-3, 1, 4], [0, 2, 5]], [[-1, 0, 2], [-3, -1, 1, 4]], [[-2, 1, 3], [-2, 0, 1, 5]],
            [[-1, 0, 2], [-4, -1, 0, 2, 5]], [[-1, 0, 2], [-5, -2, 0, 1, 3, 4]], [[-2, -1, 1, 3], [-3, 0, 1, 4]], [[-2, -1, 1, 3], [-4, -1, 0, 2, 5]]], bc,
    report(bc[1], bc[2], K));
}
main();
quit
