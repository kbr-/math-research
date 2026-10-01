thetastep(p, alpha, beta, e) = { (1 - 'w) * ('w * deriv(p, 'w) + (beta - e) * p) - alpha * 'w * p; }
{
foreach([[2, 3], [3, 3], [2, 4], [4, 3]], v,
  my(n = v[1], k = v[2], C = n * (n - 1) / 2, P = (k - 1) * (k - 2) / 2);
  my(E = concat(vector(C + P + 2, t, t - 1 - C), vector((k - 1) * n, t, 1/2 - (n - 1) + t - 1)), q = #E);
  my(v3 = vector(k - 1, j, my(p = 'w^(j - 1), al = 1/2); for (i = 1, q, p = thetastep(p, al, 0, E[i]); al--); valuation(p, 'w)));
  my(v4 = vector(n, j, my(p = 'w^(j - 1), al = 1/2); for (i = 1, q, p = thetastep(p, al, 1/2 - (n - 1), E[i]); al--); valuation(p, 'w)));
  print([n, k], " P+2 = ", P + 2, " valuations P3: ", v3, "; (k-1)n = ", (k - 1) * n, " valuations P4: ", v4));
}
quit;
