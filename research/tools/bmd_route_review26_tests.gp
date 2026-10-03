\\ Route review tests (cycle bmd-20261009-bp, 9 October 2026).
\\ (1) Four-root C-block tie (ex:cube-cblock-midpoint-tie): y* = (0,1,3,4), arc y* + s v, x = x1 s. The leading C-block
\\     vector is alpha e_T0 + beta e_S0 with alpha = x1^15 [s]p_T0, beta = x1^16 p_S0(y*), S0 = {0..4,6}. By
\\     lem:cube-leading-wronskian-sum E has weight 1 iff alpha Vand(T0) + beta Vand(S0) = 0: report the unique bad x1 and
\\     its sign for several directions v (total-positivity bridge: is the bad x1 always negative for real arcs?).
\\ (2) Richardson lead: the linear form Y -> Vand(Y) is nonzero at the torus-fixed point e_S0 of the Richardson variety
\\     X_[T0, S0], so its zero set there is a proper hypersurface (checked: Vand(S0) != 0).
OUT = "research/results/bmd-20261009-bp/review-tests.txt";
default(parisizemax, 2 * 10^9);
vand(Y) = prod(i = 1, #Y, prod(j = i + 1, #Y, Y[j] - Y[i]));
{
  my(R = 6, K = 7, NS = 4, ys = [0, 1, 3, 4], T0 = [0 .. 5], S0 = [0, 1, 2, 3, 4, 6]);
  foreach([[1, 2, -1, 5], [1, 0, 0, 0], [0, 0, 0, 1], [2, -3, 1, 1], [-1, 4, 2, -2]], v,
    my(Ys = vector(4, i, ys[i] + v[i] * 's + O('s^NS)), P = matrix(R, K), r = 0);
    for (i = 1, 4, for (j = i + 1, 4, r++;
      my(f = ((1 + Ys[i] * 'x + O('x^K)) * (1 + Ys[j] * 'x))^(-3/2));
      for (k = 1, K, P[r, k] = polcoef(f, k - 1, 'x))));
    my(pT = matdet(matrix(R, R, i, j, P[i, T0[j] + 1])), pS = matdet(matrix(R, R, i, j, P[i, S0[j] + 1])));
    my(c1 = polcoef(pT, 1, 's), c0 = polcoef(pT, 0, 's), b0 = polcoef(pS, 0, 's));
    my(x1bad = if (b0 != 0, -c1 * vand(T0) / (b0 * vand(S0)), oo));
    write(OUT, "(1) v = ", v, ": [s^0]p_T0 = ", c0, ", [s^1]p_T0 = ", c1, ", p_S0(y*) = ", b0, "; bad x1 = ", x1bad, ", sign ", sign(x1bad)));
  write(OUT, "(2) Vand(T0) = ", vand(T0), ", Vand(S0) = ", vand(S0), ": the form is nonzero at both torus-fixed endpoints of the Richardson variety");
}
