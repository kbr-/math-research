\\ Class determinants det T_c of the far spaces F_k at 0 (cycle bmd-20260930-zzq), for 1 <= e, l <= 4.
\\ T_c[i,j] = coefficient of x^(rho_j) in the i-th basis function of class c (lem:cube-far-extreme-coefficients),
\\ in class-block order.  Compared with:
\\  half-integral class: the Toeplitz binomial determinant det[binom(-5/2, sigma + t - j)]_{j,t < 4l}, sigma = 4(e+l-1),
\\    and its product formula prod_{i<m} Gamma(al+1+i) Gamma(i+1) / (Gamma(s+1+i) Gamma(al-s+1+i)), al = -5/2, s = sigma,
\\    m = 4l (Krattenthaler's binomial determinant);
\\  integral class: printed factored, to look for a product form.
default(parisizemax, 2000000000);
read("research/tools/bmd_cube_far_wronskian_lib.gp");
classdets(e, l) = {
  my(F = funcs(e, l), R = #F, rho = List(), res = vector(2));
  for (j = -(Rn(l) + 2), -3, listput(rho, j));
  for (j = 0, Rn(e) + 4*e, listput(rho, j));
  for (i = 4*e - 4*e*l, 4*e + 4*l - 1, listput(rho, -7/2 + i));
  rho = Vec(rho);
  for (ci = 1, 2, my(cls = [0, 1/2][ci]);
    my(idx = [i | i <- [1..R], frac(F[i][1]) == cls], ex = [r | r <- rho, frac(r) == cls], n = #idx);
    my(T = matrix(n, n), sh = cls, lo = vecmin(ex) - sh, L = ceil(vecmax(ex) - lo) + 3);
    for (a = 1, n, my(fi = F[idx[a]], ser = x^(fi[1] - sh - lo) * (1 + x + O(x^L))^fi[2] * fi[3]);
      for (b = 1, n, T[a, b] = polcoef(ser, ex[b] - sh - lo, x)));
    res[ci] = matdet(T));
  res;
}
toep(al, s, m) = matdet(matrix(m, m, j, t, binomial(al, s + (t - 1) - (j - 1))));
prodform(al, s, m) = prod(i = 0, m - 1, gamma(al + 1 + i) * gamma(i + 1) / (gamma(s + 1 + i) * gamma(al - s + 1 + i)));
{
  for (e = 1, 4, for (l = 1, 4,
    my(d = classdets(e, l), m = 4*l, s = 4*(e + l - 1), tp = toep(-5/2, s, m), pf = prodform(-5/2, s, m));
    print("(e,l) = ", [e, l], ": det T_half / Toeplitz = ", d[2] / tp, ", Toeplitz / product formula = ", round(tp / pf * 10^6) / 10^6,
      "; det T_int = ", factor(d[1]))));
}
