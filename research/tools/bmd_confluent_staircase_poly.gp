\\ Staircase polynomials of the confluent tie window (cycle bmd-20261009-bz, 9 October 2026).
\\ y^(s)(T) = sum_j y^(s)_(s+3m-j) T^j (degree 3m), where y^(s) annihilates the 3m single-type rows of W^c(c): equivalently
\\ [T^K](y (1+T)^(-5/2)) = 0 for K in [s+m+1, s+3m] and [T^K](y (1+cT)^(-3/2)) = 0 for K in [s+2m+1, s+3m]. Computed
\\ symbolically in c (m = 1, 2, 3, s = d, d+1) and factored over Q(c)[T], to look for a Rodrigues-type closed form. Also the
\\ reversed polynomial T^(3m) y(1/T) and its factors.
OUT = "research/results/bmd-20261009-bz/confluent-staircase-poly.txt";
default(parisizemax, 2 * 10^9);
bn(a, k) = if (k < 0, 0, binomial(a, k));
{
  for (m = 1, 3, my(d = m * (m - 1) / 2);
    foreach([d, d + 1], s,
      my(cols = vector(3 * m + 1, j, s + j - 1));
      my(A = matrix(3 * m, 3 * m + 1, r, j, my(k = cols[j]); if (r <= 2 * m, bn(-5/2, k - (r - 1)), my(n = r - 2 * m - 1); bn(-3/2, k - n) * 'c^max(k - n, 0))));
      my(K = matker(A));
      if (#K != 1, write(OUT, "m = ", m, ", s = ", s, ": kernel dimension ", #K); next);
      my(v = K[, 1], y = sum(j = 0, 3 * m, v[3 * m + 1 - j] * 'T^j), yr = sum(j = 0, 3 * m, v[j + 1] * 'T^j));
      y = y / content(y); yr = yr / content(yr);
      write(OUT, "m = ", m, ", s = ", s, ": y(T) = ", factor(y));
      write(OUT, "        reversed: ", factor(yr))));
}
