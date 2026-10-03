\\ Route review test (cycle bmd-20261009-bx, 9 October 2026), adapted from bmd_joint_tie_cross_leaders.gp: the cross
\\ support condition on cone tie clusters over a grid of rates. Falsification target: cor:cube-cherry-step-spread-two needs
\\ cross supports within 2M+1 columns where the C-block ties (w_x = 1 for the Gegenbauer-zero cluster) and within 2M+2
\\ columns elsewhere (prop:cube-cherry-step-wide). Clusters: the tie at the Gegenbauer zero -1, (-1 + eta, 1, 2 eta^2,
\\ 5 eta^4), and a control tie off the zeros, (3 + eta, 1, 2 eta^2, 5 eta^4); w_x in {1/2, 1, 2, 3}, w_e in {1/4, ..., 12}.
\\ Tested statement (condition (W') of cor:cube-cherry-step): along the arc x = eta^wx, eps = eta^we, with normalized
\\ cluster roots y (integer polynomials in eta), the cross coordinates of least valuation are all 2M-subsets of one
\\ interval of 2M+1 consecutive integers. Uses the homogeneity P_Lambda = sum_n x^(Sigma Lambda + n) eps^n F_n(y),
\\ F_n = [u^n] P_Lambda at x = 1, eps = u, so val P_Lambda = min_n ((Sigma Lambda + n) wx + n we + val_q F_n).
\\ Columns [-M, 2M]; u-orders up to NU. q-adic reading at eta = q = 1000003.
OUT = "research/results/bmd-20261009-bx/review-tests.txt";
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
    my(un = #Set(concat(apply(L -> L, Vec(lead)))));
    NARC++; if (#lead > 1, NMULTI++); if (un > 2 * M + 1, N1++); if (un > 2 * M + 2, N2++);
    if (un > 2 * M + 1, write(OUT, "  prime ", q, " ", name, " arc (wx,we)=(", wx, ",", we, "): ", #lead, " leaders, union of ", un, " columns",
      if (un > 2 * M + 2, " (exceeds 2M+2)", " (exceeds 2M+1)"), if (#lead <= 4, Str("; leaders ", Vec(lead)), ""))));
};
{
  my(e = 'e, arcs = List());
  foreach([1/2, 1, 2, 3], wx, for (k = 1, 48, listput(arcs, [wx, k / 4])));
  arcs = Vec(arcs);
  my(cfg = [["cone tie at the Gegenbauer zero -1", [-1 + e, 1, 2 * e^2, 5 * e^4]], ["control tie off the zeros", [3 + e, 1, 2 * e^2, 5 * e^4]]]);
  foreach([1000003, 1000033], qq, q = qq;
    for (i = 1, #cfg, my(Y = subst(cfg[i][2], 'e, q)); DROPPED = 0; my(R = coords(Y));
      write(OUT, "prime ", q, ", ", cfg[i][1], ": ", #R, " nonzero coordinates, dropped (zero to u^NU) ", DROPPED);
      NARC = 0; NMULTI = 0; N1 = 0; N2 = 0;
      arctest(cfg[i][1], Y, R, arcs);
      write(OUT, "  summary: ", NARC, " arcs, ", NMULTI, " with several cross leaders, ", N1, " with leader union > 2M+1 columns, ", N2, " with union > 2M+2")));
}
