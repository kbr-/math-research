\\ Full hull test of the confluent neck (29 September 2026).
\\ Tested statement (Case A and Case B control on the one-double-root stratum): for generic
\\ P = (x-u)^2 Q and lambda = 3/2, among all 2M-sets S of columns in a range, W_(M-2) is the unique
\\ minimizer of Phi_alpha(S) = val det C[:,S] - alpha sum S for alpha in ((M-2)/M, 1), and at
\\ alpha = 1 the minimizers include W_(M-2), W_(M-1), W_M (C: rescaled neck matrix of the neck
\\ window theorem). Also checks alpha in (k/M,(k+1)/M), k <= M-3, against W_k.
\\ Env MM = M; columns cmin..cmax; one random rational P with the stratum hypotheses checked.
lam = 3/2; J = 40;
OUT = getenv("OUT");
emit(s) = print(s); if (OUT != 0 && OUT != "", write(OUT, s));
beta(j) = binomial(-lam, j);
tv = vector(J, j, polcoeff(truncate(-tanh(lam * atanh(y + O(y^(J + 2))))), j, y));
main() = {
  my(M = eval(getenv("MM")), cmin = -(M + 2), cmax = 2 * M + 2, NN = cmax + 14, ncol = cmax - cmin + 1);
  setrand(7 + M);
  my(Q = prod(i = 1, M - 2, x - (random(2001) - 1000) / (random(13) + 1)), u = (random(201) - 100) / (random(9) + 1));
  my(P = (x - u)^2 * Q);
  if (poldegree(gcd(Q, (x - u) * deriv(Q))) > 0 || subst(P, x, 0) == 0 || u == 0, error("genericity"));
  my(R = vector(NN + 1, n, lift(Mod(x^(n - 1), P))));
  my(G(m, n) = if (m < 0, 0, if (n < M, m == n, beta(n) / beta(m) * polcoeff(R[n + 1], m, x))));
  my(A = matrix(2 * M, ncol));
  for (m = 0, M - 1,
    my(uu = T^m + sum(n = M, NN, G(m, n) * e^(n - m) * T^n));
    my(w = sum(j = 1, J, tv[j] * T^(J - j)) * uu);
    for (c = 1, ncol, A[m + 1, c] = polcoeff(uu, cmin + c - 1, T); A[M + m + 1, c] = polcoeff(w, cmin + c - 1 + J, T)));
  my(sets = List(), vals = List());
  forsubset([ncol, 2 * M], s,
    my(d = matdet(matrix(2 * M, 2 * M, r, c, A[r, s[c]])));
    if (d != 0, listput(sets, vector(2 * M, i, cmin + s[i] - 1)); listput(vals, valuation(d, e))));
  emit(Str("M=", M, " columns ", cmin, "..", cmax, ": ", #sets, " nonzero minors"));
  my(W(k) = vector(2 * M, i, i - (M - k) - 1));
  my(alphas = concat(vector(M - 2, k, (2 * k - 1) / (2 * M)), [(2 * M - 3) / (2 * M), (M - 1) / M, (M - 1) / M + 1 / (4 * M), 9/10, 99/100, 1]));
  foreach (alphas, al,
    my(best = oo, arg = List());
    for (i = 1, #sets, my(f = vals[i] - al * vecsum(sets[i]));
      if (f < best, best = f; arg = List([sets[i]]), if (f == best, listput(arg, sets[i]))));
    my(names = vector(#arg, i, my(k = -1); for (kk = 0, M, if (arg[i] == W(kk), k = kk)); if (k >= 0, Str("W", k), Str(arg[i]))));
    emit(Str("  alpha=", al, ": min ", best, " attained by ", names)));
  emit(Str("  window valuations k=0..M: ", vector(M + 1, k, my(i = 0); for (t = 1, #sets, if (sets[t] == W(k - 1), i = vals[t])); i)));
}
main();
