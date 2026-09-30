\\ Direct control for the peeling neck model (30 September 2026; cycle bmd-20260930-zc).
\\ The half-integral class (around the cluster loop) of E_(k-1) at D_k = eps c, for b = 4, k = 2 (e = 1, l = 2):
\\   (1 + D_s z)^(-7/2) Pol_(<4e)(z)  and  (1 + eps c z)^(-5/2) (1 + D_s z)^(-7/2) Pol_(<4)(z),  s = 3, 4.
\\ Question: do the edges of the Newton polygon (t-degree d, eps-valuation) of its Wronskian with slopes strictly
\\ between 0 and 1 (the neck, |z| ~ eps^(-alpha)) agree with the window model of bmd_cube_peeling_neck_windows.gp,
\\ which predicts slopes 1/8, 3/8, 5/8, 7/8, each of length 16 with a binomial edge polynomial?
\\ Method: normalized Taylor rows at t (as in bmd_cube_base_peeling_far.gp), determinant times
\\ (1 + D_3 t)^A (1 + D_4 t)^A (1 + eps c t)^A with A = binom(16, 2) (a polynomial; these factors only add
\\ edges of slope 0 and 1), interpolated in t (with two checks) and in eps (with two checks) modulo 2^61 - 1.
OUT = getenv("OUT");
emit(s) = print(s); if (OUT != 0 && OUT != "", write(OUT, s));
\\ normalized Taylor row of t^j prod_a (1 + a t)^ga_a at t, R coefficients
rowm(j, fa, t, R, q) = {
  my(u = vector(R, i, Mod(binomial(j, i - 1), q) * t^(j - i + 1)));
  foreach (fa, f, my(r = Mod(f[1], q) / (1 + f[1] * t), v = vector(R, s, Mod(binomial(f[2], s - 1), q) * r^(s - 1)));
    u = vector(R, m, sum(i = 1, m, u[i] * v[m + 1 - i])));
  u;
}
Qval(ep, t, q) = {
  my(D = [Mod(2, q) / 3, Mod(-3, q) / 5], c = 1, R = 16, A = binomial(16, 2), rows = List());
  foreach (D, d, for (j = 0, 3, listput(rows, rowm(j, [[d, -7/2]], t, R, q))));
  foreach (D, d, for (j = 0, 3, listput(rows, rowm(j, [[ep * c, -5/2], [d, -7/2]], t, R, q))));
  matdet(Mat(Vec(rows)~)) * ((1 + D[1] * t) * (1 + D[2] * t) * (1 + ep * c * t))^A;
}
export(rowm, Qval);
main() = {
  my(q = 2^61 - 1, DT = if (getenv("DT"), eval(getenv("DT")), 420), KE = if (getenv("KE"), eval(getenv("KE")), 260));
  my(ts = vector(DT + 3, j, Mod(j + 1, q)), es = vector(KE + 2, i, Mod(i + 1, q)));
  my(Y = parvector(KE + 2, i, vector(DT + 3, j, Qval(es[i], ts[j], q))));
  my(C = matrix(KE + 2, DT + 1));
  for (i = 1, KE + 2, my(P = polinterpolate(ts[1..DT + 1], Y[i][1..DT + 1], 'z));
    if (subst(P, 'z, ts[DT + 2]) != Y[i][DT + 2] || subst(P, 'z, ts[DT + 3]) != Y[i][DT + 3], error("t check"));
    for (d = 0, DT, C[i, d + 1] = polcoef(P, d, 'z)));
  my(v = vector(DT + 1), cs = vector(DT + 1), tdeg = -1, edeg = 0);
  for (d = 0, DT, my(cc = polinterpolate(es[1..KE], C[1..KE, d + 1]~, 'e));
    if (subst(cc, 'e, es[KE + 1]) != C[KE + 1, d + 1] || subst(cc, 'e, es[KE + 2]) != C[KE + 2, d + 1], error("e check"));
    cs[d + 1] = cc; v[d + 1] = if (cc == 0, oo, valuation(cc, 'e)); if (cc != 0, tdeg = d; edeg = max(edeg, poldegree(cc))));
  emit(Str("t-degree ", tdeg, " (", DT, " allowed), max eps-degree ", edeg, " (", KE, " points)"));
  my(pts = List()); for (d = 0, DT, if (v[d + 1] != oo, listput(pts, [d, v[d + 1]])));
  my(H = List([pts[1]]));
  for (k = 2, #pts, while (#H >= 2 && (H[#H][2] - H[#H - 1][2]) * (pts[k][1] - H[#H][1]) >= (pts[k][2] - H[#H][2]) * (H[#H][1] - H[#H - 1][1]), listpop(H)); listput(H, pts[k]));
  for (k = 2, #H, my(d0 = H[k - 1][1], d1 = H[k][1], sl = (H[k][2] - H[k - 1][2]) / (d1 - d0), nt = 0);
    for (d = d0, d1, if (v[d + 1] != oo && v[d + 1] == H[k - 1][2] + sl * (d - d0), nt++));
    emit(Str("edge slope ", -sl, " length ", d1 - d0, ", nonzero terms on the edge ", nt)));
}
default(nbthreads, 12);
default(parisizemax, 3000000000);
default(threadsizemax, 200000000);
main();
