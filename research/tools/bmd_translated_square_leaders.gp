\\ Falsification test for lem:cube-dilation-leader-transfer (cycle bmd-20261009-bb, 9 October 2026).
\\ Prediction: on fixed-cluster arcs at a translate y0 + c of a rotation-invariant cluster, the leaders and least
\\ value equal those at y0 (thm:cube-rotation-cluster-leaders). Test: M = 4, y0 = (1, i, -1, -i), c = 2 and c = 1 + 3i,
\\ exact over Q(i), rates (1,1) (predicted leaders L_2*, L_3*, value 26) and (2,1) (predicted single family).
\\ Candidates: all 8-sets in families 1..4 with E+ <= 6, E- <= 1 (reaches every L_p*: E+ = k(p-1) <= 4).
\\ Control: the untranslated square.
OUT = "research/results/bmd-20261009-bb/translated-square.txt";
default(parisizemax, 2 * 10^9);
default(threadsizemax, 4 * 10^8);
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
{
  my(tt = varlower("tt"), M = 4, z = Mod(tt, tt^2 + 1), sq = vector(M, j, z^(j - 1)), cand = List());
  for (p = 1, M, foreach(famsets(M, p, 6, 1), f, listput(cand, concat([p], f))));
  cand = Vec(cand);
  foreach([[0, "square"], [2, "square + 2"], [1 + 3*z, "square + 1 + 3i"]], sh,
    my(ys = apply(y -> y + sh[1], sq));
    foreach([[1, 1], [2, 1]], w,
      my(NS = vecmax(apply(c -> V(M, c[1], w[1], w[2]), cand)) + 10 * max(w[1], w[2]) + 6);
      my(Vs = parapply(c -> valat(ys, c[2], w[1], w[2], NS), cand), m = vecmin(Vs));
      my(lead = select(i -> Vs[i] == m, [1 .. #cand]), U = Set(concat(apply(i -> cand[i][2], lead))));
      write(OUT, sh[2], ", rate ", w, ": ", #cand, " candidates; predicted min V = ", vecmin(vector(M, p, V(M, p, w[1], w[2]))),
            "; least value ", m, "; leaders [p, set]: ", apply(i -> [cand[i][1], cand[i][2]], lead), "; union ", #U)));
}
