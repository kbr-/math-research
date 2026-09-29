\\ Confluent top windows at a sparse point of the discriminant (29 September 2026).
\\ Tested statement (conj:cube-confluent-top-windows, generic form): the coefficient of
\\ eps^(v0+2), v0 = k(k+1), in det C[:,W_k] (k = M-1, M; rescaled neck matrix of the neck window
\\ theorem, lambda = 3/2) is a polynomial in the coefficients of P which vanishes to lower order on
\\ the whole discriminant hypersurface; it is nonzero generically there iff it is nonzero at one
\\ point. Point: P = x^(M-2) (x^2 - 1), where every basis row except g_(M-2), g_(M-1) is a monomial.
\\ Also reports k = M-2 (theorem: val = (M-2)(M-1) generically; here the point is special).
lam = 3/2; J = 29;
OUT = getenv("OUT");
emit(s) = print(s); if (OUT != 0 && OUT != "", write(OUT, s));
beta(j) = binomial(-lam, j);
Gp(P, m, n) = polcoeff(lift(Mod(x^n, P)), m, x);
G(P, m, n) = my(M = poldegree(P)); if (m < 0, 0, if (n < M, m == n, beta(n) / beta(m) * Gp(P, m, n)));
tv = vector(J, j, polcoeff(truncate(-tanh(lam * atanh(y + O(y^(J + 2))))), j, y));
windet(P, k, NN) = {
  my(M = poldegree(P), rows = List(), S);
  for (m = 0, M - 1,
    my(u = T^m + sum(n = M, NN, G(P, m, n) * e^(n - m) * T^n));
    my(w = sum(j = 1, J, tv[j] * T^(J - j)) * u);
    listput(rows, [vector(3 * M, c, polcoeff(u, c - 1 - M, T)), vector(3 * M, c, polcoeff(w, c - 1 - M + J, T))]));
  S = vector(2 * M, i, i - (M - k) - 1);
  matdet(matrix(2 * M, 2 * M, r, c, my(m = (r - 1) % M, typ = (r - 1) \ M); rows[m + 1][typ + 1][S[c] + M + 1]));
}
main() = {
  for (M = 3, 7,
    my(P = x^(M - 2) * (x^2 - 1), NN = 2 * M + 8, out = []);
    for (k = M - 2, M,
      my(d = windet(P, k, NN), v = if (d == 0, "inf", valuation(d, e)));
      out = concat(out, [[k, v, k * (k + 1), if (d == 0, 0, polcoeff(d, valuation(d, e), e))]]));
    emit(Str("M=", M, " [k, val, k(k+1), leading coeff]: ", out)));
}
main();
