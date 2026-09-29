\\ The genericity determinant of the window valuation formula.
\\
\\ U_x = <(1+b_i x)^(-lam)>, i = 1..M, has the triangular basis g_m = x^m + sum_(n>=M) G_(m,n) x^n
\\ (m < M), with G_(m,n) = (beta_n/beta_m) G'_(m,n), beta_j = binom(-lam,j), and G'_(.,n) the
\\ coefficients of x^n mod prod_i (x - b_i). For 1 <= k <= M put (G_(-1,.) = 0)
\\   Gamma_k = [ G_(m,D+1) - G_(m-1,D) - G_(m,M) G_(M-1,D) ]_(m = M-k..M-1, D = M..M+k-1).
\\ Tested statement: det Gamma_k != 0 for generic b (here: one random rational b per M, exact),
\\ for lam = 3/2 and M = 2..8, and the checkerboard Hankel minors det[t_(m+s)]_(m<n, 1<=s<=n) of
\\ tau = -tanh(lam artanh y) are nonzero for n = 1..8. With these, the Laplace expansion gives
\\ val det C[:,W_k] = M(M-1) + k(k+1) (entry of 29 September 2026, window valuation proof).
\\ Also: det Gamma_k at lam = 1 (predicted to vanish identically: at lam = 1, beta_n/beta_m = +-1
\\ and G'_(m,D+1) = G'_(m-1,D) + G'_(m,M) G'_(M-1,D)).
OUT = getenv("OUT");
emit(s) = print(s); if (OUT != 0 && OUT != "", write(OUT, s));
beta(lam, j) = binomial(-lam, j);
Gprime(b, m, n) = { my(P = prod(i = 1, #b, 'x - b[i]), r = lift(Mod('x^n, P))); polcoeff(r, m, 'x); };
G(lam, b, m, n) = if (n < #b, m == n, beta(lam, n) / beta(lam, m) * Gprime(b, m, n));
\\ Corrected after review: the entry has the extra term - G_(m,M) G_(M-1,D) from clearing the tail
\\ entries of w_m on the middle columns (G_(-1,.) = 0).
Gm(lam, b, m, n) = if (m < 0, 0, G(lam, b, m, n));
gam(lam, b, k) = { my(M = #b); matdet(matrix(k, k, i, j, my(m = M - k + i - 1, D = M + j - 1); Gm(lam, b, m, D + 1) - Gm(lam, b, m - 1, D) - Gm(lam, b, m, M) * Gm(lam, b, M - 1, D))); };
main() = {
  setrand(20260929);
  for (M = 2, 8,
    my(b = vector(M, i, (random(2001) - 1000) / (random(97) + 1)));
    my(r = vector(M, k, gam(3/2, b, k) != 0), r1 = vector(M, k, gam(1, b, k) == 0));
    emit(Str("M=", M, " lam=3/2: det Gamma_k != 0 for k=1..", M, ": ", r, "; lam=1: det Gamma_k = 0: ", r1)));
  my(y = 'y + O('y^40), tau = -tanh(3/2 * atanh(y)), t = vector(38, j, polcoeff(truncate(tau), j, 'y)));
  emit(Str("checkerboard Hankel minors det[t_(m+s)] nonzero for n=1..8: ",
    vector(8, n, matdet(matrix(n, n, i, j, t[(i - 1) + j])) != 0)));
}
main();
