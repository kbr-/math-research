\\ Rank pattern of the neck genericity matrix with a double roots (29 September 2026).
\\ Tested statement (thm:cube-multi-double-window-rank): for P = prod_(i<=a) (x-u_i)^2 Q, generic,
\\ lambda = 3/2: rank Gamma_k = k for k <= M-1-a, = M-1-a for M-a <= k <= M-1, and = M-a for k = M.
\\ Proved in the notebook except generic nonvanishing for M-2a <= k <= M-2-a, which this checks.
\\ One random rational point per (a, M), a = 2, 3, M = 2a+2 .. 2a+5.
OUT = getenv("OUT");
emit(s) = print(s); if (OUT != 0 && OUT != "", write(OUT, s));
beta(j) = binomial(-3/2, j);
Gp(P, m, n) = polcoeff(lift(Mod(x^n, P)), m, x);
G(P, M, m, n) = if (m < 0, 0, if (n < M, m == n, beta(n) / beta(m) * Gp(P, m, n)));
gam(P, M, k) = matrix(k, k, i, j, my(m = M - k + i - 1, D = M + j - 1); G(P, M, m, D + 1) - G(P, M, m - 1, D) - G(P, M, m, M) * G(P, M, M - 1, D));
main() = {
  setrand(2026);
  foreach ([2, 3], a,
    for (M = 2 * a + 2, 2 * a + 5,
      my(us = vector(a, i, (random(201) - 100) / (random(9) + 1)), Q = prod(i = 1, M - 2 * a, x - (random(2001) - 1000) / (random(13) + 1)));
      my(P = prod(i = 1, a, (x - us[i])^2) * Q);
      my(hyp = poldegree(gcd(P, x * deriv(P))) == a && subst(P, x, 0) != 0 && #Set(us) == a && vecmin(apply(abs, us)) > 0);
      emit(Str("a=", a, " M=", M, ": hypotheses (deg gcd(P,xP') = a, P(0) != 0, u_i distinct nonzero) hold: ", hyp));
      my(got = vector(M, k, matrank(gam(P, M, k))), pred = vector(M, k, if (k <= M - 1 - a, k, if (k < M, M - 1 - a, M - a))));
      emit(Str("a=", a, " M=", M, ": ranks ", got, " predicted ", pred, " match ", got == pred))));
}
main();
