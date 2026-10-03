\\ Falsification attempt for the flow-order bilinear relation (route review bmd-20261009-bg, 9 October 2026).
\\ Relation (from the Toda-type congruence (D Hank_k)^2 = -4k^2 Hank_(k+1) Hank_(k-1) mod Hank_k): along the D-flow,
\\ j_(k+1) + j_(k-1) = 2 j_k - 2 whenever 1 <= j_k < oo, where j_k = ord_(t=0) Hank_k(y/(1 - t y)), j_0 = j_M = ...
\\ (Hank_0 = M, Hank_M = 0 is excluded: the relation is tested for 1 <= k <= M-2). Clusters with many vanishing
\\ Hankel determinants: z^M + a z + b, z^M + z^2 + 1, z^M - 1, for M = 6, 7, 8. Under r = j and (F), the relation
\\ makes Delta_p = (o*_p - p + 1)/(2p) strictly decreasing; the script also reports Delta and its monotonicity.
OUT = "research/results/bmd-20261009-bg/flow-order-bilinear.txt";
floword(P, M, k, T) = {
  my(Q = subst(P, 'z, 'x / (1 + 'tt * 'x)) * (1 + 'tt * 'x)^M + O('tt^T));
  Q = Q / polcoeff(Q, M, 'x);
  my(a = vector(M, j, polcoeff(Q, M - j, 'x)), pw = vector(2*k + 1));
  for (j = 1, 2*k, my(s = if (j <= M, j * a[j], 0)); for (i = 1, min(j - 1, M), s += a[i] * pw[j - i]); pw[j] = -s);
  my(H = matdet(matrix(k + 1, k + 1, i, j, if (i + j == 2, M, pw[i + j - 2]))));
  if (H == 0, oo, valuation(H, 'tt));
}
{
  for (M = 6, 8,
    foreach(['z^M + 'z + 1, 'z^M + 2*'z - 3, 'z^M + 'z^2 + 1, 'z^M - 1, 'z^M + 'z^3 - 2], P,
      my(j = vector(M - 1, k, floword(P, M, k, 3 * M^2)));  \\ j[k] for k = 1..M-1 (k = M-1: Vand^2)
      my(jj = concat([0], j), ok = 1, bad = List());        \\ jj[k+1] = j_k, j_0 = 0
      for (k = 1, M - 2, if (jj[k + 1] >= 1 && jj[k + 1] < oo, if (jj[k + 2] + jj[k] != 2 * jj[k + 1] - 2, ok = 0; listput(bad, k))));
      \\ by p: j_p = j_(k = M - p); o*_p - (2M - p - 1) = j_p - j_(p+1)
      my(jp = vector(M, p, if (p == M, 0, jj[M - p + 1])), Delta = vector(M - 1, p, (2*M - 2*p + jp[p] - jp[p + 1]) / (2*p)));
      my(dec = 1); for (p = 1, M - 2, if (!(Delta[p] > Delta[p + 1]), dec = 0));
      write(OUT, "M = ", M, ", ", P, ", disc != 0: ", poldisc(P) != 0, ": j_k (k = 1..M-1) = ", j, "; relation holds: ", ok,
            if (#bad, Str(" (fails at k = ", Vec(bad), ")"), ""), "; Delta_p = ", Delta, ", strictly decreasing: ", dec)));
}
