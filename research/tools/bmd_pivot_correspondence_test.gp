\\ Test of the family-Hankel pivot correspondence (cycle bmd-20261009-bk, 9 October 2026).
\\ Conjecture (conj:cube-family-hankel-pivots): for a cluster y with distinct roots and 1 <= p <= M-1, k = M - p,
\\ the vanishing-order set of V_p(y) = span{z^j H (j < M), (1/z) int_0^z w^m H (p-1 <= m <= M-2)} is
\\ O_p = [0, M-2] u (M - 1 + P_k), where P_k is the pivot set (vanishing orders) of the Hankel column space
\\ C_k = span{(p_(r+c))_(r >= 0) : c <= k}. With thm:cube-hankel-block-flow-orders this gives r_p = j_k
\\ (conj:cube-ramification-flow-order). Clusters with one or two nontrivial Hankel blocks, M = 4..8.
OUT = "research/results/bmd-20261009-bk/pivot-correspondence.txt";
default(parisizemax, 2 * 10^9);
NS = 60;
vorders(F, T) = {
  my(A = matrix(T, #F, i, j, polcoeff(F[j], i - 1, 'z)), ords = List(), prev = 0);
  for (i = 1, T, my(ri = matrank(A[1..i, ])); if (ri > prev, listput(ords, i - 1); prev = ri));
  [matrank(A), Vec(ords)];
}
{
  my(cls = [[4, 'z^4 - 1], [5, 'z^5 + 'z + 1], [5, 'z^5 + 'z^3 - 'z^2 + 57/40*'z - 187/100], [6, 'z^6 + 'z + 1], [6, 'z^6 + 'z^3 - 2],
            [6, 'z^6 + 'z^2 + 1], [7, 'z^7 + 'z^2 + 1], [7, 'z^7 + 'z^3 - 2], [8, 'z^8 + 'z^3 - 2], [8, 'z^8 + 'z + 1]]);
  foreach(cls, cl,
    my([M, P] = cl, pi = Polrev(Vec(P), 'z), H = 1 / pi + O('z^NS), hv = Vec(H), S = -'z * deriv(pi, 'z) / pi + M + O('z^NS), sv = Vec(S));
    my(ok = 1, bad = List(), hp = List());
    for (p = 1, M - 1,
      my(k = M - p, FV = List(), CK = List());
      for (j = 0, M - 1, listput(FV, 'z^j * H));
      for (m = p - 1, M - 2, listput(FV, sum(n = 0, NS - 1 - m, hv[n + 1] * 'z^(n + m) / (n + m + 1)) + O('z^(NS - 1))));
      for (c = 0, k, listput(CK, sum(r = 0, NS - 1 - c, sv[r + c + 1] * 'z^r) + O('z^(NS - c))));
      my(oV = vorders(Vec(FV), NS - 12), oC = vorders(Vec(CK), NS - 12)[2]);
      my(pred = concat([0 .. M - 2], apply(x -> x + M - 1, oC)));
      listput(hp, [p, oC]);
      if (oV[2] != pred, ok = 0; listput(bad, [p, oV[2], pred])));
    write(OUT, "M = ", M, ", ", P, ": correspondence holds for all p: ", ok, if (#bad, Str("; failures [p, O_p, predicted] = ", Vec(bad)), ""),
          "; Hankel pivots [p, P_k] = ", Vec(hp)));
}
