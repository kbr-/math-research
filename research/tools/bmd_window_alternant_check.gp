\\ Hypergeometric alternant formula for the windows (9 October 2026; cycle bmd-20261009-b).
\\ Tested statement (lem:cube-cross-hypergeometric-alternant): for the window Lambda_p = [-p, 2M-1-p], 1 <= p <= M,
\\ k = M - p, the cherry cross coordinate (x = 1, eps = u, lambda = 3/2) satisfies, as power series in u,
\\   P_Lambda = kappa_(M,p) * Vand(y) * det[ u^n F_n(u y_s) (n = 1..p) | sum_i (P z^j)_i y_s^i F_i(u y_s)/c_i (j < k) ]_s,
\\ with F_n(w) = sum_m c_m c_(n+m) w^m, P = prod (z - y_s), and kappa a nonzero constant independent of y and u.
\\ Checked: the ratio is the same series-constant at two random rational points, to u^(B_p + 6).
c(n) = if(n < 0, 0, binomial(-3/2, n));
F(n, w, T) = sum(m = 0, T, c(m) * c(n + m) * w^m);
vand(Y) = prod(a = 1, #Y, prod(b = a + 1, #Y, Y[b] - Y[a]));
lhs(Y, p, T) = {
  my(M = #Y, L = vector(2 * M, i, -p - 1 + i));
  matdet(matrix(2 * M, 2 * M, r, i, my(t = L[i]);
    if(r <= M, if(t >= 0, c(t) * Y[r]^t, 0),
      my(s = r - M); sum(m = max(1, -t), T, c(m) * c(t + m) * Y[s]^(t + m) * 'u^m)))) + O('u^(T + 1));
};
rhs(Y, p, T) = {
  my(M = #Y, k = M - p, P = prod(s = 1, M, 'z - Y[s]));
  my(A = matrix(M, M, a, s,
    if(a <= p, 'u^a * F(a, 'u * Y[s], T),
      my(j = a - p - 1, f = P * 'z^j); sum(i = 0, poldegree(f, 'z), polcoef(f, i, 'z) * Y[s]^i * F(i, 'u * Y[s], T) / c(i)))));
  vand(Y) * matdet(A) + O('u^(T + 1));
};
{
  setrand(9);
  for (M = 2, 4, for (p = 1, M,
    my(B = p^2 - p + M, T = B + 6, r = vector(2));
    for (i = 1, 2, my(Y = vector(M, s, (random(41) - 20) / (random(5) + 1)));
      while(vand(Y) == 0, Y = vector(M, s, (random(41) - 20) / (random(5) + 1)));
      r[i] = lhs(Y, p, T) / rhs(Y, p, T));
    print("M=", M, " p=", p, ": ratio at point 1 = ", r[1], "; equal at both points: ", r[1] == r[2])));
}
