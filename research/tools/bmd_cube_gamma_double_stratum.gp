\\ Review tests (29 September 2026).
\\ (1) det Gamma_k on the one-double-root stratum: Gamma_k = [G_(m,D+1) - G_(m-1,D) - G_(m,M) G_(M-1,D)]
\\     with G_(m,n) = (beta_n/beta_m) [x^n mod P]_m, beta_j = binom(-3/2,j), for P = (x-u)^2 Q with
\\     random rational u and Q (so P has exactly one double root), M = 3..8, all k = 1..M.
\\     The specialization x^(M-k-1)(x^(k+1)-c) lies in the closure of this stratum only for
\\     k <= M-3; this checks the remaining k at one random point of the stratum.
\\ (2) The rigid three-point confluent pattern (2,1,1): double root 1, simple roots -1 and 0 (branch
\\     values -1, 1 and infinity), pair space of dimension 6. Exact Wronskian numerator over Q:
\\     squarefree off the branch values? degree of the non-branch part?
OUT = getenv("OUT");
emit(s) = print(s); if (OUT != 0 && OUT != "", write(OUT, s));
beta(j) = binomial(-3/2, j);
Gp(P, m, n) = polcoeff(lift(Mod('x^n, P)), m, 'x);
G(P, M, m, n) = if (m < 0, 0, if (n < M, m == n, beta(n) / beta(m) * Gp(P, m, n)));
gam(P, M, k) = matdet(matrix(k, k, i, j, my(m = M - k + i - 1, D = M + j - 1); G(P, M, m, D + 1) - G(P, M, m - 1, D) - G(P, M, m, M) * G(P, M, M - 1, D)));
main1() = {
  setrand(4711);
  for (M = 3, 8,
    my(u = (random(201) - 100) / (random(9) + 1), Q = prod(i = 1, M - 2, 'x - (random(2001) - 1000) / (random(13) + 1)), P = ('x - u)^2 * Q);
    emit(Str("M=", M, " double-root P: det Gamma_k != 0 for k=1..", M, ": ", vector(M, k, gam(P, M, k) != 0))));
}
\\ (2) rows as in bmd_cube_confluent_weight_certificate.gp, exact over Q
serpow(u, al, L) = vector(L, m, binomial(al, m - 1) * u^(m - 1));
mul(A, B, L) = vector(L, n, sum(m = 1, n, A[m] * B[n + 1 - m]));
shiftX(A, L) = vector(L, n, if (n == 1, 0, A[n - 1]));
rowmatrix(A, S, t, L) = {
  my(ua = A / (1 + A * t), us = vector(#S, k, S[k] / (1 + S[k] * t)), rows = List());
  for (i = 1, #S, for (k = i + 1, #S, listput(rows, mul(serpow(us[i], -3/2, L), serpow(us[k], -3/2, L), L))));
  for (k = 1, #S,
    listput(rows, mul(serpow(ua, -3/2, L), serpow(us[k], -3/2, L), L));
    my(b = mul(serpow(ua, -5/2, L), serpow(us[k], -3/2, L), L));
    listput(rows, t * b + shiftX(b, L)));
  listput(rows, serpow(ua, -3, L));
  matrix(L, L, r, j, rows[r][j]);
}
main2() = {
  my(A = 1, S = [-1, 0], R = 6, E = 15, vals = [1, -1], D = 2 * E + 2, xs = List(), ys = List(), t = 1);
  while (#xs < D + 3, t++; if (prod(c = 1, #vals, 1 + vals[c] * t) == 0, next);
    listput(xs, t); listput(ys, matdet(rowmatrix(A, S, t, R)) * prod(c = 1, #vals, (1 + vals[c] * t)^E)));
  my(P = polinterpolate(Vec(xs)[1..D+1], Vec(ys)[1..D+1], 'z));
  if (subst(P, 'z, xs[D+2]) != ys[D+2], error("check"));
  my(P0 = P);
  foreach (vals, c, while (subst(P0, 'z, -1/c) == 0, P0 = P0 / ('z + 1/c)));
  emit(Str("(2,1,1): deg P=", poldegree(P), " non-branch part degree ", poldegree(P0), ", squarefree ", poldegree(gcd(P0, deriv(P0))) == 0, ", factors ", factor(P0)));
}
main1();
main2();
