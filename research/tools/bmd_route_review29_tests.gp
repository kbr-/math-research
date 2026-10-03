\\ Cheap tests of the route review of 9 October 2026 (cycle bmd-20261009-cg), on the reduced triple window U_3
\\ (lem:cube-level-window-gegenbauer-form: rows (1 + a_k E^-1)^m h^(ij), h^(ij)_n = rho_n e^(ij)_n, columns n = d+m..d+m+4,
\\ d = m(m-1)/2, lambda = 3/2, rho_n = Gamma(n+1)/Gamma(n+lambda+m+1); rho is normalized by a common constant, which does
\\ not affect ranks or signs of minors).
\\ (a) Lead "creative telescoping": a P-recursive sequence grows at most like exp(O(m log m)). At a = (2/7, -5/3, 1) print
\\     log|largest 3 x 3 minor| / m^2 for m = 4..30; a limit bounded away from 0 means the minors are not P-recursive in m.
\\ (b) Lead "Chebyshev systems": at real configurations print the signs of the ten 3 x 3 minors for m = 2..16; one strict
\\     sign for all ten at every m is sign-regularity, the signature of a T-system mechanism.
\\ (c) Bridge "zero counting for recurrences": the least order r (with polynomial coefficients of degree <= 8) of a
\\     recurrence annihilating one filtered row, m = 3, exact over Q; three rows of order r give a combination of order <= 3r.
OUT = "research/results/bmd-20261009-cg/route-review29-tests.txt";
default(realprecision, 150);
lam = 3/2;
\\ exact filtered row entries for n = 0..top (rho as exact rationals relative to rho_0 = 1/Gamma(lambda+m+1))
rowseq(a, i, j, k, m, top) = {
  my(e = Vec(((1 + a[i] * 'T + O('T^(top + 1))) * (1 + a[j] * 'T))^(-lam)), rho = vector(top + 1), h);
  rho[1] = 1; for (n = 1, top, rho[n + 1] = rho[n] * n / (n + lam + m));
  h = vector(top + 1, t, rho[t] * e[t]);
  vector(top + 1, t, my(n = t - 1); sum(l = 0, min(m, n), binomial(m, l) * a[k]^l * h[n - l + 1]));
}
U3(a, m) = {
  my(d = m * (m - 1) / 2, N0 = d + m, top = N0 + 4, prs = [[1, 2, 3], [1, 3, 2], [2, 3, 1]]);
  my(R = vector(3, r, rowseq(a, prs[r][1], prs[r][2], prs[r][3], m, top)));
  matrix(3, 5, r, c, R[r][N0 + c]);
}
minors(U) = { my(L = List()); forsubset([5, 3], S, my(Sv = Vec(S)); listput(L, matdet(matrix(3, 3, r, t, U[r, Sv[t]])))); Vec(L); }
{
  my(a = [2/7, -5/3, 1]);
  write(OUT, "(a) growth at a = ", a);
  for (m = 4, 30, my(M = minors(U3(a, m)), b = vecmax(apply(abs, M)));
    write(OUT, "  m = ", m, "  log|max minor| = ", precision(log(b), 20), "  / m^2 = ", precision(log(b) / m^2, 10)));
  foreach([[3/10, 3/5, 1], [-1/2, 2/5, 1], [-3, -1/2, 1], [5/2, 7/4, 1]], a,
    write(OUT, "(b) signs at a = ", a);
    for (m = 2, 16, my(M = minors(U3(a, m)));
      write(OUT, "  m = ", m, "  signs = ", apply(sign, M))));
  my(a = [2/7, -5/3, 1], m = 3, top = 140, F = rowseq(a, 1, 2, 3, m, top), found = 0);
  write(OUT, "(c) recurrence order of row (12|3) at a = ", a, ", m = ", m);
  for (r = 1, 4, if (found, break); for (D = 0, 8,
    my(nv = (r + 1) * (D + 1), nE = nv + 20, A = matrix(nE, nv));
    for (q = 1, nE, my(n = q - 1); for (i = 0, r, for (e = 0, D, A[q, i * (D + 1) + e + 1] = n^e * F[n + i + 1])));
    my(K = matker(A));
    if (#K, write(OUT, "  order ", r, ", degree ", D, ": kernel dimension ", #K, " (", nE, " equations)"); found = 1; break)));
  if (!found, write(OUT, "  no recurrence of order <= 4, degree <= 8"));
}
