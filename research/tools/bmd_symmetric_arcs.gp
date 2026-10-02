\\ (W') and window local optimality along arcs above clusters placed symmetrically about the origin of the cherry
\\ coordinates, where e_1 (the sum of the roots) has positive valuation and standard-negative minimality fails
\\ (ex:cube-standard-negative-minimality-fails). Cycle bmd-20261009-p, 9 October 2026; copy of
\\ bmd_route_review17_tests.gp (cycle bmd-20261009-j) with these trees, M = 4, columns [-4, 7], NU = 31.
\\ Tested: (W') on 11 arcs; the exchange axiom on random triples; whether the best window beats all its single
\\ exchanges (prop:cube-window-local-exchange-reduction's condition). One prime q = 1000003 (eta = q).
default(parisizemax, 4 * 10^9);
OUT = "research/results/bmd-20261009-p/symmetric-arcs.txt";
DROPPED = 0;
q = 1000003;
c(n) = if(n < 0, 0, binomial(-3/2, n));
vq(x) = if(x == 0, oo, valuation(x, q));
NU = 27;  \\ >= the largest leading u-order M^2 = 16 at M = 4, with margin (a first run with NU = 14 dropped p = 4)
export(c, vq, q, NU);
coords(Y) = {
  \\ coordinates computed in parallel (parapply); results collected in the original subset order
  my(M = #Y, cols = [-M .. 2 * M - 1], Ls = List(), res = List());
  forsubset([#cols, 2 * M], S, my(L = vector(2 * M, i, cols[S[i]]));
    if(#select(t -> t < 0, L) <= M, listput(Ls, L)));
  my(V = parapply(L -> my(X = matrix(2 * #Y, 2 * #Y, r, i, my(t = L[i]);
        if(r <= #Y, if(t >= 0, c(t) * Y[r]^t, 0),
          my(s = r - #Y); sum(m = max(1, -t), NU, c(m) * c(t + m) * Y[s]^(t + m) * 'u^m))));
      my(D = matdet(X)); vector(NU + 1, n, vq(polcoef(D, n - 1, 'u))), Vec(Ls)));
  for (i = 1, #Ls, if(vecmin(V[i]) < oo, listput(res, [Ls[i], vecsum(Ls[i]), V[i]]), DROPPED++));
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
BIG = 10^9;  \\ finite sentinel for vanishing coordinates (PARI forbids t_INT + oo)
omg(R, idx, wx, we) = { my(v = R[idx][3], sL = R[idx][2], val = BIG);
  for (n = 0, NU, if(v[n + 1] < oo, val = min(val, (sL + n) * wx + n * we + v[n + 1]))); val };
exchtest(name, Y, R, arcs) = {
  my(M = #Y, H = Map(), N = #R);
  for (i = 1, N, mapput(H, R[i][1], i));
  my(get = (L, wx, we) -> my(j); if(mapisdefined(H, vecsort(L), &j), omg(R, j, wx, we), BIG));
  setrand(1);
  for (a = 1, #arcs, my(wx = arcs[a][1], we = arcs[a][2], bad = 0, tested = 0);
    for (r = 1, 3000, my(i1 = random(N) + 1, i2 = random(N) + 1, A = R[i1][1], B = R[i2][1]);
      my(AmB = setminus(Set(A), Set(B)), BmA = setminus(Set(B), Set(A)));
      if(#AmB == 0, next);
      my(x = AmB[random(#AmB) + 1], lhs = omg(R, i1, wx, we) + omg(R, i2, wx, we), rhs = 3 * BIG);
      if(lhs >= BIG, next);
      foreach(BmA, y, rhs = min(rhs, get(concat(setminus(Set(A), [x]), [y]), wx, we) + get(concat(setminus(Set(B), [y]), [x]), wx, we)));
      tested++; if(lhs < rhs, bad++));
    my(bw = 3 * BIG, bp = -1);
    for (p = 0, M, my(W = [-p .. 2 * M - 1 - p], w = get(W, wx, we)); if(w < bw, bw = w; bp = p));
    my(W = [-bp .. 2 * M - 1 - bp], nb = 3 * BIG);
    foreach(W, x, for (y = -M, 2 * M - 1, if(!setsearch(Set(W), y), nb = min(nb, get(concat(setminus(Set(W), [x]), [y]), wx, we)))));
    write(OUT, "  ", name, " arc (", wx, ",", we, "): exchange axiom violations ", bad, " of ", tested,
      "; best window p=", bp, " value ", bw, ", best single exchange ", nb, ", locally optimal: ", bw <= nb));
};
{
  my(arcs = [[1, 1], [1, 3], [3, 1], [1, 5], [5, 1], [2, 7], [7, 2], [1, 9], [9, 1], [1, 20], [20, 1]], q0 = 1000003);
  my(cfg = [["two cherries symmetric about 0", [1, 1 + q0, -1, -1 - q0 + q0^2]], ["pair and cherry, e_1 = eta", [1, -1 + q0, 2, -2 + q0^2]], ["nested cluster at +-1, e_1 = eta", [1, 1 + q0^2, -1 + q0, -1 + q0 + q0^3]]]);
  for (i = 1, #cfg, DROPPED = 0; my(R = coords(cfg[i][2]));
    write(OUT, cfg[i][1], ": ", #R, " nonzero coordinates, dropped ", DROPPED);
    arctest(cfg[i][1], cfg[i][2], R, arcs); exchtest(cfg[i][1], cfg[i][2], R, arcs));
}
