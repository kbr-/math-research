\\ Control for thm:cube-cherry-hankel-form (8 October 2026; cycle bmd-20261008-zt).
\\ Tested statement: with lambda = 3/2, c_n = binom(-3/2, n), rows V_s = sum c_t y_s^t w^t and
\\ Q_s = (U_u - 1) V_s, U_u = (1 + u/w)^(-lambda) (x = 1, eps = u), the coefficient L of u^(B_j),
\\ B_j = j^2 - j + M, in the Pluecker coordinate on the window [-j, 2M-1-j] satisfies
\\ L = c_(M,j) Vand(y)^2 Hank_(M-j)(y) with c_(M,j) a nonzero constant. Checked at two random
\\ integer points per (M, j): the two ratios must agree. Full minor, power series in u.
OUT = "research/results/bmd-20261008-zt/hankel-form-control.txt";
\\ Predicted |c_(M,j)| = |H_j c_1^k prod_(e<j) c_e prod_(i<2M-j) c_i| (1/2)^k / prod_(t=-k..k) (M+t), k = M - j.
c(n) = if(n < 0, 0, binomial(-3/2, n));
vand(Y) = prod(a = 1, #Y, prod(b = a + 1, #Y, Y[b] - Y[a]));
Hb(j) = matdet(matrix(j, j, e, k, c(e + k - 1)));
pred(M, j) = my(k = M - j); abs(Hb(j) * c(1)^k * prod(e = 0, j - 1, c(e)) * prod(i = 0, 2 * M - j - 1, c(i)) * (1/2)^k / prod(t = -k, k, M + t));
hank(Y, k) = matdet(matrix(k + 1, k + 1, a, b, sum(s = 1, #Y, Y[s]^(a + b - 2))));
lead(Y, j) = {
  my(M = #Y, B = j^2 - j + M, cols = vector(2 * M, i, -j - 1 + i));
  my(X = matrix(2 * M, 2 * M, r, i, my(t = cols[i]);
    if(r <= M, if(t >= 0, c(t) * Y[r]^t, 0),
      my(s = r - M); sum(m = max(1, -t), B, c(m) * c(t + m) * Y[s]^(t + m) * 'u^m))));
  polcoef(matdet(X), B, 'u);
};
setrand(20261008);
{
for(M = 6, 7,
  for(j = 1, M,
    my(rat = vector(2, i, my(Y = vector(M, s, random(41) - 20));
      while(vand(Y) == 0, Y = vector(M, s, random(41) - 20));
      lead(Y, j) / (vand(Y)^2 * hank(Y, M - j))));
    write(OUT, "M=", M, " j=", j, " k=", M - j, ": ratios ", rat, " equal: ", rat[1] == rat[2], " nonzero: ", rat[1] != 0, " |ratio| = predicted |c|: ", abs(rat[1]) == pred(M, j))));
}
