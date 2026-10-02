\\ Cherry cross block over a caterpillar cluster: leading coordinate sets (7 October 2026; cycle bmd-20261007-u).
\\ Tests conj:cube-cherry-support-window: along the arc x = s^a, e = s^b, with the caterpillar D~ = {c_q delta^(q-1)},
\\ delta = s^d (d = 0: a fixed cluster), the cross block of x D~ u {1, 1+e} in the basis w^(-lambda+t), w = 1+T
\\ (rows V_q = (1+beta_q w)^(-lambda), Q_q = ((1+eps/w)^(-lambda) - 1) V_q, exact reparametrized roots
\\ eps = -e/(1+e), beta_q = x y_q/(1 - x y_q)).  The conjecture predicts that the leading coordinate sets all lie
\\ in one interval of at most 2M+2 integers.  Method: the exact s-adic valuation of every window coordinate
\\ Lambda_j = [-j, 2M-1-j] gives an upper bound ref for the least valuation; every 2M-subset of [-M-3, 2M+3] whose
\\ window bound 2 val Vand(y') + b(Lambda) (thm:cube-cherry-lattice-splitting) is <= ref is then computed exactly.
\\ Sets reaching outside the range are excluded when their least bound exceeds ref (printed as "outside bound").
\\ Prints, per arc, ref, the least valuation, its sets, and the width of their union.
OUT = getenv("OUT");
emit(str) = print(str); if (OUT != 0 && OUT != "", write(OUT, str));
lam = 3/2;
cc(n) = if (n < 0, 0, binomial(-lam, n));
CS = [1, 3, -2, 5, 7];
bnd(L, M, a, b) = {
  my(p = #select(t -> t < 0, L), sp = vecsum(select(t -> t >= 0, L)), sm = vecsum(select(t -> t < 0, L)));
  a * (sp + binomial(p, 2) + M - p) + b * (binomial(p, 2) + M - p - sm);
}
runcase(M, a, b, d) = {
  my(lo = -M - 3, hi = 2*M + 3, cols = [lo .. hi], n = #cols, vV = 2 * sum(q = 1, M, (M - q) * d * (q - 1)));
  \\ window valuations first, with generous precision, to get ref
  my(NS = vV + bnd([-M .. M - 1], M, a, b) + 4, rows, ref = oo, best = oo, arg = List(), outb = oo);
  my(eps0 = -s^b / (1 + s^b) + O(s^NS), bet = vector(M, q, my(y = CS[q] * s^(d * (q - 1))); s^a * y / (1 - s^a * y) + O(s^NS)));
  rows = matrix(2*M, n);
  for (q = 1, M, for (u = 1, n, my(t = cols[u]);
    \\ polynomial truncations: entry errors start at degree NS, so determinant valuations below NS are exact
    rows[q, u] = truncate(if (t >= 0, cc(t) * bet[q]^t, O(s^NS)));
    rows[M + q, u] = truncate(sum(r = max(1, -t), NS \ b + 1, cc(r) * cc(t + r) * eps0^r * bet[q]^(t + r)) + O(s^NS))));
  my(val = S -> my(D = matdet(vecextract(rows, "..", S))); if (D == 0, oo, my(v = valuation(D, s)); if (v >= NS, oo, v)));
  for (j = 1, M, my(S = vector(2*M, u, u - j - lo)); ref = min(ref, val(S)));
  forsubset([n, 2*M], S, my(L = apply(u -> cols[u], Vec(S)));
    if (vV + bnd(L, M, a, b) <= ref, my(v = val(Vec(S)));
      if (v < best, best = v; arg = List());
      if (v == best, listput(arg, L))));
  \\ least window bound over sets with an element just outside the range (larger elements only raise it)
  for (p = 1, M, outb = min(outb, vV + bnd(concat(concat([lo - 1], [-(p - 1) .. -1]), [0 .. 2*M - p - 1]), M, a, b)));
  for (p = 0, M, outb = min(outb, vV + bnd(concat(concat([-p .. -1], [0 .. 2*M - p - 2]), [hi + 1]), M, a, b)));
  my(U = Set(concat(Vec(arg))), wd = if (#U, U[#U] - U[1] + 1, 0));
  emit(Str("M = ", M, ", (a,b,d) = (", a, ",", b, ",", d, "): ref ", ref, ", least ", best, ", outside bound >= ", outb,
    ", sets ", Vec(arg), ", union width ", wd, " (limit 2M+2 = ", 2*M + 2, ")"));
}
{
foreach([[3,1,4,1],[3,1,1,1],[3,4,1,1],[3,2,3,1],[3,1,1,3],[3,3,2,2],[3,1,1,0],
         [4,1,5,1],[4,1,1,1],[4,5,1,1],[4,2,3,1],[4,3,2,1],[4,1,2,2],[4,1,1,0]], c,
  runcase(c[1], c[2], c[3], c[4]));
}
