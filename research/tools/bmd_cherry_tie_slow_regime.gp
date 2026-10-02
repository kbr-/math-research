\\ Slow regime of a cherry above a tie cluster (8 October 2026; cycle bmd-20261008-zl), lambda = 3/2, M = 4.
\\ Cross block of thm:cube-cherry-lattice-splitting in the basis w^(-lambda+t): rows V_s = (1+beta_s w)^(-lambda),
\\ coefficient c_t beta_s^t (t >= 0), and Q_s = (U_eps - 1) V_s, coefficient sum_(m>=1) c_m eps^m c_(t+m) beta_s^(t+m).
\\ Arc made q-adic: e = q^b (cherry {1, 1+e}), x = q^a, tie cluster y = (c0, 1, q^d, -3 q^(d+1)), c0 = 2;
\\ beta_s = x y_s / (1 - x y_s), eps = -e/(1+e).  For every 8-subset Lambda of the columns t in [-4, 10] the script
\\ computes v(Lambda) = val_q P_Lambda exactly (rational determinants), and prints the least value, the sets attaining
\\ it, whether they are windows Lambda_p = [-p, 7-p], and whether their union lies in an interval of 2M+1 = 9 integers
\\ (condition (W') of cor:cube-cherry-step).  It also prints the least value over non-windows with p = 1.
\\ Prediction (entry): f(p) = b(Lambda_p) + pen_p with b = a A_p + b B_p, A = (24,18,14,12), B = (4,6,10,16), pen_1 = 2d,
\\ pen_2 = pen_3 = pen_4 = 0; the leader is the window or adjacent pencil minimizing f, unless a p = 1 non-window
\\ escapes the penalty (then it would sit at b(Lambda_1) + min(a, b) + 2 val Vand-shift).
OUT = getenv("OUT");
emit(s) = print(s); if (OUT != 0 && OUT != "", write(OUT, s));
q = 1000003; M = 4; T0 = -4; T1 = 10; MMAX = 34;
cc(n) = binomial(-3/2, n);
cross(a, b, d, c0) = {
  my(x = q^a, e = q^b, ys = [c0, 1, q^d, -3 * q^(d + 1)], eps = -e / (1 + e), nc = T1 - T0 + 1, P = matrix(2 * M, nc));
  for (s = 1, M, my(be = x * ys[s] / (1 - x * ys[s]));
    for (j = 1, nc, my(t = T0 + j - 1);
      if (t >= 0, P[s, j] = cc(t) * be^t);
      P[M + s, j] = sum(m = max(1, -t), MMAX, cc(m) * eps^m * cc(t + m) * be^(t + m))));
  P;
}
iswin(L) = { my(p = #select(t -> t < 0, L)); L == [-p .. 2 * M - 1 - p]; }
run(a, b, d, c0) = {
  my(P = cross(a, b, d, c0), nc = matsize(P)[2], best = oo, arg = List(), bestnw = oo);
  forsubset([nc, 2 * M], S, my(L = apply(j -> T0 + j - 1, Vec(S)), D = matdet(vecextract(P, "..", Vec(S))));
    if (D != 0, my(v = valuation(D, q), p = #select(t -> t < 0, L));
      if (v < best, best = v; arg = List([L]), if (v == best, listput(arg, L)));
      if (p == 1 && !iswin(L) && v < bestnw, bestnw = v)));
  my(u = vecsort(concat(Vec(arg)), , 8), wins = vector(#arg, i, iswin(arg[i])));
  my(fp = vector(4, p, a * [24, 18, 14, 12][p] + b * [4, 6, 10, 16][p] + if (p == 1, 2 * d, 0)));
  \\ Equality clause for every window: val P_(Lambda_p) - (b(Lambda_p) + 2d) against pi_(M-p), with nu = (d, d+1),
  \\ pi_k = 2 sum_(i<j<=k-1) nu_i (nu_i for i <= 2 only), so pi_0..2 = 0, pi_3 = 2d, pi_4 = 6d + 2.
  my(pis = [0, 0, 0, 2 * d, 6 * d + 2], exc = vector(5, i, my(p = i - 1, L = [-p .. 2 * M - 1 - p],
      D = matdet(vecextract(P, "..", apply(t -> t - T0 + 1, L)))); valuation(D, q) - (a * [32, 24, 18, 14, 12][i] + b * [4, 4, 6, 10, 16][i] + 2 * d)));
  emit(Str("(a, b, d) = ", [a, b, d], ": window excess val - (b + 2d) for p = 0..4: ", exc, "; predicted pi_(M-p): ", vector(5, i, pis[6 - i])));
  emit(Str("(a, b, d) = ", [a, b, d], ": least val ", best, " at ", Vec(arg), "; windows ", wins, "; union ", u,
    " fits an interval of 9: ", u[#u] - u[1] <= 8, "; best p=1 non-window ", bestnw,
    "; prediction f(p) - f(min) = ", apply(z -> z - vecmin(fp), fp)));
}
{
  emit(Str("q = ", q, ", c0 = 2, columns [", T0, ", ", T1, "], m <= ", MMAX));
  \\ ARCS: the cycle-zl run used [[1,4,1],[1,4,2],[1,4,4],[1,5,2],[1,5,6],[1,3,2],[1,9,6]] (slow-regime-v2.txt); the
  \\ cycle-zm run uses the deep arcs d > w_x + w_e below (deep-arcs.txt), where the p = 1 penalty is predicted to be
  \\ capped at 2(w_x + w_e) by the deep-pair multiplicity pattern (4, 4, 2) of bmd_cross_deep_pair.gp.
  foreach([[1, 3, 6], [1, 3, 8]], A, run(A[1], A[2], A[3], 2));
}
quit
