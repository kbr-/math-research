\\ Mark determinant along the three-centre family over Q (4 October 2026; cycle bmd-20261004-zx).
\\ Delta(eps) = det of the D x D matrix with rows 1, T and, for pairs i<j, the coefficients k < D of
\\ ((1 + a_i T)(1 + a_j T))^(1/2), at labels a = centre + eps * slope (dummy a = 0 in the cluster at 0, one zero slope
\\ per cluster, centres 0, 1, c).  Output: the lowest eps-order v and the factorization of its coefficient over Q, and
\\ the lowest eps-order of Delta mod 3 (the characteristic-three valuation along the same family).
\\ Question: do nonclassical multisets (mod 3) have an extra factor 3 in the characteristic-zero leading coefficient?
\\ Env SIZES, CC (centre c, integer), SL (base for slopes).
default(parisizemax, 4000000000);
OUT = getenv("OUT");
emit(s) = print(s); if (OUT != 0 && OUT != "", write(OUT, s));
{
my(cc = eval(getenv("CC")), sl = eval(getenv("SL")), e = 'e);
foreach(eval(getenv("SIZES")), sz,
  my(N = vecsum(sz), D = N * (N - 1) / 2 + 2, lab = List(), cen = [0, 1, cc]);
  for (t = 1, 3, for (q = 1, sz[t], listput(lab, cen[t] + if(q == 1, 0, (sl + 3 * t + q) * e))));
  lab = Vec(lab);
  my(bh = vector(D, k, binomial(1/2, k - 1)), M = matrix(D, D), row = 2);
  M[1, 1] = 1; M[2, 2] = 1;
  for (i = 1, N, for (j = i + 1, N, row++;
    for (k = 1, D, M[row, k] = sum(u = 0, k - 1, bh[u + 1] * bh[k - u] * lab[i]^u * lab[j]^(k - 1 - u)))));
  my(dl = matdet(M), v = valuation(dl, e), lc = polcoef(dl, v, e));
  my(d3 = dl * Mod(1, 3), v3 = if (d3 == 0, -1, valuation(lift(d3), e)));
  emit(Str("sizes ", sz, " N = ", N, ", D = ", D, ": char-0 eps-order ", v, ", leading coefficient factorization ", factor(lc),
    "; mod-3 eps-order ", v3)));
}
quit;
