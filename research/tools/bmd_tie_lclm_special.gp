\\ Propagation recurrence of the confluent tie window at fixed c (8 October 2026; cycle bmd-20261008-r).
\\ Same construction as research/tools/bmd_tie_lclm_propagation.gp, with c specialized to rational c0 so that all
\\ arithmetic is over Q(k) (the bivariate factorization at m = 3 timed out at 900 s).  For m = 2, 3, 4 and
\\ c0 in {2/7, 3, -5/3}: the leading coefficient rho_5(M, c0) of the order-5 least common left multiple P of the
\\ recurrences of u_a = Q e_a; prints its factor degrees in M, its rational factors, the integer roots M >= d
\\ (which block forward propagation at this c0), and the shifts j for which S(M+j, c0) (the apparent factor of Q,
\\ i.e. the shifted pure determinant) divides rho_5.
default(parisizemax, 6 * 10^9);
OUT = getenv("OUT");
emit(s) = print(s); if (OUT != 0 && OUT != "", write(OUT, s));
coords(Sh, J) = {
  my(v = vector(J + 1)); v[1] = [1, 0]; v[2] = [0, 1];
  for (j = 2, J, v[j + 1] = subst(Sh[1], 'k, 'k + j - 2) * v[j - 1] + subst(Sh[2], 'k, 'k + j - 2) * v[j]);
  v;
}
introots(f) = { my(F = factor(f), r = List()); for (t = 1, #F[, 1], if (poldegree(F[t, 1], 'k) == 1, my(x = -polcoef(F[t, 1], 0, 'k) / polcoef(F[t, 1], 1, 'k)); if (type(x) == "t_INT", listput(r, x)))); vecsort(Vec(r)); }
{
foreach([2, 3, 4], m, foreach([2/7, 3, -5/3], c0,
  my(n = 3 * m, d = m * (m - 1) / 2, A = matrix(n, n + 1), q, rows = List(), ker, rho, ap = 1,
     rf = r -> prod(i = 0, r - 1, -('k + i - 2 * m + 7/2) / ('k + i + 1)),
     rg = r -> prod(i = 0, r - 1, -c0 * ('k + i - m + 5/2) / ('k + i + 1)),
     S2 = [-c0 * ('k + 3) / ('k + 2), -(1 + c0) * ('k + 5/2) / ('k + 2)],
     S3 = [-c0 * ('k + 3) / ('k + 1), -((1 + c0) * ('k + 1) + (3 + c0) / 2) / ('k + 1)]);
  for (j = 0, 2 * m - 1, for (r = 0, n, A[j + 1, r + 1] = rf(r) * ('k + r)^j));
  for (j = 0, m - 1, for (r = 0, n, A[2 * m + j + 1, r + 1] = rg(r) * ('k + r)^j));
  q = matker(A)[, 1]; my(den = 1); for (r = 1, n + 1, den = lcm(den, denominator(q[r]))); q = q * den;
  my(g = 0); for (r = 1, n + 1, g = gcd(g, q[r])); q = q / g;
  \\ the part of q_(3m) of degree > 1 in k: the specialized apparent factor
  my(F = factor(q[n + 1])); for (t = 1, #F[, 1], if (poldegree(F[t, 1], 'k) > 1, ap *= F[t, 1]^F[t, 2]));
  my(R1 = sum(r = 0, n, q[r + 1] * (-1)^r * ('k + r + 1) * ('k + r + 2)) / (('k + 1) * ('k + 2)));
  listput(rows, vector(6, s, subst(R1, 'k, 'k + s - 1) * (-1)^(s - 1) * ('k + s) * ('k + s + 1) / (('k + 1) * ('k + 2))));
  foreach([S2, S3], Sh, my(C = coords(Sh, n + 6), u = vector(6));
    for (s = 0, 5, u[s + 1] = sum(r = 0, n, subst(q[r + 1], 'k, 'k + s) * C[s + r + 1]));
    listput(rows, vector(6, s, u[s][1])); listput(rows, vector(6, s, u[s][2])));
  ker = matker(matrix(#rows, 6, i, j, rows[i][j]));
  rho = ker[, 1]; my(dd = 1); for (s = 1, 6, dd = lcm(dd, denominator(rho[s]))); rho = rho * dd;
  my(gg = 0); for (s = 1, 6, gg = gcd(gg, rho[s])); rho = rho / gg;
  my(F5 = factor(rho[6]), sh = List(), rest = rho[6]);
  for (j = -2, 8, my(a = subst(ap, 'k, 'k + j)); if (poldegree(a, 'k) > 0 && rest % a == 0, listput(sh, j); rest = rest / a));
  \\ the point-row factor N_1 (numerator of R_1 = (Q e_1)/e_1): which shift divides the remaining part
  \\ staircase independence: the six vectors q(M, c0), M = d..d+5, padded into C^(3m+6) at positions M-d..M-d+3m
  my(St = matrix(3 * m + 6, 6, i, j, my(r = i - j); if (r >= 0 && r <= n, subst(q[r + 1], 'k, d + j - 1), 0)));
  emit(Str("m = ", m, ", c0 = ", c0, ": rank of the six padded staircase vectors at M = d..d+5: ", matrank(St),
    "; q_(3m)(M, c0) nonzero at these M: ", vector(6, j, subst(q[n + 1], 'k, d + j - 1) != 0)));
  my(N1 = numerator(R1), shN = List()); for (j = -2, 8, if (rest % subst(N1, 'k, 'k + j) == 0, listput(shN, j)));
  emit(Str("m = ", m, ", c0 = ", c0, ": deg N_1 = ", poldegree(N1, 'k), ", N_1(M+j) divides the remaining part for j = ", Vec(shN)));
  emit(Str("m = ", m, ", c0 = ", c0, ": kernel dimension ", #ker, "; deg rho_5 = ", poldegree(rho[6], 'k), ", factor degrees ",
    vector(#F5[, 1], t, [poldegree(F5[t, 1], 'k), F5[t, 2]]), "; linear factors ", select(f -> poldegree(f, 'k) == 1, F5[, 1]~),
    "; integer roots >= d = ", d, ": ", select(x -> x >= d, introots(rho[6])), "; shifted apparent factors S(M+j) divide for j = ", Vec(sh),
    "; remaining degree ", poldegree(rest, 'k)))));
}
quit
