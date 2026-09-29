\\ Neck blocks of a nested cluster (29 September 2026; route review, log-gas bridge test).
\\ Tested prediction: for b = (c1, c2, e c3, e c4) (two sub-clusters of two roots), the discriminant form
\\ det Gamma_k ~ sum over (k+1)-sets of squared Vandermondes gives e-valuations 0, 0, 2 for k = 1, 2, 3
\\ (ground-state energy of k+1 particles), and the Gram form e_M^2 Vandermonde^2 guessed for the top
\\ block predicts valuation 6 for k = M = 4. Prints the exact valuations at lambda = 3/2.
OUT = getenv("OUT");
emit(s) = print(s); if (OUT != 0 && OUT != "", write(OUT, s));
beta(n) = binomial(-3/2, n);
gam(b, M, k) = {
  my(P = prod(i = 1, M, x - b[i]), G = (m, n) -> if (m < 0, 0, beta(n) / beta(m) * polcoef(lift(Mod(x^n, P)), m, x)));
  matdet(matrix(k, k, r, s, my(m = M - k + r - 1, D = M + s - 1); G(m, D + 1) - G(m - 1, D) - G(m, M) * G(M - 1, D)));
}
b = [3, -5, 7 * e, 2 * e];
emit(Str("nested b = ", b, ": val det Gamma_k (k=1..4) = ", vector(4, k, valuation(gam(b, 4, k), e)), "; predicted [0, 0, 2, 6]"));
