\\ Confluent cherry windows: Cauchy-Binet prediction against exact valuations (7 October 2026; cycle bmd-20261007-za).
\\ Cross block (up to w^(-lambda)): the doubled rows w^(-1) psi_q, w^(-1) d_beta psi_q, psi = (1+beta w)^(-1/2), and the
\\ E rows ((1+eps/w)^(-3/2) - 1)(1+beta_q w)^(-3/2).  For a caterpillar (val beta_q = a + v_q, v strictly increasing)
\\ each Cauchy-Binet term over (N12, N3) has the exact valuation
\\   T = sum_q b_q (s_q - 1) + sum_q b_q n3_(M+1-q) + w (Sum N3 - Sum Lambda3),
\\ s_q = sum of the q-th pair of exponents of N12 from the top, Lambda3 = Lambda \ (N12 - 1), N3 least admissible.
\\ Prediction tested: at each window Lambda'_j = [-j, 3M-1-j], 2 <= j <= M+1, the exact valuation equals the least term
\\ valuation F_j (minimum over the complement C of N12 - 1 in [-1, 3M-1-j]), and the number of minimizing C is printed.
\\ Exact valuations: arc parameter specialized to P = 1000003, rational entries, eps-series truncated (exact below the
\\ printed threshold).
default(parisizemax, 2 * 10^9);
OUT = getenv("OUT");
emit(str) = print(str); if (OUT != 0 && OUT != "", write(OUT, str));
lam = 3/2; mu = 1/2;
cc(n) = if (n < 0, 0, binomial(-lam, n));
dd(n) = if (n < 0, 0, binomial(-mu, n));
CS = [1, 3, -2, 5];
P = 1000003;
Fpred(M, a, w, vv, j) = {
  my(K = 3*M - j, Lam = [-j .. K - 1], best = oo, cnt = 0, bq = vector(M, q, a + vv[q]));
  \\ choose the 2M columns of the doubled rows among [-1, K-1]
  forsubset([K + 1, 2*M], S, my(cols12 = apply(u -> u - 2, Vec(S)), N12 = apply(t -> t + 1, cols12));
    my(L3 = vecsort(setminus(Set(Lam), Set(cols12))), N3 = vector(M));
    for (i = 1, M, N3[i] = max(L3[i] + 1, i - 1); if (i > 1, N3[i] = max(N3[i], N3[i - 1] + 1)));
    my(N12s = vecsort(N12), T = 0);
    for (q = 1, M, my(hi = N12s[2*(M + 1 - q)], lo = N12s[2*(M + 1 - q) - 1]); T += bq[q] * (hi + lo - 1) + bq[q] * N3[M + 1 - q]);
    T += w * (vecsum(N3) - vecsum(L3));
    if (T < best, best = T; cnt = 0); if (T == best, cnt++));
  [best, cnt];
}
actual(M, a, b, vv, j, NS) = {
  my(R = NS \ (a + b) + 1, cols = [-j .. 3*M - 1 - j], n = #cols, rows = matrix(3*M, n));
  my(eps0 = -P^b / (1 + P^b), bet = vector(M, q, my(y = CS[q] * P^vv[q]); P^a * y / (1 - P^a * y)));
  for (q = 1, M, for (u = 1, n, my(t = cols[u]);
    rows[q, u] = if (t >= -1, dd(t + 1) * bet[q]^(t + 1), 0);
    rows[M + q, u] = if (t >= -1, (t + 1) * dd(t + 1) * bet[q]^t, 0);
    rows[2*M + q, u] = sum(r = max(1, -t), R, cc(r) * cc(t + r) * eps0^r * bet[q]^(t + r))));
  my(D = matdet(rows)); if (D == 0, oo, valuation(D, P));
}
{
foreach([[2, 1, 1, [0, 2]], [2, 2, 1, [0, 3]], [2, 1, 3, [0, 1]], [3, 1, 1, [0, 1, 2]], [3, 1, 3, [0, 1, 2]], [3, 3, 1, [0, 1, 2]],
         [3, 1, 2, [0, 2, 3]], [4, 1, 1, [0, 1, 2, 3]], [4, 2, 1, [0, 1, 3, 4]]], c,
  my(M = c[1], a = c[2], b = c[3], vv = c[4], NS = (a + b) * (3*M^2 + 3*M) + 6 * M * vecsum(vv) + 10, out = List());
  for (j = 2, M + 1, my(F = Fpred(M, a, b, vv, j), A = actual(M, a, b, vv, j, NS)); listput(out, [j, A, F[1], F[2]]));
  emit(Str("M = ", M, ", (a,b) = (", a, ",", b, "), v = ", vv, ": [j, actual, least term, #minimizers] = ", Vec(out),
    "; exact below ", (NS \ (a + b) + 2) * (a + b) - (M + 1) * a)));
}
