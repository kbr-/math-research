\\ Leading C-block coordinate above the excluded tie moduli (cycle bmd-20261009-ad, 9 October 2026).
\\ The C-block (lem:cube-node-weight-bound) is the pair space of the cluster in the variable w; its coordinate on a
\\ column set S is x^(Sigma S) p_S(y), so along an arc its value is w_x Sigma S + val p_S(y). Proxy: p_S of the pair
\\ matrix of the normalized cluster y (rows [w^t]((1 + y_i w)(1 + y_j w))^(-3/2), i < j, columns t = 0..K), q-adic
\\ with q = 1000003 (the shift y -> y' = y/(1 - x y) is ignored: it changes p_S only at higher order in x).
\\ Tested statement (hypothesis of prop:cube-cherry-step-any-set): for every w_x in a grid, the minimum of
\\ w_x Sigma S + val p_S over binom(M,2)-subsets S of [0, K] is attained by a unique S.
\\ Clusters: (c0, 1, q, q + q^2) with c0 = (1 +- 2 sqrt(-2))/3 (excluded moduli), c0 = 2 (control), and the
\\ deeper scaling (c0, 1, q^10, q^10 + q^20) used on the failing ray. K = 9.
OUT = "research/results/bmd-20261009-ad/cblock-uniqueness.txt";
q = 1000003; PREC = 60; K = 9;
vq(x) = if(x == 0, 10^6, valuation(x, q));
H(r, s, K) = { my(f = ((1 + r * 'x + O('x^(K + 1))) * (1 + s * 'x))^(-3/2)); vector(K + 1, k, polcoef(f, k - 1, 'x)); }
run(name, Y) = {
  my(M = #Y, R = M * (M - 1) / 2, P = matrix(R, K + 1), r = 0);
  for (i = 1, M, for (j = i + 1, M, r++; my(h = H(Y[i], Y[j], K)); for (k = 1, K + 1, P[r, k] = h[k])));
  my(L = List());
  forsubset([K + 1, R], I, my(S = Vec(I) - vector(R, i, 1), d = matdet(matrix(R, R, a, b, P[a, I[b]])));
    if (d != 0, listput(L, [vecsum(S), vq(d), S])));
  my(nonuniq = List(), leaders = Set());
  for (a = 1, 40, my(wx = a / 10, best = 10^9, arg = List());
    foreach(L, t, my(v = wx * t[1] + t[2]); if (v < best, best = v; arg = List([t[3]]), if (v == best, listput(arg, t[3]))));
    leaders = setunion(leaders, Set(Vec(arg)));
    if (#arg > 1, listput(nonuniq, [wx, Vec(arg)])));
  my(vT = 10^6, vmin = 10^6); foreach(L, t, vmin = min(vmin, t[2]); if (t[3] == [0 .. R - 1], vT = t[2]));
  write(OUT, name, ": ", #L, " nonzero coordinates; Taylor dominance: val p_T0 = ", vT, ", min_S val p_S = ", vmin, "; leading sets over w_x in (1/10)[1..40]: ", Vec(leaders));
  write(OUT, "  w_x with a non-unique leader: ", #nonuniq);
  for (i = 1, min(#nonuniq, 6), write(OUT, "   ", nonuniq[i]));
};
{
  my(r = sqrt(-2 + O(q^PREC)), cA = truncate((1 + 2 * r) / 3), cB = truncate((1 - 2 * r) / 3));
  run("c0 = (1 + 2 sqrt(-2))/3, depths (1,2)", [cA, 1, q, q + q^2]);
  run("c0 = (1 - 2 sqrt(-2))/3, depths (1,2)", [cB, 1, q, q + q^2]);
  run("c0 = (1 + 2 sqrt(-2))/3, depths (10,20)", [cA, 1, q^10, q^10 + q^20]);
  run("control c0 = 2, depths (1,2)", [2, 1, q, q + q^2]);
}
