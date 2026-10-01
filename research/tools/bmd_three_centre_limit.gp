\\ Three-centre simultaneous limit in characteristic 3 (4 October 2026; cycle bmd-20261004-zp).
\\ Route review entry-2026-10-04-cube-limit-design-review: two-cluster limits inherit a -> 1-a and are nonclassical
\\ beyond six labels (conj:cube-two-cluster-limits-nonclassical).  Here the N labels are split into three clusters with
\\ centres 0, 1, c (branch c0 + eps*s, one zero slope per cluster, c and slopes fixed generic in F_(3^5)).  With
\\ x^2 = 1+T, z^2 = 1+cT the limit curve is the conic z^2 - c x^2 = 1 - c, rational in m:
\\   Q = m^2 - c, X = m^2 - 2m + c, Z = -m^2 + 2cm - c, x = X/Q, z = Z/Q, T = (X^2 - Q^2)/Q^2.
\\ A label at centre c0 has w = w0 (1 + eps s T / w0^2)^(1/2), w0 in {1, x, z}; (1+y)^(1/2) mod 3 has coefficients bet(u).
\\ Rows 1, T, w_i w_j are multiplied by one common polynomial G (a unit factor: jet ranks unchanged), expanded in eps,
\\ saturated coefficientwise, and the length-D Hasse jet rank of the limit is computed at three generic points m = t.
\\ Question: is the three-centre limit classical (rank D) at N = 7, 8?  Control: N = 6 with sizes (2,2,2).
\\ Env SIZES = list of [n0, n1, nc]; PREC = eps precision (default 24).
default(parisizemax, 2000000000);
bet(j) = {my(v = if(j % 3 == 1, -1, 1)); j = j \ 3; while(j > 0, if(j % 3 == 2, return(0)); j = j \ 3); v};
OUT = getenv("OUT");
emit(s) = print(s); if (OUT != 0 && OUT != "", write(OUT, s));
{
my(ff = ffinit(3, 5, 'a), g = ffgen(ff, 'a), one = g^0, m = 'm, P = if(getenv("PREC") != "" && getenv("PREC") != 0, eval(getenv("PREC")), 24));
my(c = g^2, Q = m^2 - c, X = m^2 - 2 * m + c, Z = -m^2 + 2 * c * m - c, T = (X^2 - Q^2) / Q^2);
my(w0 = [one + 0 * m, X / Q, Z / Q], cen = [0 * one, one, c]);
my(G = Q^(2 * P + 4) * X^(2 * P + 2) * Z^(2 * P + 2));
foreach(eval(getenv("SIZES")), sz,
  my(N = vecsum(sz), lab = List());
  for (t = 1, 3, for (q = 1, sz[t], listput(lab, [t, if(q == 1, 0 * one, g^(5 * t + 7 * q + 3 * t * q))])));
  lab = Vec(lab);
  my(pairs = List()); for (i = 1, N, for (j = i + 1, N, listput(pairs, [i, j]))); pairs = Vec(pairs);
  my(nr = #pairs + 2, rows = vector(nr), dmax = 0);
  \\ rows(k) = vector over eps-order e = 0..P of polynomials in m
  rows[1] = vector(P + 1, e, if(e == 1, G * one, 0 * one));
  rows[2] = vector(P + 1, e, if(e == 1, G * T, 0 * one));
  for (k = 1, #pairs, my(i = pairs[k][1], j = pairs[k][2], ti = lab[i][1], tj = lab[j][1], si = lab[i][2], sj = lab[j][2], r = vector(P + 1, e, 0 * one));
    for (u = 0, P, for (v = 0, P - u, my(f = bet(u) * bet(v) * si^u * sj^v);
      if (f != 0, r[u + v + 1] += f * w0[ti] * w0[tj] * T^(u + v) / (w0[ti]^(2 * u) * w0[tj]^(2 * v)))));
    rows[k + 2] = vector(P + 1, e, G * r[e]));
  for (k = 1, nr, for (e = 1, P + 1, my(h = rows[k][e]); if (denominator(h) != 1 && type(h) != "t_POL" && h != 0, error("G does not clear a denominator")); dmax = max(dmax, poldegree(h, m))));
  my(nc = dmax + 1, coefs = vector(P + 1, e, matrix(nr, nc, k, d, polcoef(lift(rows[k][e]), d - 1, m))));
  my(prec = P, step = 0, ranks = List(), ok = 1);
  while (1,
    my(M0 = coefs[1], ix = matindexrank(M0)[1], rk = #ix); listput(ranks, rk);
    if (rk == nr, break);
    if (prec < 1, ok = 0; break);
    my(ker = matker(M0~), Pm = matrix(nr, nr, i, j, if(i <= rk, if(j == ix[i], one, 0 * one), ker[j, i - rk])));
    my(trans = vector(prec + 1, e, Pm * coefs[e]));
    coefs = vector(prec, e, matrix(nr, nc, i, j, if(i <= rk, trans[e][i, j], trans[e + 1][i, j])));
    prec--; step++);
  if (!ok, emit(Str("sizes ", sz, ": precision exhausted, ranks ", Vec(ranks))); next);
  my(B0 = coefs[1], mov = vector(3, q, my(t = g^([5, 13, 29][q])); matrank(matrix(nr, nr, i, j, sum(d = j - 1, nc - 1, B0[i, d + 1] * binomial(d, j - 1) * t^(d - j + 1))))));
  emit(Str("sizes ", sz, " N = ", N, ", D = ", nr, ": saturation steps ", step, ", ranks ", Vec(ranks), "; generic Hasse jet ranks at m = g^5, g^13, g^29: ", mov,
    if (vecmin(mov) == nr, " (classical)", " (nonclassical)"))));
}
quit;
