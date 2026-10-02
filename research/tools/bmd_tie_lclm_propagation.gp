\\ Propagation recurrence of the confluent tie window (8 October 2026; cycle bmd-20261008-r, route review test).
\\ With Q = sum_r q_r(k) E^r the operator of lem:cube-tie-holonomic-staircase, the window has full rank iff the 3 x 5
\\ matrix u_a(M) = (Q e_a)(M), M = d..d+4, has rank 3, where e_1 = coefficients of (1+T)^(-3), e_2 of
\\ ((1+T)(1+cT))^(-3/2), e_3 of T(1+T)^(-5/2)(1+cT)^(-3/2).  e_1 is hypergeometric; e_2, e_3 satisfy
\\   e_2(k+2) = -((1+c)(k+5/2) e_2(k+1) + c(k+3) e_2(k)) / (k+2),
\\   e_3(k+2) = -(((1+c)(k+1)+(3+c)/2) e_3(k+1) + c(k+3) e_3(k)) / (k+1).
\\ So u_1, u_2, u_3 span a module of dimension at most 1+2+2 = 5 over Q(k, c), and their least common left multiple
\\ P = sum_(s=0..5) rho_s(M) E^s annihilates every combination.  Prints, for m = 2 (and 3), the factorization of the
\\ primitive leading coefficient rho_5(M, c) and trailing coefficient rho_0(M, c) over Q[M, c]: [deg_M, deg_c, mult],
\\ and which factors are the shifted apparent factors S(M+j, c) of Q.
default(parisizemax, 6 * 10^9);
OUT = getenv("OUT");
emit(s) = print(s); if (OUT != 0 && OUT != "", write(OUT, s));
rf(m, r) = prod(i = 0, r - 1, -('k + i - 2 * m + 7/2) / ('k + i + 1));
rg(m, r) = prod(i = 0, r - 1, -'c * ('k + i - m + 5/2) / ('k + i + 1));
fmt(F) = vector(#F[, 1], t, [poldegree(F[t, 1], 'k), poldegree(F[t, 1], 'c), F[t, 2]]);
\\ second-order shift: e(k+2) = s0(k) e(k) + s1(k) e(k+1)
S2 = [-'c * ('k + 3) / ('k + 2), -(1 + 'c) * ('k + 5/2) / ('k + 2)];
S3 = [-'c * ('k + 3) / ('k + 1), -((1 + 'c) * ('k + 1) + (3 + 'c) / 2) / ('k + 1)];
\\ coordinates of e(k+j) in the basis (e(k), e(k+1)), j = 0..J
coords(Sh, J) = {
  my(v = vector(J + 1)); v[1] = [1, 0]; v[2] = [0, 1];
  for (j = 2, J, my(s0 = subst(Sh[1], 'k, 'k + j - 2), s1 = subst(Sh[2], 'k, 'k + j - 2));
    v[j + 1] = s0 * v[j - 1] + s1 * v[j]);
  v;
}
{
foreach([2, 3], m, my(n = 3 * m, A = matrix(n, n + 1), q, rows = List(), ker, rho, ap);
  for (j = 0, 2 * m - 1, for (r = 0, n, A[j + 1, r + 1] = rf(m, r) * ('k + r)^j));
  for (j = 0, m - 1, for (r = 0, n, A[2 * m + j + 1, r + 1] = rg(m, r) * ('k + r)^j));
  q = matker(A)[, 1]; my(den = 1); for (r = 1, n + 1, den = lcm(den, denominator(q[r]))); q = q * den;
  my(g = 0); for (r = 1, n + 1, g = gcd(g, q[r])); q = q / g;
  my(F = factor(q[n + 1])); ap = 1; for (t = 1, #F[, 1], if (poldegree(F[t, 1], 'k) > 0 && poldegree(F[t, 1], 'c) > 0, ap = F[t, 1]));
  \\ u_1(M+s)/e_1(M): R_1(M+s) e_1(M+s)/e_1(M)
  my(R1 = sum(r = 0, n, q[r + 1] * (-1)^r * ('k + r + 1) * ('k + r + 2)) / (('k + 1) * ('k + 2)));
  listput(rows, vector(6, s, subst(R1, 'k, 'k + s - 1) * (-1)^(s - 1) * ('k + s) * ('k + s + 1) / (('k + 1) * ('k + 2))));
  foreach([S2, S3], Sh, my(C = coords(Sh, n + 6), u = vector(6));
    \\ u(M+s) = sum_r q_r(M+s) e(M+s+r), in the basis (e(M), e(M+1))
    for (s = 0, 5, u[s + 1] = sum(r = 0, n, subst(q[r + 1], 'k, 'k + s) * C[s + r + 1]));
    listput(rows, vector(6, s, u[s][1])); listput(rows, vector(6, s, u[s][2])));
  ker = matker(matrix(#rows, 6, i, j, rows[i][j]));
  emit(Str("m = ", m, ": kernel dimension of the 5 x 6 system: ", #ker));
  rho = ker[, 1]; my(dd = 1); for (s = 1, 6, dd = lcm(dd, denominator(rho[s]))); rho = rho * dd;
  my(gg = 0); for (s = 1, 6, gg = gcd(gg, rho[s])); rho = rho / gg;
  my(F5 = factor(rho[6]), F0 = factor(rho[1]), sh = List());
  for (t = 1, #F5[, 1], for (j = -3, 8, my(rr = F5[t, 1] / subst(ap, 'k, 'k + j)); if (poldegree(F5[t, 1], 'c) > 0 && type(rr) != "t_RFRAC" && poldegree(rr, 'k) <= 0 && poldegree(rr, 'c) <= 0, listput(sh, [t, j]))));
  emit(Str("m = ", m, ": rho_5 bidegree ", [poldegree(rho[6], 'k), poldegree(rho[6], 'c)], ", factors [deg_M, deg_c, mult] ", fmt(F5)));
  emit(Str("m = ", m, ": factors of rho_5 equal to a shifted apparent factor S(M+j, c) (factor index, j): ", Vec(sh)));
  emit(Str("m = ", m, ": rho_0 bidegree ", [poldegree(rho[1], 'k), poldegree(rho[1], 'c)], ", factors ", fmt(F0)));
  emit(Str("m = ", m, ": rho_5 factors depending on both M and c, listed: ", select(f -> poldegree(f, 'k) > 0 && poldegree(f, 'c) > 0, F5[, 1]~))));
}
quit
