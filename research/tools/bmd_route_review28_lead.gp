\\ Route review lead test (cycle bmd-20261009-bx, 9 October 2026): does the kernel method of thm:cube-tie-window-second-minor
\\ transfer to the confluent tie (c -> 1)? At c = 1, P = (1+T)^(2m), and the vectors x^(s)_k = p_(s+2m-k) rho^(m)_k should
\\ annihilate the rows T^n (1+T)^(-3/2) and their c-derivatives d/dc [T^n (1+cT)^(-3/2)] at c = 1 (n < m), since the
\\ rho-weighted rows are (-1)^k times polynomials of degree < 2m, killed by (1 + E^-1)^(2m). m = 2..6, s = d..d+2.
OUT = "research/results/bmd-20261009-bx/review-lead.txt";
lam = 3/2;
b(k) = if (k < 0, 0, binomial(-lam, k));
rho(j, k) = gamma(k + 1) / gamma(k + lam - j + 1);
{
  for (m = 2, 6, my(d = m * (m - 1) / 2, cols = vector(2 * m + 3, j, d + j - 1), P = (1 + 'T)^(2 * m), ok = 1);
    for (s = d, d + 2, my(x = vector(#cols, j, my(k = cols[j], i = s + 2 * m - k); if (i < 0 || i > 2 * m, 0, polcoef(P, i, 'T) * rho(m, k))));
      for (n = 0, m - 1,
        my(r0 = vector(#cols, j, b(cols[j] - n)), r1 = vector(#cols, j, (cols[j] - n) * b(cols[j] - n)));
        \\ relative tolerance (a first run used an absolute 1e-30 and failed at m = 5, 6 from the size of the Gamma values)
        my(sc = sum(j = 1, #cols, abs(r0[j] * x[j]) + abs(r1[j] * x[j])));
        if (abs(sum(j = 1, #cols, r0[j] * x[j])) + abs(sum(j = 1, #cols, r1[j] * x[j])) > 1e-25 * sc, ok = 0)));
    write(OUT, "m = ", m, ": x^(s) at c = 1 annihilate the 2m confluent rows (values and c-derivatives): ", ok));
}
