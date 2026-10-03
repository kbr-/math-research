\\ Consistency check of conj:cube-flow-order-family-value with thm:cube-rotation-cluster-leaders (cycle bmd-20261009-bc).
\\ At the M-th roots of unity the theorem gives family minimum b_p + w_x k(p-1), k = M - p; the conjecture then
\\ predicts ord_(t=0) Hank_k(y/(1 - t y)) = k(p-1). Computed exactly for M = 4..8, 1 <= p <= M-1.
OUT = "research/results/bmd-20261009-bc/rotation-flow-orders.txt";
floword(P, M, k, T) = {
  my(Q = subst(P, 'z, 'z / (1 + 'tt * 'z)) * (1 + 'tt * 'z)^M + O('tt^T));
  Q = Q / polcoeff(Q, M, 'z);
  my(a = vector(M, j, polcoeff(Q, M - j, 'z)), pw = vector(2*k + 1));
  for (j = 1, 2*k, my(s = if (j <= M, j * a[j], 0)); for (i = 1, min(j - 1, M), s += a[i] * pw[j - i]); pw[j] = -s);
  my(H = matdet(matrix(k + 1, k + 1, i, j, if (i + j == 2, M, pw[i + j - 2]))));
  if (H == 0, oo, valuation(H, 'tt));
}
{
  for (M = 4, 8,
    my(got = vector(M - 1, p, floword('z^M - 1, M, M - p, 80)), pred = vector(M - 1, p, (M - p) * (p - 1)));
    write(OUT, "M = ", M, ": flow orders p = 1..M-1: ", got, "; predicted k(p-1): ", pred, "; agree: ", got == pred));
}
