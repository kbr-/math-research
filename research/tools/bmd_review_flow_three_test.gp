\\ Route review (cycle kfk, 9 October 2026): falsification test of the graded vanishing at flow order three.
\\ Statement tested (conj:cube-flow-order-family-value via prop:cube-family-schubert-reduction): at a cluster with
\\ distinct roots and flow order j_p = 3, every coefficient at eps^(B(Lambda) + delta) with E+ + delta < 3 vanishes.
\\ Cluster: exact. A block with k0 = 1, N_b = 4 means the monic orthogonal P_2 has L(x^r P_2) = 0 for r <= 4, i.e.
\\ P_2(y_s) = c / P'(y_s) on the 6 roots, i.e. P_2 P' - (6z + b) P = c; for fixed P_2 = z^2 + al z + be and b this is
\\ linear in the coefficients of P and c. H_1, H_5 != 0 and distinct roots are checked, so k = 2 (p = 4) and k = 4
\\ (p = 2) have j = 3, and k = 3 (p = 3) has j = 4. Coefficients (60 digits, Fourier extraction): window u^(B+1),
\\ u^(B+2); top-up [-p, N-2] u {N} at u^(B+1); controls: the window's least coefficient (0 predicted) and the
\\ leader I(R) (nonzero predicted by thm:cube-ramification-equals-flow-order).
OUT = getenv("OUT");
emit(s) = print(s); if (OUT != 0 && OUT != "", write(OUT, s));
default(realprecision, 60);
lam = 3/2;
cc(n) = if (n < 0, 0, binomial(-lam, n));
vand(Y) = prod(i = 1, #Y, prod(j = i + 1, #Y, Y[j] - Y[i]));
hank(ps, k) = matdet(matrix(k + 1, k + 1, a, b, ps[a + b - 1]));
cluster(al, be, b0) = {
  my(P2 = 'z^2 + al * 'z + be, P = 'z^6 + 'q5 * 'z^5 + 'q4 * 'z^4 + 'q3 * 'z^3 + 'q2 * 'z^2 + 'q1 * 'z + 'q0);
  my(E = P2 * deriv(P, 'z) - (6 * 'z + b0) * P - 'cst, vars = ['q0, 'q1, 'q2, 'q3, 'q4, 'q5, 'cst]);
  my(A = matrix(7, 7), r = vector(7));
  for (d = 1, 7, my(e = polcoef(E, d - 1, 'z));
    for (j = 1, 7, A[d, j] = polcoef(e, 1, vars[j]));
    r[d] = -substvec(e, vars, vector(7)));
  my(x = matsolve(A, r~));
  'z^6 + sum(i = 1, 6, x[i] * 'z^(i - 1));
}
coef(Y, L, D) = {
  my(M = #Y, K = 2 * M * D + 1, s0 = 0);
  for (j = 0, K - 1, my(w = exp(2 * Pi * I * j / K), G = matrix(2 * M, 2 * M));
    for (s = 1, M, for (u = 1, 2 * M, my(t = L[u]);
      G[s, u] = if (t >= 0, cc(t) * Y[s]^t, 0);
      G[M + s, u] = sum(r = max(1, -t), D, cc(r) * cc(t + r) * w^r * Y[s]^(t + r))));
    s0 += matdet(G) * w^(-D));
  s0 / K;
}
{
  my(f = cluster(1/3, -2, 5/7), ps = polsym(f, 12), Y = polroots(f), M = 6, V = vand(Y)^2);
  emit(Str("cluster ", f));
  emit(Str("H_0..H_5 = ", vector(6, k, hank(ps, k - 1)), "; discriminant nonzero: ", poldisc(f) != 0));
  foreach([[4, 2, [3]], [2, 4, [1, 1, 1]], [3, 3, [2, 2]]], cs, my(p = cs[1], k = cs[2], R = cs[3], N = 2 * M - p, B = p^2 - p + M);
    my(W = vector(2 * M, i, -p - 1 + i), T = concat(vector(2 * M - 1, i, -p - 1 + i), [N]));
    my(lk = concat(vector(k - #R), Vecrev(R)), top = concat(vector(M, i, i - 1), vector(k, n, M + (n - 1) + lk[n])));
    my(LR = concat(vector(p, i, -p - 1 + i), top));
    emit(Str("p=", p, " k=", k, " rectangle R=", R, ":"));
    emit(Str("  window least |u^B| = ", Strprintf("%.3g", abs(coef(Y, W, B) / V)),
             "; window |u^(B+1)| = ", Strprintf("%.3g", abs(coef(Y, W, B + 1) / V)),
             "; window |u^(B+2)| = ", Strprintf("%.3g", abs(coef(Y, W, B + 2) / V))));
    emit(Str("  top-up least |u^B| = ", Strprintf("%.3g", abs(coef(Y, T, B) / V)), "; top-up |u^(B+1)| = ", Strprintf("%.3g", abs(coef(Y, T, B + 1) / V))));
    emit(Str("  leader I(R) least |u^B| = ", Strprintf("%.3g", abs(coef(Y, LR, B) / V)))));
  quit;
}
