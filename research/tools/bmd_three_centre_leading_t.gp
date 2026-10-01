\\ Leading eps-coefficient of the mark determinant along the three-centre family over F_3(t) (4 October 2026; cycle
\\ bmd-20261004-zz).  Labels a = centre + eps * slope, centres 0, 1, c = t; slopes distinct powers t^(k+1) (one zero slope
\\ per cluster, dummy a = 0).  Delta(eps) = det of rows 1, T, and the first D coefficients of ((1+a_i T)(1+a_j T))^(1/2)
\\ (binom(1/2, k) mod 3), computed exactly as a polynomial in F_3[t, eps].  Output: the eps-order and the factorization
\\ over F_3 of the leading coefficient.  Question (conj:cube-three-centre-leading-factorization): what is the form of the
\\ mixed factor for {1,2,4} (classical) and {1,1,5} (not)?
default(parisizemax, 4000000000);
OUT = getenv("OUT");
emit(s) = print(s); if (OUT != 0 && OUT != "", write(OUT, s));
{
my(t = 't, e = 'e, pr = if(getenv("PRIME") != "" && getenv("PRIME") != 0, eval(getenv("PRIME")), 3), fixed = getenv("FIXEDSLOPES") != "" && getenv("FIXEDSLOPES") != 0, one = Mod(1, pr));
foreach(eval(getenv("SIZES")), sz,
  my(N = vecsum(sz), D = N * (N - 1) / 2 + 2, cen = [0, 1, t], lab = List(), k = 0, t0 = getwalltime());
  for (q = 1, 3, for (r = 1, sz[q], listput(lab, cen[q] * one + if(r == 1, 0, k++; if(fixed, (7 * k^2 + 3 * k + 5), t^(k + 1)) * one * e))));
  lab = Vec(lab);
  my(bh = vector(D, j, binomial(1/2, j - 1) * one), M = matrix(D, D), row = 2);
  M[1, 1] = one; M[2, 2] = one;
  for (i = 1, N, for (j = i + 1, N, row++;
    for (kk = 1, D, M[row, kk] = sum(u = 0, kk - 1, bh[u + 1] * bh[kk - u] * lab[i]^u * lab[j]^(kk - 1 - u)))));
  my(dl = matdet(M));
  if (dl == 0, emit(Str("sizes ", sz, ": Delta = 0 identically")); next);
  my(v = valuation(dl, e), lc = polcoef(dl, v, e));
  emit(Str("sizes ", sz, " N = ", N, ": eps-order ", v, "; leading coefficient factorization over F_p (p = ", pr, if(fixed, ", fixed integer slopes", ""), "): ", factor(lc),
    " (", getwalltime() - t0, " ms)")));
}
quit;
