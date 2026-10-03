\\ Bilinear (Somos/Hirota) test of the triple window's Plücker vector in m (cycle bmd-20261009-ci, 9 October 2026).
\\ Bridge tested (window cores review, integrable lattices): the ten maximal minors P_S(m) of U_3 at a fixed point satisfy
\\ Somos-4: P_S(m+2) P_S(m-2) = alpha(m) P_S(m+1) P_S(m-1) + beta(m) P_S(m)^2 for all ten S, or
\\ Somos-5: P_S(m+3) P_S(m-2) = alpha(m) P_S(m+2) P_S(m-1) + beta(m) P_S(m+1) P_S(m),
\\ with scalars alpha(m), beta(m) common to all S (a per-m rescaling of rows multiplies every P_S by one factor and is
\\ absorbed). For each m, the 10 x 3 matrix [lhs | first | second] has rank 2 iff such scalars exist; print its singular
\\ values relative to the largest. Two normalizations: (A) the export normalization (rho = rq(-m, n), raw e_n); (B) rows
\\ divided by their largest entry. Point a = (2/7, -5/3, 1) exactly; m = 2..20.
OUT = "research/results/bmd-20261009-ci/triple-window-bilinear.txt";
default(realprecision, 200);
lam = 3/2;
rq(j, k) = prod(i = 1, k, i / (i + lam - j));
cc(n) = binomial(-lam, n);
U3(a, m) = {
  my(d = m * (m - 1) / 2, N0 = d + m, U = matrix(3, 5), prs = [[1, 2, 3], [1, 3, 2], [2, 3, 1]], top = N0 + 4);
  for (r = 1, 3, my([i, j, k] = prs[r]);
    my(e = vector(top + 1, n, sum(t = 0, n - 1, cc(t) * cc(n - 1 - t) * a[i]^t * a[j]^(n - 1 - t))));
    for (col = 1, 5, my(n = N0 + col - 1);
      U[r, col] = sum(l = 0, m, binomial(m, l) * a[k]^l * if (n - l >= 0, rq(-m, n - l) * e[n - l + 1], 0))));
  U;
}
pl(U) = { my(L = List()); forsubset([5, 3], S, my(Sv = Vec(S)); listput(L, matdet(matrix(3, 3, r, t, U[r, Sv[t]])))); Vec(L); }
rk(M) = { my(s = qfjacobi(M~ * M)[1]); s = vecsort(apply(x -> sqrt(abs(x)), s), , 4); s / s[1]; }
{
  my(a = [2/7, -5/3, 1], PA = vector(20), PB = vector(20));
  for (m = 2, 20, my(U = U3(a, m)); PA[m] = pl(U);
    my(V = matrix(3, 5, r, c, U[r, c] / vecmax(apply(abs, U[r, ])))); PB[m] = pl(V));
  foreach([["A", PA], ["B", PB]], NP, my(P = NP[2]);
    for (m = 4, 18, my(M = matrix(10, 3, s, t, [P[m + 2][s] * P[m - 2][s], P[m + 1][s] * P[m - 1][s], P[m][s]^2][t] * 1.));
      write(OUT, NP[1], " Somos-4 m = ", m, ": relative singular values ", precision(rk(M), 6)));
    for (m = 4, 17, my(M = matrix(10, 3, s, t, [P[m + 3][s] * P[m - 2][s], P[m + 2][s] * P[m - 1][s], P[m + 1][s] * P[m][s]][t] * 1.));
      write(OUT, NP[1], " Somos-5 m = ", m, ": relative singular values ", precision(rk(M), 6))));
}
