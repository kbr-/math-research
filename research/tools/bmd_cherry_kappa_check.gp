\\ Check of the leading window coefficient in thm:cube-cherry-caterpillar-windows (7 October 2026; cycle bmd-20261007-w).
\\ Along a caterpillar arc (x = s^a, e = s^b, y_q = s^(v_q), leading coefficients 1, so lc(beta_q) = 1, lc(eps) = -1),
\\ the proof predicts val P_(Lambda_j) = W_j for EVERY window j (not only the minimizing ones), with leading coefficient
\\ of absolute value |kappa_(M,j)| = |prod_(n<M+k) c_n * prod_(n<j) c_n * prod_(i<=k) (lambda-1)/((b_i+1)(b_i+2))
\\ * det[c_(j+a-b)]_(a,b<=j) * c_1^k|, k = M-j, b_i = j+2i-2.  Prints, per (M, j), the actual valuation, W_j, the
\\ actual |leading coefficient| and |kappa|.
OUT = getenv("OUT");
emit(str) = print(str); if (OUT != 0 && OUT != "", write(OUT, str));
lam = 3/2;
cc(n) = if (n < 0, 0, binomial(-lam, n));
kap(M, j) = {
  my(k = M - j);
  abs(prod(n = 0, M + k - 1, cc(n)) * prod(n = 0, j - 1, cc(n)) * prod(i = 1, k, my(bb = j + 2*i - 2); (lam - 1) / ((bb + 1) * (bb + 2)))
      * matdet(matrix(j, j, aa, cb, cc(j + aa - cb))) * cc(1)^k);
}
check(M, a, b, vv) = {
  my(W = vector(M, j, my(k = M - j); 2 * sum(q = 1, M, (M - q) * vv[q]) + a * (2*M^2 - 2*M*j + j^2 - j) + b * (j^2 - j + M) + 2 * sum(i = 1, k, (k + 1 - i) * vv[i])));
  my(NS = vecmax(W) + 3, eps0 = -s^b / (1 + s^b) + O(s^NS), bet = vector(M, q, my(y = s^vv[q]); s^a * y / (1 - s^a * y) + O(s^NS)));
  for (j = 1, M,
    my(L = vector(2*M, u, u - 1 - j), G = matrix(2*M, 2*M));
    for (q = 1, M, for (u = 1, 2*M, my(t = L[u]);
      G[q, u] = truncate(if (t >= 0, cc(t) * bet[q]^t, O(s^NS)));
      G[M + q, u] = truncate(sum(r = max(1, -t), NS \ b + 1, cc(r) * cc(t + r) * eps0^r * bet[q]^(t + r)) + O(s^NS))));
    my(D = matdet(G), v = valuation(D, s), lcf = polcoef(D, v, s));
    emit(Str("M = ", M, ", (a,b) = (", a, ",", b, "), v = ", vv, ", j = ", j, ": val ", v, " (W_j = ", W[j], "), |lc| = ", abs(lcf),
      ", |kappa| = ", kap(M, j), ", equal: ", v == W[j] && abs(lcf) == kap(M, j))));
}
{
check(3, 1, 1, [0, 1, 2]);
check(3, 2, 3, [0, 2, 5]);
check(4, 1, 1, [0, 1, 2, 3]);
}
