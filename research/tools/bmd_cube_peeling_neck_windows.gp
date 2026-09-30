\\ Neck windows of the peeling degeneration of the base (30 September 2026; cycle bmd-20260930-zc).
\\ Model: in y = 1/z the half-integral class of E_(k-1) at D_k = eps c, near the neck, is U + tau W with
\\   U = sum_s Pol_(<n)(y) phi_s, W = y^(n-4) sum_s Pol_(<4)(y) phi_s (a subspace of U),
\\   phi_s = (1 + beta_s y)^(-7/2), tau = (1 + eps c / y)^(-5/2), n = 4e, s = 1..l, e = k-1, l = b-k.
\\ With M = nl, K = 4l, L = M + K, the entry proves the neck has 16 k l (l-1) points; its exponent lists
\\ at the two ends are the windows W_c = {-c..-1} + {0..M-1} + {M..M+K-c-1} for c = 4 (near) and c = K (far).
\\ Question: the valuations f(c) = val_eps det C[:, W_c] for 4 <= c <= K, where C has rows g_d (the triangular
\\ basis of U at 0, identity on the middle columns) and f_i = (tau - 1) h_i (h_i a basis of W), after
\\ clearing middle columns.  The breakpoints alpha_c = (f(c+1) - f(c)) / L (y ~ eps^alpha) give the neck's
\\ Newton polygon if the windows are its vertices; also printed: the naive assignment bound E(c).
\\ Exactness: tau is truncated at eps^mmax; a determinant with valuation <= mmax is exact (reported).
\\ Arithmetic modulo q = 2^61 - 1, beta_s = (2, -3, 5, -7, 11)[s] / 3, c = 1.
OUT = getenv("OUT");
emit(s) = print(s); if (OUT != 0 && OUT != "", write(OUT, s));
q = 2^61 - 1;
naiveE(l, cc) = {
  my(rows = vecsort(concat(vector(4, r, vector(l, s, r - 1)))), top = rows[#rows - cc + 1..#rows]);
  sum(i = 1, cc, max(0, i - top[i] - 1));
}
neck(e, l, mmax) = {
  my(n = 4 * e, M = n * l, K = 4 * l, Y = M + K + mmax + 8, lam = -7/2);
  my(bet = vector(l, s, Mod([2, -3, 5, -7, 11][s], q) / 3));
  my(phi = vector(l, s, vector(Y, r, Mod(binomial(lam, r - 1), q) * bet[s]^(r - 1))));
  \\ U rows y^i phi_s, columns 0..Y-1; reduce to identity on columns 0..M-1
  my(A = matrix(M, Y, a, b, 0), row = 0);
  for (s = 1, l, for (i = 0, n - 1, row++; for (r = 1, Y - i, A[row, r + i] = phi[s][r])));
  my(A0 = A[, 1..M]);
  if (matrank(A0) < M, error("U not ordinary at 0"));
  my(G = A0^(-1) * A);  \\ rows g_d: identity on columns 0..M-1
  \\ f rows: (tau - 1) y^(n-4+p) phi_s; columns -mmax..Y-1 stored at index col + mmax + 1
  my(t = vector(mmax, m, Mod(binomial(-5/2, m), q)), W = Y + mmax, F = matrix(K, W, a, b, 0), fr = 0);
  for (s = 1, l, for (p = 0, 3, fr++;
    my(h = vector(Y, r, if (r - 1 >= n - 4 + p, phi[s][r - (n - 4 + p)], 0)));
    for (m = 1, mmax, for (r = 1, Y, if (h[r] != 0, my(col = r - 1 - m);
      F[fr, col + mmax + 1] += t[m] * 'x^m * h[r])))));
  \\ clear middle columns 0..M-1 with the g rows
  for (i = 1, K, for (d = 0, M - 1, my(v = F[i, d + mmax + 1]);
    if (v != 0, for (r = 1, Y, if (G[d + 1, r] != 0, F[i, r + mmax] -= v * G[d + 1, r])))));
  my(res = vector(K - 3));
  for (cc = 4, K,
    my(cols = concat(vector(cc, j, -j + mmax + 1), vector(K - cc, j, M + j - 1 + mmax + 1)));
    my(Z = matrix(K, K, a, b, F[a, cols[b]]), dt = matdet(Z));
    my(v = if (dt == 0, oo, valuation(lift(dt), 'x)));
    res[cc - 3] = v;
    emit(Str("e=", e, " l=", l, " M=", M, " K=", K, " L=", M + K, " window c=", cc, ": val ", v,
      if (v != oo && v <= mmax, " (exact)", " (NOT EXACT)"), ", naive bound E(c)+16l = ", naiveE(l, cc) + 16 * l)));
  my(df = vector(K - 4, j, res[j + 1] - res[j]));
  emit(Str("  differences f(c+1)-f(c), c = 4..K-1: ", df, "; breakpoints alpha = diff / L: ", df / (M + K),
    "; convex: ", if (#df <= 1 || vecmin(vector(#df - 1, j, df[j + 1] - df[j])) > 0, "strictly", "NO")));
}
main() = {
  my(cases = if (getenv("CASES"), eval(getenv("CASES")), [[1, 2]]), mm = if (getenv("MMAX"), eval(getenv("MMAX")), 80));
  foreach (cases, cs, neck(cs[1], cs[2], mm));
}
default(parisizemax, 4000000000);
main();
