\\ Check of the Hermite–Padé lattice identity for the triple window's system (cycle bmd-20261009-cj, 9 October 2026).
\\ Claim (lem:cube-window-hermite-pade-frobenius): for the seven functions 1, w_i^-3, (w_i w_j)^-3 and a multi-index N,
\\ with H(N) the square determinant (rows T^r g, r < N_g, g non-polynomial; columns N_0..|N|-1; polynomial rows dropped),
\\ for blocks i != j among the six non-polynomial directions:
\\   H(N) H(N + e0 - e_i - e_j) = s1 H(N + e0 - e_i) H(N - e_j) + s2 H(N + e0 - e_j) H(N - e_i), s1, s2 in {+1, -1}.
\\ At a = (2/7, -5/3, 1) exactly, for N = (1;2,2,2;1,1,1) and (3;3,3,3;1,1,1), and all 15 pairs i < j, print whether
\\ some sign pair makes the identity exact, and which.
OUT = "research/results/bmd-20261009-cj/hp-frobenius-check.txt";
cc(n) = binomial(-3/2, n);
H(a, N) = {
  my(prs = [[1, 2], [1, 3], [2, 3]], tot = vecsum(N), dd = N[1], top = tot, seq = vector(6), rows = List());
  if (tot - dd == 0, return(1));
  for (i = 1, 3, seq[i] = vector(top + 1, c, cc(c - 1) * a[i]^(c - 1)));
  for (p = 1, 3, my([i, j] = prs[p]); seq[3 + p] = vector(top + 1, c, sum(t = 0, c - 1, cc(t) * cc(c - 1 - t) * a[i]^t * a[j]^(c - 1 - t))));
  for (g = 1, 6, for (r = 0, N[g + 1] - 1, listput(rows, vector(tot - dd, col, my(c = dd + col - 1 - r); if (c >= 0, seq[g][c + 1], 0)))));
  matdet(matrix(#rows, tot - dd, i, j, rows[i][j]));
}
{
  my(a = [2/7, -5/3, 1], e0 = [1, 0, 0, 0, 0, 0, 0]);
  foreach([[1, 2, 2, 2, 1, 1, 1], [3, 3, 3, 3, 1, 1, 1]], N,
    for (i = 2, 7, for (j = i + 1, 7,
      my(ei = vector(7, k, k == i), ej = vector(7, k, k == j));
      my(L = H(a, N) * H(a, N + e0 - ei - ej), A = H(a, N + e0 - ei) * H(a, N - ej), B = H(a, N + e0 - ej) * H(a, N - ei), ok = "none");
      foreach([[1, 1], [1, -1], [-1, 1], [-1, -1]], s, if (L == s[1] * A + s[2] * B, ok = s; break));
      write(OUT, "N = ", N, ", i = ", i, ", j = ", j, ": exact with signs ", ok, if (L == 0, " (L = 0)", "")))));
}
