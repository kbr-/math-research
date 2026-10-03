\\ Vanishing orders of V_p and the polynomial space U_p (cycle bmd-20261009-bd, 9 October 2026).
\\ V_p = span{z^j H (j < M), (1/z) int_0^z w^m H (p-1 <= m <= M-2)}, H = 1/pi, pi = prod(1 - y_q z).
\\ Claims tested: (a) the vanishing-order set O(V_p) at z = 0 is the unique Gale-minimal nonzero minor, i.e. the
\\ nonnegative part of the family-p minimizer found in research/results/bmd-20261009-bc/flow-order-families.txt;
\\ (b) U_p = {Q' pi - Q pi' : deg Q <= M} + pi * span{z^m : p-1 <= m <= M-2} has the same ramification weight at 0
\\ as V_p (via W(1, z V_p) = W(U) and multiplication by the unit pi^2); also reports dimensions.
OUT = "research/results/bmd-20261009-bd/vanishing-orders.txt";
N = 40;
\\ vanishing orders of the span of series/polynomials F (list), via column echelon of the coefficient matrix
vorders(F, T) = {
  my(A = matrix(T, #F, i, j, polcoeff(F[j], i - 1, 'z)), r = matrank(A), ords = List(), B = A);
  \\ greedy: orders are the row indices where the rank of the top rows increases
  my(prev = 0);
  for (i = 1, T, my(ri = matrank(A[1..i, ])); if (ri > prev, listput(ords, i - 1); prev = ri));
  [r, Vec(ords)];
}
weight(o) = sum(i = 1, #o, o[i] - (i - 1));
{
  my(cls = [[4, 'z^4 - 1], [4, 'z^4 + 'z + 1], [5, 'z^5 - 1], [5, 'z^5 + 'z + 1], [5, 'z^5 - 'z^2 + 2*'z + 3]]);
  foreach(cls, cl,
    my([M, P] = cl, pi = Polrev(Vec(P), 'z), H = 1 / pi + O('z^N), hv = Vec(H));
    for (p = 1, M - 1,
      my(k = M - p, FV = List(), FU = List());
      for (j = 0, M - 1, listput(FV, 'z^j * H));
      for (m = p - 1, M - 2, listput(FV, sum(n = 0, N - 1 - m, hv[n + 1] * 'z^(n + m) / (n + m + 1)) + O('z^(N - 1))));
      for (d = 0, M, listput(FU, deriv('z^d, 'z) * pi - 'z^d * deriv(pi, 'z)));
      for (m = p - 1, M - 2, listput(FU, 'z^m * pi));
      my(oV = vorders(Vec(FV), N - 4), oU = vorders(Vec(FU), 2 * M + 2));
      write(OUT, "M = ", M, ", ", P, ", p = ", p, ": dim V = ", oV[1], ", O(V) = ", oV[2], ", weight ", weight(oV[2]),
            "; dim U = ", oU[1], ", O(U) = ", oU[2], ", weight ", weight(oU[2]))));
}
