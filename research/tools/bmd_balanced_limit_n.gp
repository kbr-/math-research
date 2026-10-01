\\ Balanced simultaneous limit at N labels (4 October 2026; cycle bmd-20261004-zl).
\\ Tests conj:cube-balanced-simultaneous-limit-normality at N = 7, 8, the first sizes past the proved six-label case:
\\ characteristic 3, labels split M = floor(N/2) near 0 (branch eps*s) and L = ceil(N/2) near 1 (branch 1 + eps*s), one
\\ zero slope per cluster, other slopes fixed generic elements of F_(3^5).  Rows 1, T, w_i w_j (D = binom(N,2) + 2) in the
\\ rational coordinate x^2 = 1 + T, exactly as bmd_balanced_cluster_limit.gp (whose six-label run is the control N = 6);
\\ coefficientwise saturation over the smoothing DVR, then the length-D Hasse jet matrix at x = 1 of the limit.
\\ The conjecture predicts an invertible jet matrix.  Env NS = list of N; PREC = epsilon precision (default 40); SEED shifts the slopes.
\\ Also: jet ranks at three generic points x = t (moving-point criterion, lem:cube-moving-point-limit-criterion).
default(parisizemax, 2000000000);
bet(j) = {my(v = if(j % 3 == 1, -1, 1)); j = j \ 3; while(j > 0, if(j % 3 == 2, return(0)); j = j \ 3); v};
OUT = getenv("OUT");
emit(s) = print(s); if (OUT != 0 && OUT != "", write(OUT, s));
{
my(ff = ffinit(3, 5, 'a), g = ffgen(ff, 'a), one = g^0, x = 'x, prec0 = if(getenv("PREC") != "" && getenv("PREC") != 0, eval(getenv("PREC")), 40));
foreach(eval(getenv("NS")), N,
  my(M = if(getenv("MFIX") != "" && getenv("MFIX") != 0, eval(getenv("MFIX")), N \ 2), L = N - M, base = vector(N, i, if(i <= M, 0, 1)));
  my(sd = if(getenv("SEED") != "" && getenv("SEED") != 0, eval(getenv("SEED")), 0));
  my(slopes = vector(N, i, if(i == 1 || i == M + 1, 0 * one, if(i <= M, g^(7 * i + 1 + 5 * sd), g^(11 * i + 3 + 3 * sd) + one))));
  for (i = 1, N, for (j = i + 1, N, if (base[i] == base[j] && slopes[i] == slopes[j], error("slope collision"))));
  my(prec = prec0, cut = prec0, pairs = List());
  for (i = 1, N, for (j = i + 1, N, listput(pairs, [i, j])));
  pairs = Vec(pairs);
  my(nr = #pairs + 2, nc = 4 * cut + 3, coefs = vector(prec + 1, m, matrix(nr, nc, i, j, 0 * one)));
  coefs[1][1, 2 * cut + 1] = one; coefs[1][2, 2 * cut + 1] = -one; coefs[1][2, 2 * cut + 3] = one;
  for (k = 1, #pairs, my(ii = pairs[k][1], jj = pairs[k][2]);
    for (m = 0, prec, my(poly = 0 * one);
      for (u = 0, m, my(v = m - u, fac = bet(u) * bet(v) * slopes[ii]^u * slopes[jj]^v);
        if (fac != 0, poly += fac * x^(2 * cut + base[ii] + base[jj] - 2 * (base[ii] * u + base[jj] * v))));
      poly *= (x^2 - 1)^m;
      for (d = 0, nc - 1, coefs[m + 1][k + 2, d + 1] = polcoef(poly, d, x))));
  my(step = 0, ranks = List(), ok = 1);
  while (1,
    my(M0 = coefs[1], ix = matindexrank(M0)[1], rk = #ix);
    listput(ranks, rk);
    if (rk == nr, break);
    if (prec < 1, ok = 0; break);
    my(ker = matker(M0~), P = matrix(nr, nr, i, j, if(i <= rk, if(j == ix[i], one, 0 * one), ker[j, i - rk])));
    my(trans = vector(prec + 1, m, P * coefs[m]));
    coefs = vector(prec, m, matrix(nr, nc, i, j, if(i <= rk, trans[m][i, j], trans[m + 1][i, j])));
    prec--; step++);
  if (!ok, emit(Str("N=", N, " (M,L)=(", M, ",", L, "): precision exhausted, ranks ", Vec(ranks), "; no conclusion")); next);
  my(B0 = coefs[1], J = matrix(nr, nr, i, j, sum(d = 0, nc - 1, B0[i, d + 1] * binomial(d, j - 1))), rkJ = matrank(J));
  my(lead = vector(nr, i, my(e = -10^9); for (d = 0, nc - 1, if (B0[i, d + 1] != 0, e = d - 2 * cut)); e));
  \\ cycle bmd-20261004-zm: reduced echelon of the limit by largest exponent; supports (Laurent exponents of x), and the
  \\ mod-3 rank of (binom(e, k))_(e in leading exponents, k < D) after shifting all exponents by 2 cut (monomial model)
  if (getenv("SUPPORTS") != "" && getenv("SUPPORTS") != 0,
    my(A = matrix(nr, nc, i, k, B0[i, nc + 1 - k]), row = 1, lead = List());
    for (col = 1, nc, if (row > nr, break);
      my(piv = 0); for (i = row, nr, if (A[i, col] != 0, piv = i; break));
      if (!piv, next);
      my(tmp = A[row, ]); A[row, ] = A[piv, ]; A[piv, ] = tmp; A[row, ] = A[row, ] / A[row, col];
      for (i = 1, nr, if (i != row && A[i, col] != 0, A[i, ] -= A[i, col] * A[row, ]));
      listput(lead, nc - col); row++);
    my(supp = vector(nr, i, my(s = List()); for (col = 1, nc, if (A[i, col] != 0, listput(s, nc - col - 2 * cut))); Vec(s)));
    my(Bm = matrix(nr, nr, i, j, Mod(binomial(lead[i], j - 1), 3)));
    emit(Str("N=", N, ": reduced supports ", supp, "; monomial-model rank of binom(leading exponent, k) mod 3: ", matrank(Bm), " of ", nr)));
  \\ moving point: Hasse jets at x = t for t = g^5, g^13, g^29 (generic points of F_(3^5))
  my(mov = vector(3, q, my(t = g^([5, 13, 29][q])); matrank(matrix(nr, nr, i, j, sum(d = j - 1, nc - 1, B0[i, d + 1] * binomial(d, j - 1) * t^(d - j + 1))))));
  emit(Str("N=", N, " (M,L)=(", M, ",", L, "): seed ", sd, ", moving-point jet ranks at x = g^5, g^13, g^29: ", mov));
  emit(Str("N=", N, " (M,L)=(", M, ",", L, "): D = ", nr, ", saturation steps ", step, ", ranks ", Vec(ranks),
    "; length-D Hasse jet rank at x=1: ", rkJ, if (rkJ == nr, " (invertible: conjecture holds at these slopes)", " (SINGULAR)"),
    "; largest exponents of saturated rows ", vecsort(lead))));
}
quit;
