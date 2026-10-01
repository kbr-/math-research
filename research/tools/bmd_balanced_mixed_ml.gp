\\ Mixed block of the balanced simultaneous limit at cluster sizes (M, L) (4 October 2026; cycle bmd-20261004-zk).
\\ Question (conj:cube-balanced-simultaneous-limit-normality, shape of its limit): at (M,L) = (3,3) the saturated mixed
\\ limit was 7 consecutive middle odd powers plus 2 endpoint rows (prop:cube-generic-balanced-six-label-limit).  Does the
\\ shape persist at (3,4), (4,4): a middle interval of odd powers plus (M-1)(L-1)-1 rows outside it?  Same construction as
\\ bmd_balanced_generic_mixed.gp (rows w_i w_j / x for i in the cluster at 0 (slopes a), j in the cluster at 1 (slopes b),
\\ coefficients bet(u) bet(v) a^u b^v eps^(u+v) y^(-v) (y-1)^(u+v), y = x^2), but with fixed slopes in F_(3^5) instead of
\\ a rational function field.  Output: saturation ranks, valuation, and the reduced echelon form of the limit basis as
\\ x-exponent supports (x-exponent 1 + 2 k for y^k); a row's largest exponent is its leading exponent.
\\ Env MLS = list of [M, L]; PREC = epsilon precision (default 30).
default(parisizemax, 1000000000);
bet(j) = {my(v = if(j % 3 == 1, -1, 1)); j = j \ 3; while(j > 0, if(j % 3 == 2, return(0)); j = j \ 3); v};
OUT = getenv("OUT");
emit(s) = print(s); if (OUT != 0 && OUT != "", write(OUT, s));
{
my(ff = ffinit(3, 5, 'a), g = ffgen(ff, 'a), one = g^0, prec0 = if(getenv("PREC") != "" && getenv("PREC") != 0, eval(getenv("PREC")), 30));
foreach(eval(getenv("MLS")), ml,
  my(M = ml[1], L = ml[2], aa = vector(M, i, if(i == 1, 0 * one, g^(7 * i + 1))), bb = vector(L, j, if(j == 1, 0 * one, g^(11 * j + 3) + one)));
  my(prec = prec0, cut = prec0, nr = M * L, nc = 2 * cut + 1);
  my(coefs = vector(prec + 1, m, matrix(nr, nc, i, j, 0 * one)));
  for (i = 1, M, for (j = 1, L, for (m = 0, prec,
    my(poly = 0 * one * 'y);
    for (u = 0, m, my(v = m - u, fac = one * bet(u) * bet(v) * aa[i]^u * bb[j]^v); if (fac != 0, poly += fac * 'y^(cut - v)));
    poly *= ('y - 1)^m;
    for (k = 0, nc - 1, coefs[m + 1][L * (i - 1) + j, k + 1] = polcoef(poly, k, 'y)))));
  my(step = 0, total = 0, ranks = List());
  while (1,
    my(M0 = coefs[1], ix = matindexrank(M0)[1], rk = #ix);
    listput(ranks, rk);
    if (rk == nr, break);
    if (prec < 1, emit(Str("(M,L)=", ml, ": precision exhausted at step ", step, ", ranks ", Vec(ranks))); break);
    my(ker = matker(M0~), P = matrix(nr, nr, i, j, if(i <= rk, if(j == ix[i], one, 0 * one), ker[j, i - rk])));
    my(trans = vector(prec + 1, m, P * coefs[m]));
    coefs = vector(prec, m, matrix(nr, nc, i, j, if(i <= rk, trans[m][i, j], trans[m + 1][i, j])));
    total += nr - rk; prec--; step++);
  \\ reduced echelon of the limit basis by largest exponent: rows of B in columns k = nc-1 down to 0
  my(B = coefs[1], Bt = matrix(nr, nc, i, k, B[i, nc + 1 - k]), E = matrix(nr, nc), r = 0, lead = List());
  my(H = matimage(Bt~)~);
  \\ Gaussian elimination from the left of Bt (largest exponents first)
  my(A = Bt, row = 1);
  for (col = 1, nc, if (row > nr, break);
    my(piv = 0); for (i = row, nr, if (A[i, col] != 0, piv = i; break));
    if (!piv, next);
    my(tmp = A[row, ]); A[row, ] = A[piv, ]; A[piv, ] = tmp; A[row, ] = A[row, ] / A[row, col];
    for (i = 1, nr, if (i != row && A[i, col] != 0, A[i, ] -= A[i, col] * A[row, ]));
    listput(lead, 1 + 2 * ((nc - col) - cut)); row++);
  my(supp = vector(row - 1, i, my(s = List()); for (col = 1, nc, if (A[i, col] != 0, listput(s, 1 + 2 * ((nc - col) - cut)))); Vec(s)));
  emit(Str("(M,L)=", ml, " rows ", nr, ": saturation ranks ", Vec(ranks), ", valuation ", total, ", rank ", row - 1,
    "; leading x-exponents ", Vec(lead), "; supports ", supp)));
}
quit;
