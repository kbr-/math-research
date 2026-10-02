\\ Route review tests (7 October 2026; cycle bmd-20261007-zb).  Exact P-adic valuations, P = 1000003, rational entries.
\\ A (falsification of conj:cube-confluent-cherry-windows / -expansion): confluent cherry over the caterpillar
\\   y = (1, -s, s^2) (special signs), M = 3, rates (1,2) and (2,3): least valuation and its 9-sets on [-5,9].
\\ B (lead: a cherry step over a base with a double root): cherry {1, 1+e} over the cluster {double root beta_1,
\\   simple beta_2}; cross rows (U_c)(V_1, d_beta V_1, V_2), d_beta V = -lambda w (1+beta w)^(-lambda-1); prediction:
\\   leading sets are windows [-j, 5-j], j = 1..3 (as for a cluster of 3 simple roots).  Arcs with beta_1 ~ x and
\\   beta_2 ~ x s^v, and the reverse (double root deeper).
\\ C (confluent tie window at the zeros of H_m): rank of W^c(c) over Q[c]/(H_m), H_m the non-monomial factor of the
\\   pure block determinant (conj:cube-two-point-window-factorization), m = 2, 3, 4.  Full rank 3m+3 means the extra
\\   rows supply full rank exactly where the pure block is singular.
default(parisizemax, 2 * 10^9);
OUT = getenv("OUT");
emit(str) = print(str); if (OUT != 0 && OUT != "", write(OUT, str));
lam = 3/2;
cc(n) = if (n < 0, 0, binomial(-lam, n));
P = 1000003;
\\ least valuation over all k-subsets of the columns of a rational matrix
leastsets(rows, cols) = {
  my(k = #rows[, 1], n = #cols, best = oo, arg = List(), edge = oo);
  forsubset([n, k], S, my(D = matdet(vecextract(rows, "..", Vec(S))));
    if (D != 0, my(v = valuation(D, P)); if (S[1] == 1 || S[#S] == n, edge = min(edge, v));
      if (v < best, best = v; arg = List()); if (v == best, listput(arg, apply(u -> cols[u], Vec(S))))));
  [best, Vec(arg), edge];
}
eserie(t, R, eps0, b) = sum(r = max(1, -t), R, cc(r) * cc(t + r) * eps0^r * b^(t + r));
{
\\ Part A
foreach([[1, 2], [2, 3]], ab, my(a = ab[1], b = ab[2], M = 3, cols = [-5 .. 9], n = #cols, R = 60, rows = matrix(3*M, n));
  my(eps0 = -P^b / (1 + P^b), ys = [1, -P, P^2], bet = vector(M, q, P^a * ys[q] / (1 - P^a * ys[q])));
  for (q = 1, M, for (u = 1, n, my(t = cols[u]);
    rows[q, u] = if (t >= 0, cc(t) * bet[q]^t, 0);
    rows[M + q, u] = if (t >= -1, cc(t + 1) * bet[q]^(t + 1), 0);
    rows[2*M + q, u] = eserie(t, R, eps0, bet[q])));
  my(L = leastsets(rows, cols));
  emit(Str("A: confluent cherry, M = 3, y = (1,-s,s^2), (a,b) = ", ab, ": least ", L[1], " at ", L[2], "; edge ", L[3])));
\\ Part B
foreach([[1, 1, 2, 0], [1, 2, 1, 0], [2, 1, 1, 0], [1, 1, 2, 1], [1, 2, 1, 1]], c,
  my(a = c[1], b = c[2], v = c[3], rev = c[4], cols = [-5 .. 8], n = #cols, R = 60, rows = matrix(6, n));
  my(eps0 = -P^b / (1 + P^b), b1 = if (rev, P^(a + v), P^a) * 3, b2 = if (rev, P^a, P^(a + v)) * (-2));
  my(Vco(bb, t) = if (t >= 0, cc(t) * bb^t, 0), dVco(bb, t) = if (t >= 1, cc(t) * t * bb^(t - 1), 0));
  my(rowI = [t -> Vco(b1, t), t -> dVco(b1, t), t -> Vco(b2, t)]);
  for (u = 1, n, my(t = cols[u]);
    for (z = 1, 3, rows[z, u] = rowI[z](t));
    rows[4, u] = sum(r = max(1, -t), R, cc(r) * eps0^r * Vco(b1, t + r));
    rows[5, u] = sum(r = max(1, -t), R, cc(r) * eps0^r * dVco(b1, t + r));
    rows[6, u] = sum(r = max(1, -t), R, cc(r) * eps0^r * Vco(b2, t + r)));
  my(L = leastsets(rows, cols));
  emit(Str("B: cherry over {double beta_1, simple beta_2}, (a,b) = (", a, ",", b, "), inner gap ", v, if (rev, ", double root deeper", ", simple root deeper"),
    ": least ", L[1], " at ", L[2], "; edge ", L[3])));
}
\\ Part C
bn(x, k) = if (k < 0, 0, binomial(x, k));
rowco(r, m, k) = {
  if (r <= 2 * m, return(bn(-5/2, k - (r - 1))));
  if (r <= 3 * m, my(nn = r - 2 * m - 1); return(bn(-3/2, k - nn) * 'c^max(k - nn, 0)));
  if (r == 3 * m + 1, return(bn(-3, k)));
  if (r == 3 * m + 2, return(sum(aa = 0, k, bn(-3/2, aa) * bn(-3/2, k - aa) * 'c^(k - aa))));
  sum(aa = 0, k - 1, bn(-5/2, aa) * bn(-3/2, k - 1 - aa) * 'c^(k - 1 - aa));
}
{
foreach([2, 3, 4], m,
  my(d = m * (m - 1) / 2, W = matrix(3*m + 3, 3*m + 5, r, j, rowco(r, m, d + j - 1)));
  my(pure = matdet(matrix(3*m, 3*m, r, j, W[r, j])), F = factor(pure), H = 0);
  for (z = 1, #F[, 1], if (poldegree(F[z, 1], 'c) >= 2, H = F[z, 1]));
  my(Wm = matrix(3*m + 3, 3*m + 5, r, j, Mod(W[r, j], H)));
  emit(Str("C: m = ", m, ", H_m of degree ", poldegree(H, 'c), ": rank of the confluent tie window over Q[c]/(H_m) = ", matrank(Wm), " of ", 3*m + 3)));
}
