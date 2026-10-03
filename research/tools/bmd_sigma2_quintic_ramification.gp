\\ Pointwise test of conj:cube-ramification-flow-order on Sigma_2 at M = 5 (cycle bmd-20261009-be, 9 October 2026).
\\ The triangular congruence fails at M = 5, k = 2, n = 2 (bmd_wronskian_triangular.sing), so the conjecture is tested
\\ directly at rational points of Sigma_2 = {Hank_2 = D Hank_2 = 0}: centred quintics z^5 + e2 z^3 - e3 z^2 + e4 z - e5
\\ with e4 = (12 e2^3 + 45 e3^2)/(40 e2), e5 = (4 e2^2 e3 + 30 e3 e4)/(25 e2) (solving the two equations), e3 != 0.
\\ For each point and every p: flow order j_p and ramification weight r_p of V_p (vanishing orders at 0), and the
\\ vanishing orders themselves. Distinct roots are checked by the discriminant.
OUT = "research/results/bmd-20261009-be/sigma2-quintic-ramification.txt";
N = 44;
vorders(F, T) = {
  my(A = matrix(T, #F, i, j, polcoeff(F[j], i - 1, 'z)), ords = List(), prev = 0);
  for (i = 1, T, my(ri = matrank(A[1..i, ])); if (ri > prev, listput(ords, i - 1); prev = ri));
  [matrank(A), Vec(ords)];
}
weight(o) = sum(i = 1, #o, o[i] - (i - 1));
floword(P, M, k, T) = {
  my(Q = subst(P, 'z, 'x / (1 + 'tt * 'x)) * (1 + 'tt * 'x)^M + O('tt^T));
  Q = Q / polcoeff(Q, M, 'x);
  my(a = vector(M, j, polcoeff(Q, M - j, 'x)), pw = vector(2*k + 1));
  for (j = 1, 2*k, my(s = if (j <= M, j * a[j], 0)); for (i = 1, min(j - 1, M), s += a[i] * pw[j - i]); pw[j] = -s);
  my(H = matdet(matrix(k + 1, k + 1, i, j, if (i + j == 2, M, pw[i + j - 2]))));
  if (H == 0, oo, valuation(H, 'tt));
}
{
  my(M = 5, pts = [[1, 1], [2, 1], [-1, 1], [3, 2], [1, 3], [-2, 5]]);
  foreach(pts, e,
    my([e2, e3] = e, e4 = (12*e2^3 + 45*e3^2) / (40*e2), e5 = (4*e2^2*e3 + 30*e3*e4) / (25*e2));
    my(P = 'z^5 + e2*'z^3 - e3*'z^2 + e4*'z - e5, pi = Polrev(Vec(P), 'z), H = 1 / pi + O('z^N), hv = Vec(H));
    my(res = vector(M - 1, p,
      my(k = M - p, FV = List());
      for (j = 0, M - 1, listput(FV, 'z^j * H));
      for (m = p - 1, M - 2, listput(FV, sum(n = 0, N - 1 - m, hv[n + 1] * 'z^(n + m) / (n + m + 1)) + O('z^(N - 1))));
      my(o = vorders(Vec(FV), N - 4));
      [p, floword(P, M, k, 30), weight(o[2]), o[1] == M + k, o[2]]));
    write(OUT, "e2 = ", e2, ", e3 = ", e3, ": P = ", P, ", disc != 0: ", poldisc(P) != 0);
    foreach(res, r, write(OUT, "   p = ", r[1], ": flow order ", r[2], ", ramification ", r[3], ", full dim ", r[4], ", orders ", r[5], if (r[2] != r[3], "   MISMATCH", ""))));
}
