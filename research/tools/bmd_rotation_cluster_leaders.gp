\\ Falsification test for thm:cube-rotation-cluster-leaders (cycle bmd-20261009-ba, 9 October 2026).
\\ Claim: with the reparametrized roots fixed at the M-th roots of unity, at every rate (w_x, w_e), every cross
\\ coordinate of family p has value >= V(p) = w_x M (2M-1-p) + w_e (p^2 - p + M), with equality only for
\\ L_p* = [-p, M-1] u [M+p-1, 2M-2]; the leaders are the L_p* minimizing V (one family or two adjacent).
\\ Test at M = 6 (composite: the degree selection rule alone allows the p = 4 window), exact over Q(zeta_6),
\\ rates (1,1) (predicted tie p = 3, 4, value 60) and (1,2) (predicted single p = 2, value 70).
\\ Candidates: all 12-sets in families p = 1..6 with E+ <= 6, E- <= 1 (not exhaustive; E+ = 6 reaches L_3*, L_4*). Reports every
\\ candidate violating value >= V(p), every equality case, the least value and the leaders.
OUT = "research/results/bmd-20261009-ba/rotation-leaders.txt";
default(parisizemax, 4 * 10^9);
default(threadsizemax, 6 * 10^8);
default(nbthreads, 12);
lam = 3/2;
cc(n) = if (n < 0, 0, binomial(-lam, n));
valat(ys, L, a, b, NS) = {
  my(M = #ys, G = matrix(2*M, 2*M), xx = 2 * 's^a + O('s^NS), ep = 3 * 's^b + O('s^NS), R = NS \ b + 1);
  for (q = 1, M, my(be = xx * ys[q]);
    for (u = 1, 2*M, my(t = L[u]);
      G[q, u] = if (t >= 0, cc(t) * be^t, 0);
      G[M + q, u] = sum(r = max(1, -t), R, cc(r) * cc(t + r) * ep^r * be^(t + r))));
  my(d = matdet(G));
  if (d == 0, oo, valuation(lift(d), 's));
}
export(lam, cc, valat);
famsets(M, p, E, F) = {
  my(res = List());
  forsubset([2*M - p + E, 2*M - p], Sp, my(plus = apply(u -> u - 1, Vec(Sp)), Ep = vecsum(plus) - (2*M - p) * (2*M - p - 1) / 2);
    if (Ep <= E, forsubset([p + F, p], Sm, my(minus = vecsort(apply(u -> -u, Vec(Sm))), Em = -vecsum(minus) - p * (p + 1) / 2);
      if (Em <= F, listput(res, [concat(minus, plus), Ep, Em])))));
  Vec(res);
}
V(M, p, a, b) = a * M * (2*M - 1 - p) + b * (p^2 - p + M);
star(M, p) = concat([-p .. M - 1], [M + p - 1 .. 2*M - 2]);
{
  my(tt = varlower("tt"), M = 6, z = Mod(tt, polcyclo(6, tt)), ys = vector(M, j, z^(j - 1)), cand = List());
  for (p = 1, M, foreach(famsets(M, p, 6, 1), f, listput(cand, concat([p], f))));
  cand = Vec(cand);
  foreach([[1, 1], [1, 2]], w,
    my(NS = vecmax(apply(c -> V(M, c[1], w[1], w[2]), cand)) + 8 * max(w[1], w[2]) + 6);
    my(Vs = parapply(c -> valat(ys, c[2], w[1], w[2], NS), cand), m = vecmin(Vs));
    my(bad = select(i -> Vs[i] < V(M, cand[i][1], w[1], w[2]), [1 .. #cand]));
    my(eq = select(i -> Vs[i] == V(M, cand[i][1], w[1], w[2]), [1 .. #cand]));
    my(lead = select(i -> Vs[i] == m, [1 .. #cand]), U = Set(concat(apply(i -> cand[i][2], lead))));
    write(OUT, "M = 6, rate ", w, ": ", #cand, " candidates; predicted V(p), p = 1..6: ", vector(M, p, V(M, p, w[1], w[2])));
    write(OUT, "  violations of value >= V(p): ", #bad, "; equality cases [p, is L_p*]: ", apply(i -> [cand[i][1], cand[i][2] == star(M, cand[i][1])], eq));
    write(OUT, "  least value ", m, "; leaders [p, set]: ", apply(i -> [cand[i][1], cand[i][2]], lead), "; union ", #U, " columns"));
}
