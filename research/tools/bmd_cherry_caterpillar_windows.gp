\\ Cherry cross block over a caterpillar cluster: test of conj:cube-cherry-caterpillar-windows (7 October 2026;
\\ cycle bmd-20261007-u).  Extends bmd_cherry_caterpillar_support.gp to arbitrary inner valuations and adds the
\\ prediction.  Arc: x = s^a, e = s^b, cluster y_q = c_q s^(v_q), v_1 = 0 < v_2 < ... (v = 0: fixed cluster).
\\ Cross block of x D~ u {1, 1+e} in the basis w^(-lambda+t), w = 1+T, with the exact reparametrized roots.
\\ Prediction: the leading coordinate sets are exactly the windows Lambda_j = [-j, 2M-1-j] minimizing
\\   W_j = 2 sum_q (M-q) v_q + a A_j + b B_j + 2 sum_{i<=k} (k+1-i) v_i,  k = M-j,
\\ A_j = 2M^2-2Mj+j^2-j, B_j = j^2-j+M, and the least valuation is min_j W_j.  For a fixed generic cluster (v = 0) the
\\ Hankel term is 0 and the prediction is that of thm:cube-cherry-lattice-splitting.
\\ Method as before: ref = least window valuation; every 2M-subset of [-M-3-ext, 2M+3+ext] whose window bound
\\ 2 val Vand(y') + b(Lambda) is <= ref is computed exactly (polynomial truncation at degree NS); sets reaching
\\ outside the range are excluded when "outside bound" > least.
OUT = getenv("OUT");
emit(str) = print(str); if (OUT != 0 && OUT != "", write(OUT, str));
lam = 3/2;
cc(n) = if (n < 0, 0, binomial(-lam, n));
CS = [1, 3, -2, 5, 7];
bnd(L, M, a, b) = {
  my(p = #select(t -> t < 0, L), sp = vecsum(select(t -> t >= 0, L)), sm = vecsum(select(t -> t < 0, L)));
  a * (sp + binomial(p, 2) + M - p) + b * (binomial(p, 2) + M - p - sm);
}
runcase(M, a, b, vv, ext) = {
  my(lo = -M - 3 - ext, hi = 2*M + 3 + ext, cols = [lo .. hi], n = #cols, vV = 2 * sum(q = 1, M, (M - q) * vv[q]));
  my(W = vector(M, j, my(k = M - j); vV + a * (2*M^2 - 2*M*j + j^2 - j) + b * (j^2 - j + M) + 2 * sum(i = 1, k, (k + 1 - i) * vv[i])));
  my(wmin = vecmin(W), pred = List());
  for (j = 1, M, if (W[j] == wmin, listput(pred, [-j .. 2*M - 1 - j])));
  my(NS = vecmax(W) + 4, rows, ref = oo, best = oo, arg = List(), outb = oo);
  my(eps0 = -s^b / (1 + s^b) + O(s^NS), bet = vector(M, q, my(y = CS[q] * s^vv[q]); s^a * y / (1 - s^a * y) + O(s^NS)));
  rows = matrix(2*M, n);
  for (q = 1, M, for (u = 1, n, my(t = cols[u]);
    rows[q, u] = truncate(if (t >= 0, cc(t) * bet[q]^t, O(s^NS)));
    rows[M + q, u] = truncate(sum(r = max(1, -t), NS \ b + 1, cc(r) * cc(t + r) * eps0^r * bet[q]^(t + r)) + O(s^NS))));
  my(val = S -> my(D = matdet(vecextract(rows, "..", S))); if (D == 0, oo, my(v = valuation(D, s)); if (v >= NS, oo, v)));
  for (j = 1, M, my(S = vector(2*M, u, u - j - lo)); ref = min(ref, val(S)));
  forsubset([n, 2*M], S, my(L = apply(u -> cols[u], Vec(S)));
    if (vV + bnd(L, M, a, b) <= ref, my(v = val(Vec(S)));
      if (v < best, best = v; arg = List());
      if (v == best, listput(arg, L))));
  for (p = 1, M, outb = min(outb, vV + bnd(concat(concat([lo - 1], [-(p - 1) .. -1]), [0 .. 2*M - p - 1]), M, a, b)));
  for (p = 0, M, outb = min(outb, vV + bnd(concat(concat([-p .. -1], [0 .. 2*M - p - 2]), [hi + 1]), M, a, b)));
  my(ok = best == wmin && Set(Vec(arg)) == Set(Vec(pred)) && outb > best);
  emit(Str("M = ", M, ", a = ", a, ", b = ", b, ", v = ", vv, ": least ", best, " at ", Vec(arg), "; predicted ", wmin,
    " at ", Vec(pred), "; outside bound ", outb, "; match ", ok));
}
{
foreach([[3,1,4,[0,1,2],0], [3,1,1,[0,1,2],0], [3,4,1,[0,1,2],0], [3,1,1,[0,3,6],0], [3,1,1,[0,1,5],0], [3,2,1,[0,4,5],0],
         [3,1,1,[0,0,0],0], [3,1,2,[0,2,3],0],
         [4,1,5,[0,1,2,3],2], [4,1,1,[0,1,2,3],0], [4,5,1,[0,1,2,3],0], [4,1,2,[0,2,4,6],0], [4,1,1,[0,1,4,5],0],
         [4,2,1,[0,3,4,8],0], [4,1,3,[0,1,2,6],0], [4,1,1,[0,0,0,0],0],
         [5,1,1,[0,1,2,3,4],0], [5,1,2,[0,1,3,4,6],0]], c,
  runcase(c[1], c[2], c[3], c[4], c[5]));
}
