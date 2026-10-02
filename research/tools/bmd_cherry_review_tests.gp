\\ Route review tests for the cherry windows (7 October 2026; cycle bmd-20261007-v).
\\ Part A (falsification of conj:cube-cherry-caterpillar-windows): caterpillar arcs with special leading coefficients
\\   c = (1, w3, w3^2) (cube roots of unity) and c = (1, -1, 1), M = 3, v = (0,1,2), rates (1,1) and (1,2); compared
\\   with the prediction min_j W_j and its windows (same method as bmd_cherry_caterpillar_windows.gp).
\\ Part B (Outside lead: an assignment bound): for caterpillar arcs, the least Cauchy-Binet term valuation
\\   F(Lambda) = min over N1 of f(N1) + f(N2*) + w_e (Sum N1 + Sum N2* - Sum Lambda), f(N) = sum_i n_(i) (a + v_(M+1-i)),
\\   N2* the componentwise least admissible set (n_a = max(t_a + 1, a - 1)).  Every term of P_Lambda has valuation >= F.
\\   Prints min W, F at each window with the number of minimizing N1, and the least F over non-window sets.
\\ Part C (Outside lead: Andreief-Heine): L_2 at M = 4 should vanish wherever the cluster has at most 2 distinct
\\   values (Hank_2 = 0): the limit t -> 0 of L_2(y)/... along y = (1, 1+t, 2, 2+t), with control (1, 1+t, 2, 3+t).
OUT = getenv("OUT");
emit(str) = print(str); if (OUT != 0 && OUT != "", write(OUT, str));
vv0 = [x, eps, s, t]; vz = z;
lam = 3/2;
cc(n) = if (n < 0, 0, binomial(-lam, n));
bnd(L, M, a, b) = {
  my(p = #select(u -> u < 0, L), sp = vecsum(select(u -> u >= 0, L)), sm = vecsum(select(u -> u < 0, L)));
  a * (sp + binomial(p, 2) + M - p) + b * (binomial(p, 2) + M - p - sm);
}
Wvec(M, a, b, vv) = vector(M, j, my(k = M - j); 2 * sum(q = 1, M, (M - q) * vv[q]) + a * (2*M^2 - 2*M*j + j^2 - j) + b * (j^2 - j + M) + 2 * sum(i = 1, k, (k + 1 - i) * vv[i]));
\\ Part A
runcaseA(M, a, b, vv, CS, name) = {
  my(lo = -M - 3, hi = 2*M + 3, cols = [lo .. hi], n = #cols, vV = 2 * sum(q = 1, M, (M - q) * vv[q]));
  my(W = Wvec(M, a, b, vv), wmin = vecmin(W), pred = List());
  for (j = 1, M, if (W[j] == wmin, listput(pred, [-j .. 2*M - 1 - j])));
  my(NS = vecmax(W) + 4, rows = matrix(2*M, n), ref = oo, best = oo, arg = List(), outb = oo);
  my(eps0 = -s^b / (1 + s^b) + O(s^NS), bet = vector(M, q, my(y = CS[q] * s^vv[q]); s^a * y / (1 - s^a * y) + O(s^NS)));
  for (q = 1, M, for (u = 1, n, my(tt = cols[u]);
    rows[q, u] = lift(truncate(if (tt >= 0, cc(tt) * bet[q]^tt, O(s^NS))));
    rows[M + q, u] = lift(truncate(sum(r = max(1, -tt), NS \ b + 1, cc(r) * cc(tt + r) * eps0^r * bet[q]^(tt + r)) + O(s^NS)))));
  my(val = S -> my(D = Mod(matdet(vecextract(rows, "..", S)), z^2 + z + 1)); D = lift(D);
    if (D == 0, oo, my(v = valuation(D, s)); if (v >= NS, oo, v)));
  for (j = 1, M, ref = min(ref, val(vector(2*M, u, u - j - lo))));
  forsubset([n, 2*M], S, my(L = apply(u -> cols[u], Vec(S)));
    if (vV + bnd(L, M, a, b) <= ref, my(v = val(Vec(S)));
      if (v < best, best = v; arg = List());
      if (v == best, listput(arg, L))));
  for (p = 1, M, outb = min(outb, vV + bnd(concat(concat([lo - 1], [-(p - 1) .. -1]), [0 .. 2*M - p - 1]), M, a, b)));
  for (p = 0, M, outb = min(outb, vV + bnd(concat(concat([-p .. -1], [0 .. 2*M - p - 2]), [hi + 1]), M, a, b)));
  emit(Str("A: ", name, ", M = ", M, ", (a,b) = (", a, ",", b, "), v = ", vv, ": least ", best, " at ", Vec(arg),
    "; predicted ", wmin, " at ", Vec(pred), "; outside bound ", outb, "; match ", best == wmin && Set(Vec(arg)) == Set(Vec(pred)) && outb > best));
}
\\ Part B
fval(N, M, a, vv) = my(Ns = vecsort(N)); sum(i = 1, M, Ns[i] * (a + vv[M + 1 - i]));
Fmin(L, M, a, b, vv) = {
  my(Lp = select(u -> u >= 0, L), Lm = select(u -> u < 0, L), p = #Lm, best = oo, cnt = 0);
  if (p > M || #Lp < M, return([oo, 0]));
  forsubset([#Lp, M], S, my(N1 = vecextract(Lp, Vec(S)), L2 = vecsort(setminus(Set(L), Set(N1))), N2 = vector(M));
    for (aa = 1, M, N2[aa] = max(L2[aa] + 1, aa - 1); if (aa > 1, N2[aa] = max(N2[aa], N2[aa - 1] + 1)));
    my(F = fval(N1, M, a, vv) + fval(N2, M, a, vv) + b * (vecsum(N1) + vecsum(N2) - vecsum(L)));
    if (F < best, best = F; cnt = 0); if (F == best, cnt++));
  [best, cnt];
}
runcaseB(M, a, b, vv) = {
  my(W = Wvec(M, a, b, vv), wins = vector(M, j, Fmin([-j .. 2*M - 1 - j], M, a, b, vv)), nonw = oo, arg = []);
  forsubset([3*M + 5, 2*M], S, my(L = apply(u -> u - M - 3, Vec(S)));
    if (L != [L[1] .. L[#L]], my(F = Fmin(L, M, a, b, vv)[1]); if (F < nonw, nonw = F; arg = L)));
  emit(Str("B: M = ", M, ", (a,b) = (", a, ",", b, "), v = ", vv, ": W = ", W, "; window F (value, #N1) = ", wins,
    "; least F over non-windows in [", -M - 3, ",", 2*M + 1, "] = ", nonw, " at ", arg, "; min W = ", vecmin(W)));
}
\\ Part C
leadcoef(ys, M, j) = {
  my(A = 2*M^2 - 2*M*j + j^2 - j, B = j^2 - j + M, L = vector(2*M, u, u - 1 - j), G = matrix(2*M, 2*M));
  for (q = 1, M, for (u = 1, 2*M, my(tt = L[u]);
    G[q, u] = if (tt >= 0, cc(tt) * (x * ys[q])^tt, 0);
    G[M + q, u] = sum(r = max(1, -tt), B, cc(r) * cc(tt + r) * eps^r * (x * ys[q])^(tt + r))));
  polcoef(polcoef(matdet(G), B, eps), A, x);
}
vand(ys) = prod(q = 1, #ys, prod(r = q + 1, #ys, ys[r] - ys[q]));
{
my(w3 = Mod(z, z^2 + z + 1));
runcaseA(3, 1, 1, [0, 1, 2], [1, w3, w3^2], "c = cube roots");
runcaseA(3, 1, 2, [0, 1, 2], [1, w3, w3^2], "c = cube roots");
runcaseA(3, 1, 1, [0, 1, 2], [1, -1, 1], "c = (1,-1,1)");
runcaseA(3, 2, 1, [0, 2, 3], [1, -1, 1], "c = (1,-1,1)");
runcaseB(3, 1, 1, [0, 1, 2]);
runcaseB(3, 1, 2, [0, 2, 3]);
runcaseB(4, 1, 1, [0, 1, 2, 3]);
runcaseB(4, 1, 2, [0, 2, 4, 6]);
runcaseB(3, 1, 1, [0, 0, 0]);
foreach([[1, 1 + t, 2, 2 + t], [1, 1 + t, 2, 3 + t]], ys,
  my(r = leadcoef(ys, 4, 2) / vand(ys)^2); emit(Str("C: M = 4, j = 2, y = ", ys, ": L_2 at t = 0 is ", subst(r, t, 0))));
}
