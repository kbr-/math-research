\\ Confluent neck windows (29 September 2026).
\\ Tested statements, for lambda = 3/2 and monic P of degree M:
\\ (1) Remainder identity: for D >= M and m >= 1,
\\     Gamma_(m,D) = (beta_D/beta_m) (lambda-1)/((D+1) m) * [x^m] rem(x P' B_D, P),
\\     B_D = q_D - (D+1)/M q_D(0), q_D = quo(x^(D+1), P); and row 0 is
\\     Gamma_(0,D) = beta_D (lambda-1)(D-M+1)/((D+1)M) [x^M mod P]_0 q_D(0).
\\     Checked at a random squarefree P and a random P = (x-u)^2 Q.
\\ (2) On P = (x-u)^2 Q (u, Q generic): rank Gamma_(M-2) = M-2, rank Gamma_(M-1) = M-2,
\\     rank Gamma_M = M-1 (predicted by the identity: the columns lie in {f(0)=f(u)=0}).
\\ (3) Conjecture: on that stratum val det C[:,W_k] = k(k+1) for k <= M-2, and
\\     val det C[:,W_(M-1)] = M(M-1)+1, val det C[:,W_M] = M(M+1)+1.
\\     C is the rescaled neck matrix of the neck window theorem (rows u_m, w_m = tau u_m).
lam = 3/2; NN = 30; J = 29;
OUT = getenv("OUT");
emit(s) = print(s); if (OUT != 0 && OUT != "", write(OUT, s));
beta(j) = binomial(-lam, j);
Gp(P, m, n) = polcoeff(lift(Mod(x^n, P)), m, x);
G(P, m, n) = my(M = poldegree(P)); if (m < 0, 0, if (n < M, m == n, beta(n) / beta(m) * Gp(P, m, n)));
Gam(P, k) = my(M = poldegree(P)); matrix(k, k, i, j, my(m = M - k + i - 1, D = M + j - 1); G(P, m, D + 1) - G(P, m - 1, D) - G(P, m, M) * G(P, M - 1, D));
ident(P) = {
  my(M = poldegree(P), bad = 0);
  for (D = M, 2 * M + 2,
    my(q = (x^(D + 1)) \ P, B = q - (D + 1) / M * polcoeff(q, 0), h = lift(Mod(x * deriv(P) * B, P)));
    for (m = 0, M - 1,
      my(lhs = G(P, m, D + 1) - G(P, m - 1, D) - G(P, m, M) * G(P, M - 1, D));
      my(rhs = if (m == 0, beta(D) * (lam - 1) * (D - M + 1) / ((D + 1) * M) * Gp(P, 0, M) * polcoeff(q, 0),
                   beta(D) / beta(m) * (lam - 1) / ((D + 1) * m) * polcoeff(h, m)));
      if (lhs != rhs, bad++)));
  bad;
}
tv = vector(J, j, polcoeff(truncate(-tanh(lam * atanh(y + O(y^(J + 2))))), j, y));
winval(P, k) = {
  my(M = poldegree(P), rows = List(), S);
  for (m = 0, M - 1,
    my(u = T^m + sum(n = M, NN, G(P, m, n) * e^(n - m) * T^n));
    my(w = sum(j = 1, J, tv[j] * T^(J - j)) * u);
    listput(rows, [vector(3 * M, c, polcoeff(u, c - 1 - M, T)), vector(3 * M, c, polcoeff(w, c - 1 - M + J, T))]));
  S = vector(2 * M, i, i - (M - k) - 1);
  my(A = matrix(2 * M, 2 * M, r, c, my(m = (r - 1) % M, typ = (r - 1) \ M); rows[m + 1][typ + 1][S[c] + M + 1]));
  valuation(matdet(A), e);
}
main() = {
  setrand(20260929);
  for (M = 3, 6,
    my(Q = prod(i = 1, M - 2, x - (random(2001) - 1000) / (random(13) + 1)), u = (random(201) - 100) / (random(9) + 1));
    my(Pd = (x - u)^2 * Q, Ps = Q * (x - u) * (x - u - 1/7));
    if (poldegree(gcd(Q, (x - u) * deriv(Q))) > 0 || subst(Pd, x, 0) == 0, error("genericity"));
    emit(Str("M=", M, " identity mismatches: squarefree ", ident(Ps), ", double ", ident(Pd)));
    emit(Str("M=", M, " double-root ranks Gamma_(M-2), Gamma_(M-1), Gamma_M: ",
      [matrank(Gam(Pd, M - 2)), matrank(Gam(Pd, M - 1)), matrank(Gam(Pd, M))], " predicted ", [M - 2, M - 2, M - 1]));
    if (M <= 5,
      emit(Str("M=", M, " double-root window valuations k=0..M: ", vector(M + 1, k, winval(Pd, k - 1)),
        " conjectured ", vector(M + 1, k, (k - 1) * k + (k - 1 >= M - 1))))));
}
main();
