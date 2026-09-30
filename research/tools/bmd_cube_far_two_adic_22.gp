\\ Two-adic shape of the far polynomial at (e,l) = (2,2) (cycle bmd-20260930-zzv): is W = c x^A (1+x)^B mod 2,
\\ and what are its 2-adic root valuations near 0, -1 and infinity?  Uses farW of bmd_cube_far_wronskian.gp.
default(parisizemax, 8000000000);
Rn(n) = n*(2*n-1);
funcs(e, l) = {
  my(L = List());
  for (j = 0, Rn(e) - 1, listput(L, [0, 0, x^j]));
  listput(L, [0, -3, 1]);
  for (j = 0, Rn(l) - 1, listput(L, [-(Rn(l) + 2), 0, x^j]));
  for (j = 0, 4*e - 1, listput(L, [0, -7/2, x^j]));
  for (j = 0, 4*l - 1, listput(L, [1/2 - 4*l, -5/2, x^j]));
  for (j = 0, 4*e*l - 1, listput(L, [-7/2 + 4*e - 4*e*l, 0, x^j]));
  Vec(L);
}
farW(e, l) = {
  my(F = funcs(e, l), R = #F, M = matrix(R, R), Wp, v0);
  for (i = 1, R, my(al = F[i][1], be = F[i][2], p = F[i][3]);
    for (m = 0, R - 1,
      M[i, m + 1] = p;
      p = (al - m)*(1 + x)*p + (be - m)*x*p + x*(1 + x)*deriv(p, x)));
  Wp = matdet(M);
  v0 = valuation(Wp, x); Wp = Wp / x^v0;
  while (subst(Wp, x, -1) == 0, Wp = Wp / (1 + x));
  Wp;
}
segs(W, p) = {
  my(v = newtonpoly(W, p), out = List(), i = 1);
  while (i <= #v, my(j = i); while (j < #v && v[j + 1] == v[i], j++); listput(out, [v[i], j - i + 1]); i = j + 1);
  Vec(out);
}
{
  my(W = farW(2, 2), W2, sh, ok = 1);
  W = W / content(W);
  write("research/results/bmd-20260930-zzv/W_2_2.gp", W);
  W2 = W * Mod(1, 2); sh = factor(W2);
  for (i = 1, #sh~, if (lift(sh[i, 1]) != x && lift(sh[i, 1]) != x + 1, ok = 0));
  print("(e,l) = (2,2), deg ", poldegree(W), ": W = c x^A (1+x)^B mod 2: ", ok, ", mod-2 factorization ", lift(sh));
  print("   segments at 2 (slope, length): W(x) ", segs(W, 2), "; W(x-1) ", segs(subst(W, x, x - 1), 2), "; reversal ", segs(polrecip(W), 2));
}
