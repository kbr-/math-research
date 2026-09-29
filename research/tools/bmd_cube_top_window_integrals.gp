\\ Falsification test of the top-window integral formulas (29 September 2026).
\\ Claim (all M >= 3, lambda not an integer, P = (x-u)^2 Q generic): the eps^(v0+2) coefficient of
\\ det C[:,W_(M-1)] is a nonzero multiple of I1 = int_0^u (t-u)^3 Q(t)^2 dt, and that of
\\ det C[:,W_M] a nonzero multiple of I2 = int_0^u t (t-u)^3 Q(t)^2 dt (v0 = k(k+1)).
\\ Test at lambda = 3/2, M = 3, 4, u = 2, Q = (x-q) Q1 with fixed Q1, and q an algebraic number:
\\  (a) generic rational q: both valuations v0+2;
\\  (b) q a root of I1(q): val W_(M-1) > M(M-1)+2 while val W_M = M(M+1)+2;
\\  (c) q a root of I2(q): val W_M > M(M+1)+2 while val W_(M-1) = M(M-1)+2.
lam = 3/2; J = 29;
OUT = getenv("OUT");
emit(s) = print(s); if (OUT != 0 && OUT != "", write(OUT, s));
beta(j) = binomial(-lam, j);
tv = vector(J, j, polcoeff(truncate(-tanh(lam * atanh(y + O(y^(J + 2))))), j, y));
windet(P, k, NN) = {
  my(M = poldegree(P, x), R = vector(NN + 1, n, lift(Mod(x^(n - 1), P))), rows = List(), S);
  my(G(m, n) = if (m < 0, 0, if (n < M, m == n, beta(n) / beta(m) * polcoeff(R[n + 1], m, x))));
  for (m = 0, M - 1,
    my(uu = T^m + sum(n = M, NN, G(m, n) * e^(n - m) * T^n));
    my(w = sum(j = 1, J, tv[j] * T^(J - j)) * uu);
    listput(rows, [vector(3 * M, c, polcoeff(uu, c - 1 - M, T)), vector(3 * M, c, polcoeff(w, c - 1 - M + J, T))]));
  S = vector(2 * M, i, i - (M - k) - 1);
  matdet(matrix(2 * M, 2 * M, r, c, my(m = (r - 1) % M, typ = (r - 1) \ M); rows[m + 1][typ + 1][S[c] + M + 1]));
}
\\ q stays a formal variable: the determinant is computed over Q[q] and each eps-coefficient is
\\ reduced modulo f(q) (a polmod version failed only because q was created before T and e).
redval(d, f) = { my(d0 = subst(d, T, 0)); if (d0 == 0, return("inf")); for (i = 0, poldegree(d0, e), if (Mod(polcoeff(d0, i, e), f) != 0, return(i))); "inf"; }
vals(P, f) = my(M = poldegree(P, x), NN = 2 * M + 10); [redval(windet(P, M - 1, NN), f), redval(windet(P, M, NN), f)];
main() = {
  my(u = 2);
  for (M = 3, 4,
    my(Q1 = if (M == 3, 1, x - 3), pred = [M * (M - 1) + 2, M * (M + 1) + 2]);
    my(I1 = subst(intformal(subst((t - u)^3 * ((t - q) * subst(Q1, x, t))^2, t, t), t), t, u) - 0);
    my(I2 = subst(intformal(t * (t - u)^3 * ((t - q) * subst(Q1, x, t))^2, t), t, u));
    emit(Str("M=", M, " predicted generic [val W_(M-1), val W_M] = ", pred));
    emit(Str("  (a) q=5: ", vals((x - u)^2 * (x - q) * Q1, q - 5)));
    my(f1 = factor(I1)[, 1], f2 = factor(I2)[, 1]);
    foreach (f1~, f, if (poldegree(f, q) > 0,
      emit(Str("  (b) I1=0, q root of ", f, ": ", vals((x - u)^2 * (x - q) * Q1, f)))));
    foreach (f2~, f, if (poldegree(f, q) > 0,
      emit(Str("  (c) I2=0, q root of ", f, ": ", vals((x - u)^2 * (x - q) * Q1, f))))));
}
main();
