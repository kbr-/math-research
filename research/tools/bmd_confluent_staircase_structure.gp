\\ Structure of the confluent tie window's staircase vectors (cycle bmd-20261009-by, 9 October 2026).
\\ Question: the 3m single-type rows of W^c(c) ((1+T)^(-5/2) T^i, i < 2m; T^n (1+cT)^(-3/2), n < m; columns d..d+3m+4,
\\ d = binom(m,2)) have, for each start s = d..d+4, a unique (up to scale) annihilating vector y^(s) supported on
\\ [s, s+3m]. Do they have the Toeplitz-times-diagonal form y^(s)_k = kappa_s p_(s+3m-k) w_k of the tie window
\\ (thm:cube-tie-window-second-minor)? Test: the ratios y^(s)_(s+i) / y^(s+1)_(s+1+i-1), normalized by i = 3m, must not
\\ depend on s. Also tries the natural guess p = coefficients of (1+T)^(2m)(1+cT)^m. Exact at c = 7/3, m = 1..5.
OUT = "research/results/bmd-20261009-by/confluent-staircase-structure.txt";
bn(a, k) = if (k < 0, 0, binomial(a, k));
{
  my(c = 7/3);
  for (m = 1, 5, my(d = m * (m - 1) / 2, ys = List(), ok = 1);
    for (s = d, d + 4,
      my(cols = vector(3 * m + 1, j, s + j - 1));
      my(A = matrix(3 * m, 3 * m + 1, r, j, my(k = cols[j]); if (r <= 2 * m, bn(-5/2, k - (r - 1)), my(n = r - 2 * m - 1); bn(-3/2, k - n) * c^max(k - n, 0))));
      my(K = matker(A));
      if (#K != 1, ok = 0; write(OUT, "m = ", m, ", s = ", s, ": kernel dimension ", #K));
      listput(ys, K[, 1]));
    \\ product test: r_s(i) = y^(s)[i+1] / y^(s+1)[i] for i = 1..3m (0-based i of y^(s) vs i-1 of y^(s+1))
    my(prod_ok = 1, rs = List());
    for (t = 1, 4, my(a = ys[t], b = ys[t + 1], r = vector(3 * m, i, if (b[i] == 0, oo, a[i + 1] / b[i])));
      my(rn = vector(3 * m, i, if (r[i] == oo || r[3 * m] == oo, oo, r[i] / r[3 * m]))); listput(rs, rn));
    for (t = 2, 4, if (rs[t] != rs[1], prod_ok = 0));
    \\ guess: P = (1+T)^(2m) (1+cT)^m; is y^(s)_k / p_(s+3m-k) independent of s (as a function of k)?
    my(P = (1 + 'T)^(2 * m) * (1 + c * 'T)^m, wtab = Map(), guess_ok = 1);
    for (t = 1, 5, my(s = d + t - 1, y = ys[t] / ys[t][3 * m + 1]);
      for (i = 0, 3 * m, my(k = s + i, p = polcoef(P, 3 * m - i, 'T));
        if (p == 0, next);
        my(wv = y[i + 1] / p);
        if (mapisdefined(wtab, k), if (mapget(wtab, k) != wv, guess_ok = 0), mapput(wtab, k, wv))));
    write(OUT, "m = ", m, ": one staircase vector per start: ", ok, "; Toeplitz-times-diagonal (ratio test): ", prod_ok,
          "; with p from (1+T)^(2m)(1+cT)^m and the top normalization: ", guess_ok));
}
