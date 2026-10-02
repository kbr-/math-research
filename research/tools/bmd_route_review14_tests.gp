\\ Route review test (8 October 2026; cycle bmd-20261008-zu), lambda = 3/2, M = 5. Copy of bmd_cross_three_deep.gp
\\ at a non-caterpillar point: beta = (2, 1, 3 eta, 3 eta + 5 eta^2, 7 eta^3), a tie over a cherry of two roots at
\\ scale eta (difference of order eta^2) and one root at eta^3. Root valuations sorted nu = (1, 1, 3); 2 val Vand = 8.
\\ Thresholds are the two-alternant bound (thm:cube-two-alternant-penalty-bound): 2 val Vand + sum_a 2 (4 - p - a)_+ nu_a,
\\ so p = 0: 24, p = 1: 14, p = 2: 10, p >= 3: 8. Question: does the window Lambda_p still attain the least value of
\\ its class p, as at caterpillar points, and does the bound stay sharp when two deep roots form a cherry?
default(parisizemax, 6 * 10^9);
OUT = getenv("OUT");
emit(s) = print(s); if (OUT != 0 && OUT != "", write(OUT, s));
cc(n) = binomial(-3/2, n);
NE = 2; M = 5; T0 = -2; T1 = 10;
\\ Third version prints the largest least eps-order: Q entries are cut at m <= max(1,-t) + 10, so omitted terms have
\\ eps-order >= 12 and affect determinant coefficients only from order 16 on.
\\ Second version: a first run with symbolic eta (bivariate 10 x 10 determinants) was stopped after 30 minutes.  Here
\\ eta = q = 1000003 numerically, and the eta-valuation is read as the q-adic valuation of each eps-coefficient
\\ (all denominators are powers of 2, so val_q >= the eta-order, with equality unless a leading integer is divisible by q).
QQQ = 1000003;
BS = [2, 1, 3 * QQQ, 3 * QQQ + 5 * QQQ^2, 7 * QQQ^3];
TH = [24, 14, 10, 8, 8, 8];   \\ threshold for p = 0..5
{
  my(nc = T1 - T0 + 1, P = matrix(2 * M, nc), lo = vector(6, i, oo), bad = vector(6), cnt = vector(6), wins = vector(6, i, oo), l0max = vector(6, i, -oo));
  for (s = 1, M, for (j = 1, nc, my(t = T0 + j - 1);
    if (t >= 0, P[s, j] = cc(t) * BS[s]^t);
    P[M + s, j] = sum(m = max(1, -t), max(1, -t) + M + NE + 3, cc(m) * 'ep^m * cc(t + m) * BS[s]^(t + m))));
  forsubset([nc, 2 * M], S,
    my(L = apply(j -> T0 + j - 1, Vec(S)), p = #select(t -> t < 0, L), D = matdet(vecextract(P, "..", Vec(S))));
    if (D != 0, cnt[p + 1]++; my(l0 = valuation(D, 'ep), v = oo); l0max[p + 1] = max(l0max[p + 1], l0);
      for (n = l0, l0 + NE, my(cf = polcoef(D, n, 'ep)); if (cf != 0, v = min(v, valuation(cf, QQQ))));
      lo[p + 1] = min(lo[p + 1], v); if (v < TH[p + 1], bad[p + 1]++);
      if (L == [-p .. 2 * M - 1 - p], wins[p + 1] = v)));
  for (p = 0, 5, if (cnt[p + 1], emit(Str("p = ", p, ": ", cnt[p + 1], " nonzero sets; least eta-valuation ", lo[p + 1],
    " (threshold ", TH[p + 1], "); below threshold: ", bad[p + 1], "; window Lambda_", p, ": ", wins[p + 1], "; largest least eps-order ", l0max[p + 1], " (truncation exact for orders <= 15)"))));
}
quit
