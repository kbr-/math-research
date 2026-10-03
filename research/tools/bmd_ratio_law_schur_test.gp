\\ Test of a Schur-function source for conj:cube-flow-order-ratio-law (cycle bmd-20261009-bj, 9 October 2026).
\\ Heuristic: along the flow, w_S = prod_(i in S)(1 - t y_i)^(-2k) = exp(sum_m s_m p_m(y_S)), s_m = 2k t^m / m, a Toda
\\ multi-time curve; at a degenerate point the leading coefficient of tau_k would be a Schur function of the partition
\\ lambda_k (|lambda_k| = j_k) evaluated at p_m = 2k, i.e. s_lambda(1^(2k)) by the hook-content formula. For the bump
\\ profile j_k = k(N - k) take lambda_k = rectangle with k rows of length N - k. Compare
\\   R_k = s_(lambda_(k+1))(1^(2k+2)) s_(lambda_(k-1))(1^(2k-2)) / s_(lambda_k)(1^(2k))^2
\\ with the observed leading-coefficient ratio L_k = -a(a + 2k^2)/(4k^2 (4k^2 - 1)), a = k(N - k), and also the
\\ variants with rectangles transposed and with p_m = 2k replaced by the actual moving counts, reporting R_k / L_k.
OUT = "research/results/bmd-20261009-bj/schur-test.txt";
\\ s_lambda(1^n) by hook-content: prod over boxes (n + content) / hook
srect(r, c, n) = {  \\ rectangle with r rows, c columns
  if (r == 0 || c == 0, return(1));
  my(num = 1, den = 1);
  for (i = 1, r, for (j = 1, c, num *= (n + j - i); den *= ((c - j) + (r - i) + 1)));
  num / den;
}
{
  for (N = 3, 8,
    my(row = List());
    for (k = 1, N - 1,
      my(a = k * (N - k), L = -a * (a + 2*k^2) / (4*k^2 * (4*k^2 - 1)));
      my(R1 = srect(k + 1, N - k - 1, 2*k + 2) * srect(k - 1, N - k + 1, 2*k - 2) / srect(k, N - k, 2*k)^2);
      my(d2 = srect(N - k, k, 2*k), R2 = if (d2, srect(N - k - 1, k + 1, 2*k + 2) * srect(N - k + 1, k - 1, 2*k - 2) / d2^2, 0));
      listput(row, [k, a, L, R1, R2, if (R1, L / R1, "-"), if (R2, L / R2, "-")]));
    write(OUT, "N = ", N, ": [k, a, L_k, R_k (rows = k), R_k (cols = k), L/R1, L/R2] = ", Vec(row)));
}
