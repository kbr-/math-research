\\ Window excess for multi-double clusters (29 September 2026).
\\ Tested statement (conjecture, lambda = 3/2): for P = prod_(i<=a)(x-u_i)^2 Q generic
\\ (u_i distinct nonzero, Q squarefree, Q(0)Q(u_i) != 0) and every 0 <= k <= M,
\\   val det C[:,W_k] = k(k+1) + 2 (k - rank Gamma_k),
\\ that is, each window exceeds the neck window theorem's bound by twice the corank of Gamma_k.
\\ At a = 1 this is the confluent top window theorem. Consequence (slopes of consecutive windows,
\\ each step adding 2M to sum W_k): rings at slopes j/M for j in {1..M-1} \ {M-a}, the rest at
\\ slope 1, so the neck keeps 2M(M-2) points for every a (conj:cube-hierarchical-neck-count).
\\ C is the rescaled neck matrix of the neck window theorem (rows u_m, w_m = tau u_m), computed as in
\\ bmd_cube_confluent_windows.gp, with determinants as power series over F_p, p = 2^61-1 (a first
\\ exact rational run finished only a = 2, M = 5 in 600 s); truncation NN is checked at NN + 20.
\\ Cases: a = 2, M = 5, 6, 7; a = 3, M = 7, 8; one random rational P each, hypotheses asserted.
lam = 3/2;
OUT = getenv("OUT");
emit(s) = print(s); if (OUT != 0 && OUT != "", write(OUT, s));
beta(j) = binomial(-lam, j);
Gp(P, m, n) = polcoeff(lift(Mod(x^n, P)), m, x);
G(P, m, n) = my(M = poldegree(P)); if (m < 0, 0, if (n < M, m == n, beta(n) / beta(m) * Gp(P, m, n)));
Gam(P, k) = my(M = poldegree(P)); matrix(k, k, i, j, my(m = M - k + i - 1, D = M + j - 1); G(P, m, D + 1) - G(P, m - 1, D) - G(P, m, M) * G(P, M - 1, D));
winval(P, k, NN) = {
  my(M = poldegree(P), J = NN - 1, rows = List(), S);
  my(tv = vector(J, j, polcoeff(truncate(-tanh(lam * atanh(y + O(y^(J + 2))))), j, y)));
  for (m = 0, M - 1,
    my(u = T^m + sum(n = M, NN, G(P, m, n) * e^(n - m) * T^n));
    my(w = sum(j = 1, J, tv[j] * T^(J - j)) * u);
    listput(rows, [vector(3 * M, c, polcoeff(u, c - 1 - M, T)), vector(3 * M, c, polcoeff(w, c - 1 - M + J, T))]));
  S = vector(2 * M, i, i - (M - k) - 1);
  my(A = matrix(2 * M, 2 * M, r, c, my(m = (r - 1) % M, typ = (r - 1) \ M); rows[m + 1][typ + 1][S[c] + M + 1]));
  \\ Power series over F_p with precision V: entries are exact modulo e^(NN-M+1) >= e^V, and the
  \\ determinant's valuation is read from the series (mod-p valuations are >= the rational ones).
  my(V = NN - M, p = 2^61 - 1, As = matrix(2 * M, 2 * M, r, c, A[r, c] * Mod(1, p) + O(e^V)));
  my(d = matdet(As));
  if (d == 0 || valuation(d, e) >= V - 2, error("precision"));
  valuation(d, e);
}
rq() = (random(2001) - 1000) / (random(13) + 1);
main() = {
  setrand(20260930);
  my(bad = 0);
  foreach ([[2, 5], [2, 6], [2, 7], [3, 7], [3, 8]], am,
    my(a = am[1], M = am[2], us = vector(a, i, rq()), Q = prod(i = 1, M - 2 * a, x - rq()));
    my(P = prod(i = 1, a, (x - us[i])^2) * Q);
    if (#Set(us) < a || vecmin(apply(abs, us)) == 0 || poldegree(gcd(Q, deriv(Q))) > 0
        || subst(Q, x, 0) == 0 || prod(i = 1, a, subst(Q, x, us[i])) == 0, error("hypotheses"));
    my(NN = 3 * M + 2 * M * M \ 2 + 20);
    my(rk = vector(M, k, matrank(Gam(P, k))));
    my(pred = vector(M + 1, i, my(k = i - 1); k * (k + 1) + if (k, 2 * (k - rk[k]), 0)));
    my(v1 = vector(M + 1, i, winval(P, i - 1, NN)), v2 = vector(M + 1, i, winval(P, i - 1, NN + 20)));
    if (v1 != pred || v1 != v2, bad++);
    emit(Str("a=", a, " M=", M, ": ranks Gamma_k ", rk, "; valuations ", v1, " (NN+20: ", v2, ")",
      "; predicted ", pred, "; match ", v1 == pred)));
  emit(Str("mismatches: ", bad));
}
main();
