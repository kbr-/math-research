\\ Route review bmd-20261001-a, Conca lead: quadratic relations among the maximal minors of a 2 x n matrix, generic
\\ (Pluecker) versus Hankel (rows (t_q), (t_(q+1))).  For n = 5, 6, 7: the number of products p_ij p_kl
\\ (unordered pairs of 2-subsets), the dimension of their span (by evaluation at random points modulo 2^61-1),
\\ and hence the number of independent quadratic relations in each case.
q0 = 2^61 - 1;
cnt(n, hank) = {
  my(S = List()); forsubset([n, 2], v, listput(S, Vec(v))); S = Vec(S);
  my(pairs = List()); for (i = 1, #S, for (j = i, #S, listput(pairs, [S[i], S[j]]))); pairs = Vec(pairs);
  my(np = #pairs, K = np + 20, M = matrix(K, np));
  for (r = 1, K,
    my(t = vector(n + 1, i, Mod(random(q0), q0)), u = vector(n, i, Mod(random(q0), q0)));
    my(m(Q) = if (hank, t[Q[1]] * t[Q[2] + 1] - t[Q[2]] * t[Q[1] + 1], t[Q[1]] * u[Q[2]] - t[Q[2]] * u[Q[1]]));
    for (c = 1, np, M[r, c] = m(pairs[c][1]) * m(pairs[c][2])));
  [np, matrank(M)];
}
{
  setrand(1);
  for (n = 5, 7, my(g = cnt(n, 0), h = cnt(n, 1));
    print("n = ", n, ": products ", g[1], "; span generic ", g[2], " (relations ", g[1] - g[2], "), Hankel ", h[2], " (relations ", h[1] - h[2], ")"));
}
