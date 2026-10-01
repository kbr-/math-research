\\ Neck windows of the odd peeling degeneration (3 October 2026; cycle bmd-20261003-y).
\\ Model (derived in the entry): in y = 1/z the class of E_(k-1) with sign - around the cluster, at D_k = eps c, is U + tau W,
\\   U = sum_s Pol_(<n) phi_s  +  y^(2e-2) Pol_(<2e) phi_a,     W = y^(n-4) ( sum_s Pol_(<4) phi_s  +  Pol_(<2) phi_a ),
\\   phi_s = (1 + beta_s y)^(-7/2) (s = 1..l doubles), phi_a = (1 + beta_a y)^(-3/2) (the simple root), tau = (1 + eps c/y)^(-5/2),
\\   n = 4e, e = k-1, l = b-k (odd N = 2b+1).  M = dim U = 4el + 2e, K = dim W = 4l + 2, L = M + K.
\\ The odd peeling theorem gives a neck of 4k(4l^2-1) points; its end lists are the windows
\\   W_c = {-c..-1} + {0..M-1} + {M..M+K-c-1} at c = 4 (near) and c = K (far), so 4l-2 rings of L points are predicted.
\\ Output: f(c) = val_eps det C[:, W_c] for 4 <= c <= K, differences, breakpoints alpha_c = diff / L, convexity, and the
\\ prediction P(c) = c^2 + min { sum n_s^2 : n_s <= w_s, sum n_s = K - c } over the species other than one double
\\ (caps 4 for the other l-1 doubles, 2 for the simple root), reported as f(c) - P(c) (constant if it holds).
\\ Refined prediction Q(c) = (16l+4)(e-1) + c^2 + min over n_a in {0,1,2} of [ n_a^2 + (2e-2)(2-n_a) + min sum n_d^2 ]
\\ (the doubles other than the polar one capped at 4, sum n_d = K - c - n_a), reported as f(c) - Q(c) (0 if it holds).
\\ Exactness: tau truncated at eps^mmax; a valuation <= mmax is exact.  Arithmetic modulo q = 2^61 - 1.
OUT = getenv("OUT");
emit(s) = print(s); if (OUT != 0 && OUT != "", write(OUT, s));
q = 2^61 - 1;
minsq(caps, T) = {
  \\ minimum of sum n_i^2 with 0 <= n_i <= caps[i], sum n_i = T (greedy water-filling, exact by convexity)
  my(n = vector(#caps), left = T);
  while (left > 0, my(best = 0); for (i = 1, #caps, if (n[i] < caps[i] && (best == 0 || n[i] < n[best]), best = i));
    if (best == 0, return(oo)); n[best]++; left--);
  sum(i = 1, #n, n[i]^2);
}
neck(e, l, mmax) = {
  my(n = 4 * e, M = n * l + 2 * e, K = 4 * l + 2, Y = M + K + mmax + 8);
  my(bet = vector(l + 1, s, Mod([2, -3, 5, -7, 11, 13][s], q) / 3));
  my(ex = concat(vector(l, s, -7/2), [-3/2]));
  my(phi = vector(l + 1, s, vector(Y, r, Mod(binomial(ex[s], r - 1), q) * bet[s]^(r - 1))));
  \\ U rows y^(off + i) phi_s
  my(A = matrix(M, Y, a, b, 0), row = 0, blocks = concat(vector(l, s, [s, 0, n]), [[l + 1, 2 * e - 2, 2 * e]]));
  foreach (blocks, bl, for (i = 0, bl[3] - 1, row++; for (r = 1, Y - bl[2] - i, A[row, r + bl[2] + i] = phi[bl[1]][r])));
  my(A0 = A[, 1..M]);
  if (matrank(A0) < M, error("U not ordinary at 0"));
  my(G = A0^(-1) * A);
  my(t = vector(mmax, m, Mod(binomial(-5/2, m), q)), W = Y + mmax, F = matrix(K, W, a, b, 0), fr = 0);
  my(wb = concat(vector(l, s, [s, 4]), [[l + 1, 2]]));
  foreach (wb, bl, for (p = 0, bl[2] - 1, fr++;
    my(h = vector(Y, r, if (r - 1 >= n - 4 + p, phi[bl[1]][r - (n - 4 + p)], 0)));
    for (m = 1, mmax, for (r = 1, Y, if (h[r] != 0, my(col = r - 1 - m);
      F[fr, col + mmax + 1] += t[m] * 'x^m * h[r])))));
  for (i = 1, K, for (d = 0, M - 1, my(v = F[i, d + mmax + 1]);
    if (v != 0, for (r = 1, Y, if (G[d + 1, r] != 0, F[i, r + mmax] -= v * G[d + 1, r])))));
  my(res = vector(K - 3), caps = concat(vector(l - 1, s, 4), [2]), dev = vector(K - 3));
  for (cc = 4, K,
    my(cols = concat(vector(cc, j, -j + mmax + 1), vector(K - cc, j, M + j - 1 + mmax + 1)));
    my(Z = matrix(K, K, a, b, F[a, cols[b]]), dt = matdet(Z));
    my(v = if (dt == 0, oo, valuation(lift(dt), 'x)));
    res[cc - 3] = v; dev[cc - 3] = if (v == oo, oo, v - cc^2 - minsq(caps, K - cc));
    my(Qc = oo); for (na = 0, 2, if (K - cc - na >= 0, my(ms = minsq(vector(l - 1, s, 4), K - cc - na)); if (ms != oo, Qc = min(Qc, na^2 + (2 * e - 2) * (2 - na) + ms))));
    Qc += (16 * l + 4) * (e - 1) + cc^2;
    emit(Str("e=", e, " l=", l, " M=", M, " K=", K, " L=", M + K, " window c=", cc, ": val ", v,
      if (v != oo && v <= mmax, " (exact)", " (NOT EXACT)"), ", f - P = ", dev[cc - 3], ", f - Q = ", if (v == oo, oo, v - Qc))));
  my(df = vector(K - 4, j, res[j + 1] - res[j]));
  emit(Str("  differences c = 4..K-1: ", df, "; alpha = diff / L: ", df / (M + K),
    "; all in (0,1): ", vecmin(df) > 0 && vecmax(df) < M + K,
    "; convex: ", if (#df <= 1 || vecmin(vector(#df - 1, j, df[j + 1] - df[j])) > 0, "strictly", "NO")));
}
main() = {
  my(cases = if (getenv("CASES"), eval(getenv("CASES")), [[1, 1], [2, 1], [1, 2], [2, 2], [1, 3]]), mm = if (getenv("MMAX"), eval(getenv("MMAX")), 120));
  foreach (cases, cs, neck(cs[1], cs[2], mm));
}
default(parisizemax, 4000000000);
main();
