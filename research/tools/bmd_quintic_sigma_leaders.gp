\\ Falsification test for conj:cube-cancellation-wide-support at non-rotation-invariant points of Sigma_1 n Sigma_2,
\\ M = 5 (cycle bmd-20261009-bc, 9 October 2026). Clusters: roots of z^5 + a z + b (e1 = e2 = e3 = 0, so
\\ Hank_1 = D Hank_1 = Hank_2 = D Hank_2 = 0), on fixed-cluster arcs x = 2 s^wx, eps = 3 s^we.
\\ Method: by the proof of lem:cube-cross-leading-coefficient, multiplying both row blocks by X = [y^t / P'(y)]
\\ turns the cross block into Ghat with upper entries c_i x^i h_(t+i-M+1) and lower entries
\\ sum_r c_r c_(i+r) eps^r x^(i+r) h_(t+i+r-M+1), and P_L = +- Vand^2 det Ghat; at a fixed cluster Vand^2 is a nonzero
\\ constant, so val P_L = val det Ghat. The h_n are rational: sum h_n z^n = 1 / (1 + a z^4 + b z^5).
\\ Control: a = 0, b = -1 (fifth roots of unity), where thm:cube-rotation-cluster-leaders predicts the leaders.
\\ Candidates: all 10-sets in families 1..5 with E+ <= 6, E- <= 1 (not exhaustive; reaches every L_p*).
\\ Reports least value, leaders and the union size (conjecture: at most 2M + 2 = 12 columns).
OUT = "research/results/bmd-20261009-bc/quintic-sigma-leaders.txt";
default(parisizemax, 2 * 10^9);
default(threadsizemax, 4 * 10^8);
default(nbthreads, 12);
lam = 3/2;
cc(n) = if (n < 0, 0, binomial(-lam, n));
hvec(a, b, N) = Vec(1 / (1 + a * 'z^4 + b * 'z^5) + O('z^(N + 1)));
valh(hv, M, L, wa, wb, NS) = {
  my(G = matrix(2*M, 2*M), xx = 2 * 's^wa + O('s^NS), ep = 3 * 's^wb + O('s^NS), R = NS \ wb + 1, h = (n -> if (n < 0, 0, hv[n + 1])));
  for (t = 0, M - 1,
    for (u = 1, 2*M, my(i = L[u]);
      G[t + 1, u] = if (i >= 0, cc(i) * xx^i * h(t + i - M + 1), 0);
      G[M + t + 1, u] = sum(r = max(1, -i), R, cc(r) * cc(i + r) * ep^r * xx^(i + r) * h(t + i + r - M + 1))));
  my(d = matdet(G));
  if (d == 0, oo, valuation(d, 's));
}
export(lam, cc, valh);
famsets(M, p, E, F) = {
  my(res = List());
  forsubset([2*M - p + E, 2*M - p], Sp, my(plus = apply(u -> u - 1, Vec(Sp)), Ep = vecsum(plus) - (2*M - p) * (2*M - p - 1) / 2);
    if (Ep <= E, forsubset([p + F, p], Sm, my(minus = vecsort(apply(u -> -u, Vec(Sm))), Em = -vecsum(minus) - p * (p + 1) / 2);
      if (Em <= F, listput(res, [concat(minus, plus), Ep, Em])))));
  Vec(res);
}
V(M, p, a, b) = a * M * (2*M - 1 - p) + b * (p^2 - p + M);
{
  my(M = 5, cand = List());
  for (p = 1, M, foreach(famsets(M, p, 6, 1), f, listput(cand, concat([p], f))));
  cand = Vec(cand);
  foreach([[0, -1, "z^5 - 1 (control)"], [1, 1, "z^5 + z + 1"], [3, -2, "z^5 + 3z - 2"]], cl,
    my(disc = poldisc('z^5 + cl[1] * 'z + cl[2]));
    foreach([[1, 1], [3, 2], [2, 3]], w,
      my(NS = vecmax(apply(c -> V(M, c[1], w[1], w[2]), cand)) + 12 * max(w[1], w[2]) + 6, hv = hvec(cl[1], cl[2], 2 * NS + 4 * M));
      my(Vs = parapply(c -> valh(hv, M, c[2], w[1], w[2], NS), cand), m = vecmin(Vs));
      my(lead = select(i -> Vs[i] == m, [1 .. #cand]), U = Set(concat(apply(i -> cand[i][2], lead))));
      write(OUT, cl[3], " (disc ", disc, "), rate ", w, ": ", #cand, " candidates; rotation min V = ",
            vecmin(vector(M, p, V(M, p, w[1], w[2]))), "; least value ", m, "; union ", #U, " columns ", [vecmin(U), vecmax(U)]);
      foreach(lead, i, write(OUT, "     p = ", cand[i][1], ", E+ = ", cand[i][3], ", E- = ", cand[i][4], ": ", cand[i][2]))));
}
