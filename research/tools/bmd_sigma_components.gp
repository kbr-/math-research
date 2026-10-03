\\ Components of Sigma_k = {Hank_k = D Hank_k = 0} on centered clusters (cycle bmd-20261009-bb, 9 October 2026).
\\ Sigma_k is translation and scaling invariant (Hank_k is; on Hank_k = 0 so is D Hank_k), so it suffices to work
\\ with centered clusters, e1 = 0. For M = 4, 5 and every 1 <= k <= M-2, express Hank_k = det(p_(i+j))_(0<=i,j<=k)
\\ and D Hank_k (D p_j = j p_(j+1)) in e2..eM, and factor their resultant / gcd structure. Question: is every
\\ distinct-root point of Sigma_k a rotation-invariant cluster (e2 = ... = e_(M-1) = 0) up to translation?
OUT = "research/results/bmd-20261009-bb/sigma-components.txt";
\\ power sums of a monic degree-M polynomial with e1 = 0, via Newton identities
psums(M, e, n) = {
  my(p = vector(n + 1));
  p[1] = M;  \\ p_0
  for (j = 1, n,
    my(s = 0);
    for (i = 1, min(j - 1, M), s += (-1)^(i - 1) * e[i] * p[j - i + 1]);
    if (j <= M, s += (-1)^(j - 1) * j * e[j]);
    p[j + 1] = s);
  p;
}
{
  foreach([4, 5], M,
    my(ev = vector(M, i, if (i == 1, 0, eval(Str("e", i)))), P = psums(M, ev, 2*M + 2));
    for (k = 1, M - 2,
      my(H = matdet(matrix(k + 1, k + 1, i, j, P[i + j - 1])));
      \\ D acts on power sums by D p_j = j p_(j+1); differentiate H as a polynomial in p_1..p_(2k+1)
      my(pv = vector(2*k + 1, j, eval(Str("q", j))), Hq = matdet(matrix(k + 1, k + 1, i, j, if (i + j == 2, M, pv[i + j - 2]))));
      my(DHq = sum(j = 1, 2*k, deriv(Hq, pv[j]) * j * pv[j + 1]));
      my(subst_p = (f -> my(g = f); for (j = 1, 2*k + 1, g = subst(g, pv[j], P[j + 1])); g));
      my(DH = subst_p(DHq));
      write(OUT, "M = ", M, ", k = ", k, ": Hank_k = ", factor(H));
      write(OUT, "   D Hank_k = ", factor(DH));
      if (M == 4,
        my(r = polresultant(H, DH, e3));
        write(OUT, "   resultant in e3 = ", factor(r)));
      if (M == 5,
        my(r = polresultant(H, DH, e5));
        write(OUT, "   resultant in e5 = ", factor(r)))));
}
