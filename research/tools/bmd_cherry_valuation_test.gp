\\ Cherry-join valuation test (7 October 2026; cycle bmd-20261007-j).  Tested prediction (cost-chain reading of
\\ conj:cube-cherry-join-limits): for a fixed cluster D of M roots with nonzero Taylor minor, x = Q^a, e = Q^b with
\\ (M-k-1)/(k+1) < a/b < (M-k)/k, the Taylor minor (columns 0..R'-1, R' = binom(M+2,2)) of the joined cluster
\\ x*D u {1, 1+e} has Q-adic valuation a*X_k + b*E_k with X_k = binom(R_D,2) + M(M-1) + k(k+1), E_k = (M-k)^2 + k,
\\ R_D = binom(M,2); i.e. the vertices are the Minkowski sum of the chains x^(2i) and e^(2i-1).  Exact integers,
\\ Q = 1000003.  Also prints the minimum over all k (equal by construction when the prediction holds).
default(parisizemax, 2 * 10^9);
OUT = getenv("OUT");
emit(s) = print(s); if (OUT != 0 && OUT != "", write(OUT, s));
b(k) = binomial(-3/2, k);
H(X, Y, k) = sum(n = 0, k, b(n) * b(k - n) * X^n * Y^(k - n));
{
my(Q = 1000003, cases = [[4, [0, 2, -3, 7]], [6, [0, 2, -3, 7, 5, -11]]]);
foreach(cases, cs, my(M = cs[1], D = cs[2], RD = M * (M - 1) / 2, R = (M + 2) * (M + 1) / 2);
  for (k = 0, M - 1,
    my(lo = (M - k - 1) / (k + 1), hi = if (k == 0, M, (M - k) / k), r = (lo + hi) / 2, a = numerator(r), bb = denominator(r));
    my(x = Q^a, e = Q^bb, pts = concat(vector(M, i, x * D[i]), [1, 1 + e]), rows = List(), A, v, pred);
    for (i = 1, #pts, for (j = i + 1, #pts, listput(rows, vector(R, c, H(pts[i], pts[j], c - 1)))));
    A = matrix(R, R, i, j, rows[i][j]);
    v = valuation(matdet(A), Q);
    pred = vecmin(vector(M, kk, a * (RD * (RD - 1) / 2 + M * (M - 1) + (kk - 1) * kk) + bb * ((M - kk + 1)^2 + kk - 1)));
    emit(Str("M = ", M, ", regime k = ", k, ", a/b = ", a, "/", bb, ": valuation ", v, ", predicted ", a * (RD * (RD - 1) / 2 + M * (M - 1) + k * (k + 1)) + bb * ((M - k)^2 + k), " (min over vertices ", pred, ")"))));
}
