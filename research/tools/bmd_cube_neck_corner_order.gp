\\ Order of the neck corner Pluecker vector against the tropical assignment cost (1 October 2026; cycle bmd-20261001-i).
\\ Neck (m,n): V = < A(x_i) B(y_j) >, A(x) = (1 - x/z)^(1/2), B(y) = (1 - y/(z-1))^(1/2), clusters x = lambda s,
\\ y = lambda' s' (s_1 = s'_1 = 0).  P = Pluecker vector of the divided-difference basis A_k B_l; its order along
\\ the arc lambda = t, lambda' = r t^e equals the flat-limit cost sum of the product basis minus the Vandermonde
\\ orders n binom(m,2) + e m binom(n,2).  The flat-limit cost sum (algorithm of bmd_cube_neck_tie.gp) is the sum of
\\ the t-adic Smith exponents of the coefficient matrix of the numerators, i.e. the valuation of the Pluecker vector.
\\ Tropical cost c(m,n) (lower bound, lem:cube-neck-corner-tropical-bound): rows (k,l) != (0,0) split into U and V;
\\ U costs sum_t (t - k_(t))^+ over sorted k, V costs sum_t (t - l_(t))^+ over sorted l; minimum over splits.
\\ Question: is the order 2 c(m,n) on every ray (equal exponents, several ratios), and what on unequal exponents?
OUT = getenv("OUT");
emit(s) = print(s); if (OUT != 0 && OUT != "", write(OUT, s));
t; z;
T = 34; DEN = 34;
vecz(f) = my(p = simplify(f*z^DEN*(z-1)^DEN)); if(type(p) == "t_RFRAC" && poldegree(denominator(p), z) > 0, error("denominator")); Vecrev(p, 2*DEN + 2);
costsum(E) = {
  my(k = #E, rows = E, cost = vector(k), M, K, cc, piv, nr);
  for(iter = 1, 400,
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
ctrop(m, n) = {
  my(R = List()); for (k = 0, m - 1, for (l = 0, n - 1, if (k + l > 0, listput(R, [k, l]))));
  my(best = oo, N = #R);
  forstep (mask = 0, 2^N - 1, 1,
    my(ks = List(), ls = List());
    for (i = 1, N, if (bittest(mask, i - 1), listput(ks, R[i][1]), listput(ls, R[i][2])));
    my(kv = vecsort(Vec(ks)), lv = vecsort(Vec(ls)), c = 0);
    for (i = 1, #kv, c += max(0, i - kv[i]));
    for (i = 1, #lv, c += max(0, i - lv[i]));
    best = min(best, c));
  best;
}
order(m, n, s, sp, r, e) = {
  my(E = List());
  for (i = 1, m, for (j = 1, n, listput(E, Af(t * s[i]) * Bf(r * t^e * sp[j]))));
  costsum(Vec(E)) - n * binomial(m, 2) - e * m * binomial(n, 2);
}
{
  my(cases = [[2, 2], [2, 3], [3, 3], [2, 4]]);
  foreach (cases, mn, my(m = mn[1], n = mn[2], s = concat([0, 1], vector(m - 2, i, [3/7, -5/3, 11/4][i])), sp = concat([0, 1], vector(n - 2, i, [-2/5, 7/3, 5/8][i])));
    my(c = ctrop(m, n), line = Str("(m,n)=(", m, ",", n, "): tropical cost c = ", c, "; order along lambda = t, lambda' = r t:"));
    foreach ([2, 3/7, -5], r, line = Str(line, " r=", r, ": ", order(m, n, s, sp, r, 1)));
    line = Str(line, "; along lambda' = t^2 (r=1): ", order(m, n, s, sp, 1, 2), "; along lambda = t^2, lambda' = t: ", order(n, m, sp, s, 1, 2));
    emit(line));
}
quit
