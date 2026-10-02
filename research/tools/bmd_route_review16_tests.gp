\\ Route review test (9 October 2026; cycle bmd-20261009-f). Copy of bmd_cherry_cluster_arcs.gp at M = 5:
\\ (1) condition (W') along 11 arcs above two separated cherries (1, 1+eta, 2, 2+eta^2, 5) and a cherry on top
\\     (1, 1+eta, 2, 5, 7), columns [-5, 9], u-orders to NU = 27 (largest leading order M^2 = 25);
\\ (2) valuated-matroid lead: along each arc, is p -> min over sets with p negative indices of val P_Lambda discrete
\\     convex? One prime q = 1000003 (conclusive for refutation only).
default(parisizemax, 4 * 10^9);
OUT = "research/results/bmd-20261009-f/review-tests.txt";
DROPPED = 0;
q = 1000003;
c(n) = if(n < 0, 0, binomial(-3/2, n));
vq(x) = if(x == 0, oo, valuation(x, q));
NU = 27;  \\ >= the largest leading u-order M^2 = 16 at M = 4, with margin (a first run with NU = 14 dropped p = 4)
coords(Y) = {
  my(M = #Y, cols = [-M .. 2 * M - 1], res = List());
  forsubset([#cols, 2 * M], S, my(L = vector(2 * M, i, cols[S[i]]));
    if(#select(t -> t < 0, L) <= M,
      my(X = matrix(2 * M, 2 * M, r, i, my(t = L[i]);
        if(r <= M, if(t >= 0, c(t) * Y[r]^t, 0),
          my(s = r - M); sum(m = max(1, -t), NU, c(m) * c(t + m) * Y[s]^(t + m) * 'u^m))));
      my(D = matdet(X), v = vector(NU + 1, n, vq(polcoef(D, n - 1, 'u))));
      if(vecmin(v) < oo, listput(res, [L, vecsum(L), v]), DROPPED++)));
  res;
};
arctest(name, Y, R, arcs) = {
  my(M = #Y);
  for (a = 1, #arcs, my(wx = arcs[a][1], we = arcs[a][2], best = oo, lead = List(), pm = vector(M + 1, i, oo));
    for (i = 1, #R, my(L = R[i][1], sL = R[i][2], v = R[i][3], val = oo, p = #select(t -> t < 0, L));
      for (n = 0, NU, if(v[n + 1] < oo, val = min(val, (sL + n) * wx + n * we + v[n + 1])));
      pm[p + 1] = min(pm[p + 1], val);
      if(val < best, best = val; lead = List([L]), if(val == best, listput(lead, L))));
    my(lo = vecmin(apply(L -> vecmin(L), Vec(lead))), hi = vecmax(apply(L -> vecmax(L), Vec(lead))), conv = 1);
    for (p = 2, M, if(pm[p + 1] - pm[p] < pm[p] - pm[p - 1], conv = 0));
    write(OUT, "  ", name, " M=", M, " arc (", wx, ",", we, "): ", #lead, " leaders, span [", lo, ",", hi, "], (W') ",
      if(hi - lo <= 2 * M, "holds", "FAILS"), "; class minima ", pm, " convex: ", conv));
};
{
  my(arcs = [[1, 1], [1, 3], [3, 1], [1, 5], [5, 1], [2, 7], [7, 2], [1, 9], [9, 1], [1, 20], [20, 1]], q0 = 1000003);
  my(cfg = [["two separated cherries", [1, 1 + q0, 2, 2 + q0^2, 5]], ["cherry top", [1, 1 + q0, 2, 5, 7]]]);
  for (i = 1, #cfg, DROPPED = 0; my(R = coords(cfg[i][2]));
    write(OUT, cfg[i][1], ": ", #R, " nonzero coordinates, dropped ", DROPPED);
    arctest(cfg[i][1], cfg[i][2], R, arcs));
}
