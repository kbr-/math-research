\\ Cherry over a caterpillar cluster with one double root (7 October 2026; cycle bmd-20261007-zt).
\\ Cross rows as in bmd_route_review2_tests.gp part B, generalized: roots beta_q (valuation a + v_q, leading coefficient
\\ ys_q), one of them doubled (rows V, d_beta V), eps of valuation b; block I rows V/dV, block E rows U_eps V/dV.
\\ Prediction tested: the naive Cauchy-Binet bound (cherry formula with the double root counted twice at equal inner
\\ valuation, minus val(beta_double) for each of the two confluent alternants)
\\   W'_j = 2 sum_q (M-q) v_q + a(2M^2 - 2Mj + j^2 - j) + b(j^2 - j + M) + 2 sum_(i<=k) (k+1-i) v_i - 2 (a + v_dbl)
\\ (M = total multiplicity, k = M - j, v sorted increasingly with repetition) against the exact valuation at every window
\\ [-j, 2M-1-j], 0 <= j <= M, and the least valuation over all 2M-subsets of [-M-2, 2M+1].
default(parisizemax, 2 * 10^9);
OUT = getenv("OUT");
emit(str) = print(str); if (OUT != 0 && OUT != "", write(OUT, str));
lam = 3/2;
cc(n) = if (n < 0, 0, binomial(-lam, n));
P = 1000003;
Wp(M, a, b, v, vd, j) = { my(k = M - j); 2 * sum(q = 1, M, (M - q) * v[q]) + a * (2*M^2 - 2*M*j + j^2 - j) + b * (j^2 - j + M) + 2 * sum(i = 1, k, (k + 1 - i) * v[i]) - 2 * (a + vd); }
\\ roots: list of [inner valuation, leading coefficient, doubled?]
build(roots, a, b, cols) = {
  my(R = 80, eps0 = -P^b / (1 + P^b), rowsI = List(), n = #cols);
  foreach(roots, r, my(bb = P^(a + r[1]) * r[2]);
    listput(rowsI, [t -> if (t >= 0, cc(t) * bb^t, 0)]);
    if (r[3], listput(rowsI, [t -> if (t >= 1, cc(t) * t * bb^(t - 1), 0)])));
  my(M = #rowsI, A = matrix(2 * M, n));
  for (q = 1, M, my(f = rowsI[q][1]); for (u = 1, n, my(t = cols[u]);
    A[q, u] = f(t);
    A[M + q, u] = sum(r = max(1, -t), R, cc(r) * eps0^r * f(t + r))));
  A;
}
{
foreach([
    [[[0, 3, 1], [2, -2, 0]], 1, 2], [[[0, 3, 1], [1, -2, 0], [3, 5, 0]], 1, 1], [[[0, 3, 0], [1, -2, 1], [3, 5, 0]], 1, 1],
    [[[0, 3, 0], [1, -2, 0], [2, 5, 1]], 1, 1], [[[0, 3, 1], [1, -2, 0], [3, 5, 0]], 1, 3], [[[0, 3, 0], [2, -2, 1], [3, 5, 0]], 2, 1]], c,
  my(roots = c[1], a = c[2], b = c[3], v = List(), vd = 0);
  foreach(roots, r, listput(v, r[1]); if (r[3], listput(v, r[1]); vd = r[1]));
  v = vecsort(Vec(v)); my(M = #v, out = List());
  for (j = 0, M, my(cols = [-j .. 2*M - 1 - j], D = matdet(build(roots, a, b, cols)));
    listput(out, [j, if (D == 0, oo, valuation(D, P)), Wp(M, a, b, v, vd, j)]));
  my(cols = [-M - 2 .. 2*M + 1], A = build(roots, a, b, cols), best = oo, arg = List());
  forsubset([#cols, 2 * M], S, my(D = matdet(vecextract(A, "..", Vec(S)))); if (D != 0, my(val = valuation(D, P));
    if (val < best, best = val; arg = List()); if (val == best, listput(arg, [cols[S[1]], cols[S[#S]]]))));
  emit(Str("roots ", roots, ", (a,b) = (", a, ",", b, "), v = ", v, ": windows [j, exact, W'_j] = ", Vec(out), "; least over sets ", best, " at ", Vec(arg))));
}
quit
