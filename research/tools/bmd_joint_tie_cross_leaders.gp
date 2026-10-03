\\ Cross leaders above the cone tie at the Gegenbauer zero c0 = -1 (cycle bmd-20261009-bw, 9 October 2026), adapted
\\ from bmd_cherry_cluster_arcs.gp (cycle bmd-20261008-zy): cluster (-1 + eta, 1, 2 eta^2, 5 eta^4), whose C-block ties
\\ at w_x = 1; the question is at which cherry rates w_e the cross block has several leaders at w_x = 1 (joint ties).
\\ Tested statement (condition (W') of cor:cube-cherry-step): along the arc x = eta^wx, eps = eta^we, with normalized
\\ cluster roots y (integer polynomials in eta), the cross coordinates of least valuation are all 2M-subsets of one
\\ interval of 2M+1 consecutive integers. Uses the homogeneity P_Lambda = sum_n x^(Sigma Lambda + n) eps^n F_n(y),
\\ F_n = [u^n] P_Lambda at x = 1, eps = u, so val P_Lambda = min_n ((Sigma Lambda + n) wx + n we + val_q F_n).
\\ Columns [-M, 2M]; u-orders up to NU. q-adic reading at eta = q = 1000003.
OUT = "research/results/bmd-20261009-bw/joint-tie-cross-leaders.txt";
DROPPED = 0;
q = 1000003;
c(n) = if(n < 0, 0, binomial(-3/2, n));
vq(x) = if(x == 0, oo, valuation(x, q));
NU = 20;  \\ >= the largest leading u-order M^2 = 16 at M = 4, with margin (a first run with NU = 14 dropped p = 4)
coords(Y) = {
  my(M = #Y, cols = [-M .. 2 * M], res = List());
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
  for (a = 1, #arcs, my(wx = arcs[a][1], we = arcs[a][2], best = oo, lead = List());
    for (i = 1, #R, my(L = R[i][1], sL = R[i][2], v = R[i][3], val = oo);
      for (n = 0, NU, if(v[n + 1] < oo, val = min(val, (sL + n) * wx + n * we + v[n + 1])));
      if(val < best, best = val; lead = List([L]), if(val == best, listput(lead, L))));
    my(lo = vecmin(apply(L -> vecmin(L), Vec(lead))), hi = vecmax(apply(L -> vecmax(L), Vec(lead))));
    write(OUT, "  prime ", q, " ", name, " M=", M, " arc (wx,we)=(", wx, ",", we, "): ", #lead, " leaders, span [", lo, ",", hi, "], (W') ",
      if(hi - lo <= 2 * M, "holds", "FAILS"), if(#lead <= 3, Str("; leaders ", Vec(lead)), "")));
};
{
  my(e = 'e, arcs = vector(48, k, [1, k / 4]));
  my(cfg = [["cone tie at the Gegenbauer zero -1", [-1 + e, 1, 2 * e^2, 5 * e^4]]]);
  foreach([1000003, 1000033], qq, q = qq;
    for (i = 1, #cfg, my(Y = subst(cfg[i][2], 'e, q)); DROPPED = 0; my(R = coords(Y));
      write(OUT, "prime ", q, ", ", cfg[i][1], ": ", #R, " nonzero coordinates, dropped (zero to u^NU) ", DROPPED);
      arctest(cfg[i][1], Y, R, arcs)));
}
