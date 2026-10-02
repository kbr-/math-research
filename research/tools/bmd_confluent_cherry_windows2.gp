\\ Confluent cherry windows, second expansion (7 October 2026; cycle bmd-20261007-za).  Rows V_q (block I), w^(-1) V_q
\\ (block S: column n-1) and E'_q = ((1+eps/w)^(-3/2) - 1 - c_1 eps/w) V_q (block E': Toeplitz of c_r eps^r, r >= 2), which
\\ span the cross block of the confluent cherry (E' = E - c_1 eps S).  For a caterpillar each Cauchy-Binet term over
\\ (N1, N2, N3) has the exact valuation f(N1) + f(N2) + f(N3) + w (Sum N3 - Sum Lambda3), f(N) = sum_i n_(i) b_(M+1-i),
\\ with columns N1 (I), N2 - 1 (S), Lambda3 = the rest (E'), and N3 least with n_a >= max(t_a + 2, a - 1).
\\ Prediction tested: at each window [-j, 3M-1-j], 2 <= j <= M+1, the least term valuation F'_j equals the exact
\\ valuation (computed in bmd_confluent_cherry_windows.gp, research/results/bmd-20261007-za/confluent-cherry-windows.txt,
\\ and recomputed here).  Prints [j, actual, F'_j, number of minimizing (N1, N2)].
default(parisizemax, 2 * 10^9);
OUT = getenv("OUT");
emit(str) = print(str); if (OUT != 0 && OUT != "", write(OUT, str));
lam = 3/2;
cc(n) = if (n < 0, 0, binomial(-lam, n));
CS = [1, 3, -2, 5];
P = 1000003;
fval(N, M, bq) = my(Ns = vecsort(N)); sum(i = 1, M, Ns[i] * bq[M + 1 - i]);
Fpred(M, a, w, vv, j) = {
  my(Lam = [-j .. 3*M - 1 - j], bq = vector(M, q, a + vv[q]), best = oo, cnt = 0);
  my(pos = select(t -> t >= 0, Lam));
  forsubset([#pos, M], S1, my(c1 = vecextract(pos, Vec(S1)), rest = select(t -> t >= -1 && !setsearch(Set(c1), t), Lam));
    forsubset([#rest, M], S2, my(c2 = vecextract(rest, Vec(S2)), L3 = vecsort(setminus(setminus(Set(Lam), Set(c1)), Set(c2))));
      my(N3 = vector(M));
      for (i = 1, M, N3[i] = max(L3[i] + 2, i - 1); if (i > 1, N3[i] = max(N3[i], N3[i - 1] + 1)));
      my(T = fval(c1, M, bq) + fval(apply(t -> t + 1, c2), M, bq) + fval(N3, M, bq) + w * (vecsum(N3) - vecsum(L3)));
      if (T < best, best = T; cnt = 0); if (T == best, cnt++)));
  [best, cnt];
}
actual(M, a, b, vv, j, NS) = {
  my(R = NS \ (a + b) + 1, cols = [-j .. 3*M - 1 - j], n = #cols, rows = matrix(3*M, n));
  my(eps0 = -P^b / (1 + P^b), bet = vector(M, q, my(y = CS[q] * P^vv[q]); P^a * y / (1 - P^a * y)));
  for (q = 1, M, for (u = 1, n, my(t = cols[u]);
    rows[q, u] = if (t >= 0, cc(t) * bet[q]^t, 0);
    rows[M + q, u] = if (t >= -1, cc(t + 1) * bet[q]^(t + 1), 0);
    rows[2*M + q, u] = sum(r = max(2, -t), R, cc(r) * cc(t + r) * eps0^r * bet[q]^(t + r))));
  my(D = matdet(rows)); if (D == 0, oo, valuation(D, P));
}
{
foreach([[2, 1, 1, [0, 2]], [2, 2, 1, [0, 3]], [2, 1, 3, [0, 1]], [3, 1, 1, [0, 1, 2]], [3, 1, 3, [0, 1, 2]], [3, 3, 1, [0, 1, 2]],
         [3, 1, 2, [0, 2, 3]], [4, 1, 1, [0, 1, 2, 3]], [4, 2, 1, [0, 1, 3, 4]]], c,
  my(M = c[1], a = c[2], b = c[3], vv = c[4], NS = (a + b) * (3*M^2 + 3*M) + 6 * M * vecsum(vv) + 10, out = List());
  for (j = 2, M + 1, my(F = Fpred(M, a, b, vv, j), A = actual(M, a, b, vv, j, NS)); listput(out, [j, A, F[1], F[2]]));
  emit(Str("M = ", M, ", (a,b) = (", a, ",", b, "), v = ", vv, ": [j, actual, least term, #minimizers] = ", Vec(out))));
}
