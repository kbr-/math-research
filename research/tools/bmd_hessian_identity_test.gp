\\ Test of a Hessian identity behind conj:cube-hankel-flow-order-relation (cycle bmd-20261009-bi, 9 October 2026).
\\ Binary forms G_k(c, d) = sum_(|S|=k+1) Vand(y_S)^2 prod_(i not in S) (c y_i + d)^(2k), of degree n_k = 2k(M-k-1),
\\ homogenize the flow: H_k(y/(1 - t y)) prod_i (1 - t y_i)^(2k) = G_k(-t, 1), so j_k is the multiplicity of (0:1).
\\ deg G_(k+1) + deg G_(k-1) = 2 n_k - 4 = deg Hess(G_k). Candidate: Hess(G_k) = G_cc G_dd - G_cd^2 = C_k G_(k+1) G_(k-1)
\\ (G_0 = M prod (c y_i + d)^0 ... with the convention G_0 = sum_i prod_(j != i) (c y_j + d)^0 = M). Tested at random
\\ integer points y for M = 3..6, every 1 <= k <= M-2; reports whether the ratio is a constant and its value.
OUT = "research/results/bmd-20261009-bi/hessian-identity.txt";
G(y, k) = {
  my(M = #y, s = 0);
  forsubset([M, k + 1], S,
    my(v = prod(a = 1, k + 1, prod(b = a + 1, k + 1, y[S[b]] - y[S[a]])), inS = vector(M));
    for (a = 1, k + 1, inS[S[a]] = 1);
    s += v^2 * prod(i = 1, M, if (inS[i], 1, ('c * y[i] + 'd)^(2 * k))));
  s;
}
hess(f) = deriv(deriv(f, 'c), 'c) * deriv(deriv(f, 'd), 'd) - deriv(deriv(f, 'c), 'd)^2;
{
  for (M = 3, 6,
    for (trial = 1, 2,
      my(y = vector(M, i, random(21) - 10));
      while (#Set(y) < M, y = vector(M, i, random(21) - 10));
      my(Gs = vector(M + 1, k, if (k == 1, M, G(y, k - 1))));  \\ Gs[k+1] = G_k, G_0 = M
      for (k = 1, M - 2,
        my(h = hess(Gs[k + 1]), r = Gs[k + 2] * Gs[k]);
        if (r == 0, write(OUT, "M = ", M, ", y = ", y, ", k = ", k, ": G_(k+1) G_(k-1) = 0, Hess = 0: ", h == 0),
          my(q = h / r);
          write(OUT, "M = ", M, ", y = ", y, ", k = ", k, ": Hess / (G_(k+1) G_(k-1)) = ", q, if (type(q) == "t_INT" || type(q) == "t_FRAC", "  (constant)", "  (NOT constant)"))))));
}
