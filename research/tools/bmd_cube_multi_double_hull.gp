\\ Full hull control of the multi-double neck (30 September 2026).
\\ Tested statement (thm:cube-multi-double-neck-hull, lambda = 3/2): for P = prod_(i<=a)(x-u_i)^2 Q
\\ and every 2M-set S of columns, with S_- its negative columns, j = M - |S_-|, J the omitted
\\ middle columns and S_+ its high columns,
\\   val det C[:,S] >= LB(S) + 2 c_j,  LB(S) = sum_(S_+)(D+1) - sum_J (d+1) - sum_(m=M-j)^(M-1) m,
\\ with c_j = max(0, a-M+j+1) for j < M and c_M = a; the one exception j = M-1 with S_- = {-s},
\\ s even, where the bound is LB + 2a - 1. Consequence (window excess rule, proved for a <= 2): on
\\ (0,1) the minimizers of Phi_alpha(S) = val - alpha sum S are windows only: W_k on the open
\\ intervals between the ring slopes j/M, j in {1..M-1} minus {M-a}, and exactly two windows at
\\ each ring slope. C is the rescaled neck matrix (as in bmd_cube_multi_double_window_excess.gp).
\\ Case a = 2, M = 4, Q = 1 (the smallest nonvacuous case), columns -(M+2)..2M+2, all 2M-sets;
\\ determinants are power series over F_p, p = 2^61-1, exact modulo e^V with V = 64 above every
\\ sum S in range: sum S <= 52, so an O(e^V) minor has Phi_alpha >= 64 - 52 alpha >= 12 > 4 alpha =
\\ F*(0) >= the minimum for alpha <= 1. (Comment corrected after the run; code unchanged.)
lam = 3/2; p = 2^61 - 1; V = 64;
OUT = getenv("OUT");
emit(s) = print(s); if (OUT != 0 && OUT != "", write(OUT, s));
beta(j) = binomial(-lam, j);
main() = {
  my(a = 2, M = 4, us = [3, -5], Q = 1, P = prod(i = 1, a, (x - us[i])^2) * Q);
  my(cmin = -(M + 2), cmax = 2 * M + 2, ncol = cmax - cmin + 1, NN = V + M + cmax + 4, JJ = NN + 4);
  my(tv = vector(JJ, j, polcoeff(truncate(-tanh(lam * atanh(y + O(y^(JJ + 2))))), j, y)));
  my(R = vector(NN + 1, n, lift(Mod(x^(n - 1), P))));
  my(G(m, n) = if (m < 0, 0, if (n < M, m == n, beta(n) / beta(m) * polcoeff(R[n + 1], m, x))));
  my(A = matrix(2 * M, ncol));
  for (m = 0, M - 1,
    my(uu = T^m + sum(n = M, NN, G(m, n) * e^(n - m) * T^n));
    my(w = sum(j = 1, JJ, tv[j] * T^(JJ - j)) * uu);
    for (c = 1, ncol,
      A[m + 1, c] = polcoeff(uu, cmin + c - 1, T) * Mod(1, p) + O(e^V);
      A[M + m + 1, c] = polcoeff(w, cmin + c - 1 + JJ, T) * Mod(1, p) + O(e^V)));
  my(cc(j) = if (j == M, a, max(0, a - M + j + 1)));
  my(sets = List(), vals = List(), nbig = 0, viol = 0, tight = 0, nz = 0);
  forsubset([ncol, 2 * M], s,
    my(S = vector(2 * M, i, cmin + s[i] - 1));
    my(d = matdet(matrix(2 * M, 2 * M, r, c, A[r, s[c]])));
    my(v = if (d == 0, V, valuation(d, e)));
    if (v >= V, nbig++; next);
    nz++;
    my(Sm = select(z -> z < 0, S), Sp = select(z -> z >= M, S), j = M - #Sm);
    my(Jm = setminus(Set(vector(M, i, i - 1)), Set(select(z -> z >= 0 && z < M, S))));
    my(LB = vecsum(apply(D -> D + 1, Sp)) - vecsum(apply(d -> d + 1, Vec(Jm))) - sum(m = M - j, M - 1, m));
    my(bound = LB + 2 * cc(j) - if (j == M - 1 && #Sm == 1 && Sm[1] % 2 == 0, 1, 0));
    if (v < bound, viol++; emit(Str("  VIOLATION ", S, ": val ", v, " < bound ", bound)));
    if (v == bound, tight++);
    listput(sets, S); listput(vals, v));
  emit(Str("a=", a, " M=", M, " u=", us, " Q=", Q, "; columns ", cmin, "..", cmax, ": ", nz,
    " minors below e^", V, " (", nbig, " at or above); bound violations ", viol, "; tight ", tight));
  my(W(k) = vector(2 * M, i, i - (M - k) - 1));
  emit(Str("  window valuations k=0..M: ", vector(M + 1, k, my(i = -1); for (t = 1, #sets, if (sets[t] == W(k - 1), i = vals[t])); i)));
  my(alphas = [1/8, 1/4, 1/2, 3/4, 7/8, 99/100]);
  foreach (alphas, al,
    my(best = oo, arg = List());
    for (i = 1, #sets, my(f = vals[i] - al * vecsum(sets[i]));
      if (f < best, best = f; arg = List([sets[i]]), if (f == best, listput(arg, sets[i]))));
    my(names = vector(#arg, i, my(k = -1); for (kk = 0, M, if (arg[i] == W(kk), k = kk)); if (k >= 0, Str("W", k), Str(arg[i]))));
    emit(Str("  alpha=", al, ": min ", best, " attained by ", names)));
}
main();
