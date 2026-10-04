\\ Route review (cycle kfk, 9 October 2026): exact confirmation of ex:cube-family-value-flow-three.
\\ Statement tested: at the exact sextic of bmd_review_flow_three_test.gp (flow order 3 at p = 4 and p = 2, 4 at
\\ p = 3), on the fixed-cluster arc x = 2 s^wa, eps = 3 s^wb, the window's value exceeds the generic window value
\\ (which is the window bound b_p) by exactly 2(wa + wb) at p = 4, 2, beating (F)'s 3 wa when 2 wb < wa; at p = 3 by
\\ 4 wa (the window's own coefficients vanish further). Exact rational arithmetic: the h-determinant valuation valh of
\\ bmd_flow_order_families.gp (rows multiplied by [y^t/P'(y)], entries in complete homogeneous polynomials), at the
\\ cluster and at a generic sextic, rate (3, 1).
OUT = getenv("OUT");
emit(s) = print(s); if (OUT != 0 && OUT != "", write(OUT, s));
default(parisizemax, 2 * 10^9);
lam = 3/2;
cc(n) = if (n < 0, 0, binomial(-lam, n));
hvecP(P, N) = Vec(1 / Polrev(Vec(P), 'z) + O('z^(N + 1)));
valh(hv, M, L, wa, wb, NS) = {
  my(G = matrix(2*M, 2*M), xx = 2 * 's^wa + O('s^NS), ep = 3 * 's^wb + O('s^NS), R = NS \ wb + 1, h = (n -> if (n < 0, 0, hv[n + 1])));
  for (t = 0, M - 1,
    for (u = 1, 2*M, my(i = L[u]);
      G[t + 1, u] = if (i >= 0, cc(i) * xx^i * h(t + i - M + 1), 0);
      G[M + t + 1, u] = sum(r = max(1, -i), R, cc(r) * cc(i + r) * ep^r * xx^(i + r) * h(t + i + r - M + 1))));
  my(d = matdet(G));
  if (d == 0, oo, valuation(d, 's));
}
bwin(M, p, a, b) = a * (2*M^2 - 2*M*p + p^2 - p) + b * (p^2 - p + M);
{
  my(f = 'z^6 + 9/7*'z^5 - 264/49*'z^4 - 5554/1029*'z^3 + 74839/7203*'z^2 + 4823789/756315*'z - 349335146/47647845);
  my(g = 'z^6 - 'z^4 + 2*'z^3 + 3*'z^2 - 'z + 5, M = 6, wa = 3, wb = 1);
  foreach([4, 2, 3], p, my(L = vector(2 * M, i, -p - 1 + i), b = bwin(M, p, wa, wb), NS = b + 4 * wa + 2, N = 2 * M + NS);
    my(vc = valh(hvecP(f, N), M, L, wa, wb, NS), vg = valh(hvecP(g, N), M, L, wa, wb, NS));
    emit(Str("rate [3, 1] p=", p, ": window value at cluster - generic = ", vc - vg, "  ((F) predicts ", wa * if (p == 3, 4, 3), "; delta = 2 term gives ", 2 * (wa + wb), ")")));
  quit;
}
