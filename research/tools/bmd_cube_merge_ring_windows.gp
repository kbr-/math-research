\\ Ring windows of a single merge (1 October 2026; cycle bmd-20261001-w).
\\ Model: near p_0, with s = z - p_0, after the common factor s^(3/2 - n) the half-integral class of
\\ V(n; p_0; p_1..p_k), p_1 = p_0 + eps, is U + tau W with
\\   U = sum_j Pol_(<n)(s) g_j,  W = s^(n-1) <g_j>  (a subspace of U),  g_j = (1 + beta_j s)^(1/2),
\\   tau = (1 - eps/s)^(1/2),  j = 1..K, K = k - 1,  M = nK, L = M + K.
\\ Claims tested (the entry proves them from two nonvanishing conditions, checked here):
\\   f(c) = val_eps det C[:, W_c] = nK + c(c-1) for 0 <= c <= K, W_c = {-c..-1} + {0..L-c-1};
\\   the window condition: R_a = sU + G_(>=a) has exponents 1..L-a at 0 (equivalently D_a != 0), 1 <= a <= K,
\\   where G_(>=a) = {g in <g_j> : ord_0 g >= a}.
\\ Cases: n >= 1, K >= 2, n + K <= 12 (every merge of the peeling chain for N <= 13 roots, n + K = N - 1).
\\ Arithmetic modulo q = 2^61 - 1 at beta_j = (2, -3, 5, -7, 11, -13, 17, 19, -23, 29, -31)[j] / 3: a nonzero value mod q
\\ at one beta proves generic nonvanishing over Q; valuations mod q are upper bounds for the generic ones
\\ (a lower bound is proved in the entry).  eps-series truncated at eps^mmax; valuations <= mmax are exact.
OUT = getenv("OUT");
emit(s) = print(s); if (OUT != 0 && OUT != "", write(OUT, s));
q = 2^61 - 1;
ring(n, K) = {
  my(M = n * K, L = M + K, Y = L + 4, mmax = n * K + K * (K - 1) + 4);
  my(bet = vector(K, j, Mod([2, -3, 5, -7, 11, -13, 17, 19, -23, 29, -31][j], q) / 3));
  my(g = vector(K, j, vector(Y, r, Mod(binomial(1/2, r - 1), q) * bet[j]^(r - 1))));
  \\ U rows s^i g_j, columns 0..Y-1, reduced to identity on columns 0..M-1
  my(A = matrix(M, Y, a, b, 0), row = 0);
  for (j = 1, K, for (i = 0, n - 1, row++; for (r = 1, Y - i, A[row, r + i] = g[j][r])));
  my(A0 = A[, 1..M]);
  if (matrank(A0) < M, error("U not ordinary at 0"));
  my(G = A0^(-1) * A);
  \\ f rows (tau - 1) s^(n-1) g_j, columns -K..Y-1 at index col + K + 1
  my(W = Y + K, F = matrix(K, W, a, b, 0));
  for (j = 1, K, for (m = 1, mmax, my(cm = Mod((-1)^m * binomial(1/2, m), q));
    for (r = 1, Y, my(col = r - 1 + n - 1 - m);
      if (col >= -K && col <= Y - 1, F[j, col + K + 1] += cm * 'x^m * g[j][r]))));
  for (i = 1, K, for (d = 0, M - 1, my(v = F[i, d + K + 1]);
    if (v != 0, for (r = 1, Y, if (G[d + 1, r] != 0, F[i, r + K] -= v * G[d + 1, r])))));
  my(fv = vector(K + 1), ok = 1);
  for (c = 0, K,
    my(cols = concat(vector(c, t, K + 1 - t), vector(K - c, t, K + 1 + M + t - 1)));
    my(d = matdet(matrix(K, K, i, t, F[i, cols[t]])));
    fv[c + 1] = if (d == 0, -1, valuation(lift(d), 'x));
    if (fv[c + 1] != n * K + c * (c - 1) || fv[c + 1] > mmax, ok = 0));
  \\ window condition: R_a = s U + G_(>=a), rank on columns 1..L-a
  my(wc = vector(K));
  for (a = 1, K,
    my(Gm = matrix(K, a, j, r, g[j][r]), ker = matker(Gm~));  \\ combinations with ord >= a
    my(rows = List());
    for (j = 1, K, for (i = 1, n, listput(rows, vector(L - a, t, if (t - i + 1 >= 1, g[j][t - i + 1], 0)))));
    for (u = 1, #ker, listput(rows, vector(L - a, t, sum(j = 1, K, ker[j, u] * g[j][t + 1]))));
    my(R = matrix(#rows, L - a, i, t, rows[i][t]));
    wc[a] = (matrank(R) == L - a) && (#rows == L - a));
  emit(Str("n=", n, " K=", K, " L=", L, " f(c), c=0..K: ", fv, " formula nK+c(c-1): ", if (ok, "yes", "NO"),
    "; window condition a=1..K: ", wc));
  ok && vecmin(wc) == 1;
}
main() = {
  my(allok = 1);
  \\ every merge of the peeling chain up to N = 13 roots: n + K = N - 1 <= 12
  for (n = 1, 11, for (K = 2, 12 - n, if (!ring(n, K), allok = 0)));
  emit(Str("all cases pass: ", allok));
}
main();
