\\ Leaders on fixed-cluster arcs at steep rates (cycle bmd-20261009-ap, 9 October 2026); method of
\\ bmd_cube_root_open_rates.gp (exact s-adic, reparametrized roots b = x y/(1 - x y), eps = -e/(1+e)).
\\ Tested statement (conj:cube-cancellation-wide-support on fixed-cluster arcs): the leaders' union has at most 2M + 2
\\ columns at every rate, including w_x >= 2 w_e, outside the range of cor:cube-near-window-nullity.
\\ M = 3; clusters: equilateral (1, w, w^2), (3, 2+w, 2+w^2), the tie (c0, 1, 0) with c0 = -w^2 = e^(i pi/3) (also
\\ equilateral), control (1, 2, 5); rates x = s^a, e = s^b, 1 <= a <= 6, 1 <= b <= 3; all 6-subsets of [-6, 8].
\\ For each rate: least valuation, number of leaders, union size; and the window bound minimum b* for comparison.
OUT = "research/results/bmd-20261009-ap/steep-rates.txt";
lam = 3/2;
cc(n) = if (n < 0, 0, binomial(-lam, n));
leaders(ys, a, bb) = {
  my(M = #ys, NS = 18 * max(a, bb) + 10, cols = [-6 .. 8], rows = matrix(2*M, #cols), best = oo, arg = List());
  my(xx = 's^a + O('s^NS), eps0 = -'s^bb / (1 + 's^bb) + O('s^NS));
  for (q = 1, M, my(b = xx * ys[q] / (1 - xx * ys[q]));
    for (u = 1, #cols, my(t = cols[u]);
      rows[q, u] = if (t >= 0, cc(t) * b^t, 0);
      rows[M + q, u] = sum(r = max(1, -t), NS, cc(r) * cc(t + r) * eps0^r * b^(t + r))));
  forsubset([#cols, 2*M], S, my(L = apply(u -> cols[u], Vec(S)));
    if (#select(t -> t < 0, L) <= M,
      my(d = matdet(vecextract(rows, "..", Vec(S))), v = if (d == 0, oo, valuation(lift(d), 's)));
      if (v < best, best = v; arg = List());
      if (v == best, listput(arg, L))));
  [best, Vec(arg)];
}
export(lam, cc, leaders);
{
  my(w3 = Mod(z, z^2 + z + 1), rates = List());
  for (a = 1, 6, for (bb = 1, 3, listput(rates, [a, bb])));
  rates = Vec(rates);
  foreach([[[1, w3, w3^2], "equilateral (1,w,w^2)"], [[3, 2 + w3, 2 + w3^2], "equilateral (3,2+w,2+w^2)"],
           [[-w3^2, 1, 0], "tie (e^(i pi/3), 1, 0)"], [[1, 2, 5], "control (1,2,5)"]], cas,
    my(R = parapply(r -> leaders(cas[1], r[1], r[2]), rates), M = 3, worst = 0);
    for (i = 1, #rates, my([a, bb] = rates[i], bs = vecmin(vector(M, p, a * (2*M^2 - 2*M*p + p^2 - p) + bb * (p^2 - p + M))));
      my(U = Set(concat(R[i][2])));
      worst = max(worst, #U);
      write(OUT, cas[2], " (w_x, w_e) = ", [a, bb], ": b* = ", bs, ", least ", R[i][1], ", leaders ", #R[i][2], ", union ", #U, if (#R[i][2] > 1, Str(" ", R[i][2]), "")));
    write(OUT, cas[2], ": largest union ", worst, " (2M + 2 = 8)"));
}
