\\ Export of the excess-one tie sub-window rows for Macaulay2 (8 October 2026; cycle bmd-20261008-f).
\\ Writes research/results/bmd-20261008-f/k3-m<M>.m2 for m = 2, 3, 4: the block G (c-free rows and g-rows, 3m+1 rows) and
\\ the two product rows P on the columns T^d..T^(d+3m+3), each scaled by a positive integer (the lcm of its row's
\\ denominators, recorded in the file) so that entries lie in ZZ[c]; row scaling changes neither kernels nor the zeros
\\ of minors.  research/tools/bmd_tie_k3.m2 reads them.
bn(a, k) = if (k < 0, 0, binomial(a, k));
rowco(r, m, k) = {
  if (r <= 2 * m, return(bn(-5/2, k - (r - 1))));
  if (r <= 3 * m, my(n = r - 2 * m - 1); return(bn(-3/2, k - n) * 'c^max(k - n, 0)));
  if (r == 3 * m + 1, return(bn(-3, k)));
  if (r == 3 * m + 2, return(sum(a = 0, k, bn(-3/2, a) * bn(-3/2, k - a) * 'c^(k - a))));
  sum(a = 0, k - 1, bn(-5/2, a) * bn(-3/2, k - 1 - a) * 'c^(k - 1 - a));
}
rowstr(v) = { my(s = "{"); for (j = 1, #v, s = Str(s, if (j > 1, ", ", ""), v[j])); Str(s, "}"); }
{
for (m = 2, 4, my(d = m * (m - 1) / 2, N = 3 * m + 4, rows = concat([1 .. 3 * m], [3 * m + 1, 3 * m + 2, 3 * m + 3]),
    f = Str("research/results/bmd-20261008-f/k3-m", m, ".m2"), sG = "G = matrix(R, {", sP = "P = matrix(R, {");
  for (t = 1, #rows, my(r = rows[t], v = vector(N, j, rowco(r, m, d + j - 1)), L = 1);
    for (j = 1, N, if (v[j] != 0, L = lcm(L, denominator(content(v[j])))));
    v = v * L;
    if (t <= 3 * m + 1, sG = Str(sG, if (t > 1, ",\n", ""), rowstr(v)), sP = Str(sP, if (t > 3 * m + 2, ",\n", ""), rowstr(v))));
  write(f, Str("-- m = ", m, ", d = ", d, "; rows scaled by positive integers\nm = ", m, ";\n", sG, "});\n", sP, "});"));
  print(Str("wrote ", f)));
}
quit
