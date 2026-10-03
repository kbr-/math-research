\\ Near-kernel vectors of the tie window (cycle bmd-20261009-bv, 9 October 2026).
\\ Tested statement (step of the proof of conj:cube-tie-second-minor-congruence): for s = d, d+1, d+2 the vector
\\ x^(s)_k = p_(s+2m-k) rho^(m)_k (k = s..s+2m; p_i = [T^i]((1+cT)(1+T))^m, rho^(j)_k = Gamma(k+1)/Gamma(k+lambda-j+1),
\\ lambda = 3/2) annihilates the 2m single-factor rows of the window W(c) (columns d..d+2m+2) and sends the tie row to
\\ prod_(j=-m..m-1)(lambda+j) c^m rho^(-m)_s t_s (thm:cube-tie-window-gegenbauer). m = 2..7.
OUT = "research/results/bmd-20261009-bv/tie-window-kernel.txt";
default(parisizemax, 2 * 10^9);
lam = 3/2;
b(k) = if (k < 0, 0, binomial(-lam, k));
row_t(t, n, cols) = vector(#cols, j, b(cols[j] - n) * t^(cols[j] - n));
row_top(cols) = vector(#cols, j, sum(i = 0, cols[j], b(i) * b(cols[j] - i) * 'c^i));
rho(j, k) = gamma(k + 1) / gamma(k + lam - j + 1);
tco(d) = sum(i = 0, d, b(i) * b(d - i) * 'c^i);
{
  for (m = 2, 7, my(d = m * (m - 1) / 2, cols = vector(2 * m + 3, j, d + j - 1), P = ((1 + 'c * 'T) * (1 + 'T))^m, ok = 1, okc = 1);
    for (s = d, d + 2, my(x = vector(2 * m + 3, j, my(k = cols[j], i = s + 2 * m - k); if (i < 0 || i > 2 * m, 0, polcoef(P, i, 'T) * rho(m, k))));
      for (n = 0, m - 1,
        my(ra = row_t('c, n, cols), rb = row_t(1, n, cols));
        my(va = sum(j = 1, #cols, ra[j] * x[j]), vb = sum(j = 1, #cols, rb[j] * x[j]));
        if (abs(norml2(Vec(va)) + norml2(Vec(vb))) > 1e-40, ok = 0));
      my(rc = row_top(cols), vc = sum(j = 1, #cols, rc[j] * x[j]), pred = prod(j = -m, m - 1, lam + j) * 'c^m * rho(-m, s) * tco(s));
      if (norml2(Vec(vc - pred)) > 1e-40 * (1 + norml2(Vec(pred))), okc = 0));
    write(OUT, "m = ", m, ": x^(s), s = d, d+1, d+2, annihilate the 2m single-factor rows: ", ok, "; tie-row values match the Gegenbauer identity: ", okc));
}
