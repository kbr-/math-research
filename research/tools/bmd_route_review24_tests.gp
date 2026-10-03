\\ Goal-level review tests (cycle bmd-20261009-az, 9 October 2026).
\\ (1) Selection rule: at the M-th roots of unity a symmetric polynomial homogeneous of degree d vanishes unless M | d,
\\     since y -> zeta y permutes the cluster. Least coefficients (relative to Vand^2) have degree k(k+1) + E+.
\\     Compared with the square data (check:cube-square-survivors) and recomputed at M = 5 for windows and E+ <= 4.
\\ (2) Falsification attempt for conj:cube-cancellation-wide-support: leaders of the cherry cross block on arcs with the
\\     reparametrized roots fixed at the 5th roots of unity (M = 5), exact over Q(zeta_5), at rates (w_x, w_e) in
\\     {(1,1), (3,2), (2,3)}, with x = 2 s^(w_x), eps = 3 s^(w_e) (fixed units). Candidates: all 10-sets in families
\\     p = 1..5 with E+ <= 5 and E- <= 5 (every other set has window bound beyond the least value found, checked). The
\\     value of each set is its exact s-valuation. Reports the least value, the leaders and their union (2M + 2 = 12 is
\\     the conjectured bound). Control: the square at M = 4, rate (1,1).
OUT = "research/results/bmd-20261009-az/review-tests.txt";
default(parisizemax, 4 * 10^9);
default(threadsizemax, 6 * 10^8);
default(nbthreads, 12);
lam = 3/2;
cc(n) = if (n < 0, 0, binomial(-lam, n));
\\ s-valuation of the cross coordinate on L at the arc x = 2 s^a, eps = 3 s^b, roots ys (polmods in a low variable)
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
famsets(M, p, E) = {
  my(res = List());
  forsubset([2*M - p + E, 2*M - p], Sp, my(plus = apply(u -> u - 1, Vec(Sp)), Ep = vecsum(plus) - (2*M - p) * (2*M - p - 1) / 2);
    if (Ep <= E, forsubset([p + E, p], Sm, my(minus = vecsort(apply(u -> -u, Vec(Sm))), Em = -vecsum(minus) - p * (p + 1) / 2);
      if (Em <= E, listput(res, [concat(minus, plus), Ep, Em])))));
  Vec(res);
}
bnd(M, p, a, b, Ep, Em) = a * (2*M^2 - 2*M*p + p^2 - p + Ep) + b * (p^2 - p + M + Em);
{
  my(E0 = 's, tt = varlower("tt"));
  \\ (1) selection rule
  my(rows = List());
  for (M = 4, 5, for (p = 1, M, my(k = M - p); listput(rows, [M, p, k, vector(5, j, (k * (k + 1) + j - 1) % M == 0)])));
  write(OUT, "(1) [M, p, k, survival allowed for E+ = 0..4] = ", Vec(rows));
  \\ (2) leaders
  foreach([[5, Mod(tt, polcyclo(5, tt)), [[1, 1], [3, 2], [2, 3]]], [4, Mod(tt, tt^2 + 1), [[1, 1]]]], cas,
    my([M, z, rates] = cas, ys = vector(M, j, z^(j - 1)), E = 5, cand = List());
    for (p = 1, M, foreach(famsets(M, p, E), f, listput(cand, concat([p], f))));
    cand = Vec(cand);
    foreach(rates, w,
      my(bs = apply(c -> bnd(M, c[1], w[1], w[2], c[3], c[4]), cand), NS = vecmax(bs) + 4 * max(w[1], w[2]) + 6);
      my(V = parapply(c -> valat(ys, c[2], w[1], w[2], NS), cand), m = vecmin(V));
      my(lead = select(i -> V[i] == m, [1 .. #cand]), U = Set(concat(apply(i -> cand[i][2], lead))));
      my(outside = vecmin(vector(M, p, bnd(M, p, w[1], w[2], 0, 0))) + (E + 1) * min(w[1], w[2]));
      write(OUT, "(2) M = ", M, ", rate ", w, ": ", #cand, " candidates; least value ", m, " (sets outside have bound >= ", outside, "); ",
            #lead, " leaders, union ", #U, " columns ", [vecmin(U), vecmax(U)], " (2M+2 = ", 2*M + 2, ")");
      foreach(lead, i, write(OUT, "     p = ", cand[i][1], ", E+ = ", cand[i][3], ", E- = ", cand[i][4], ": ", cand[i][2]))));
}
