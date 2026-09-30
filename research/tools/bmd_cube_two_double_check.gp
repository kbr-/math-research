\\ Cross-check of the (2,2) two-cluster flat limit (30 September 2026; cycle bmd-20260930-zv), independent of the
\\ valuation-reduction scripts.  At the shapes of bmd_cube_two_cluster_limit.gp seed 0 (b = (-3/7, 5/7), c = (2/5, -1))
\\ and at a second choice (b = (1/3, -2), c = (3/4, 5/2)), it expands the four products exactly to order eps^10 and, for
\\ t = 0..6, computes the space S_t of eps^t-coefficients of combinations sum_i q_i(eps) P_i (deg q_i <= t) whose
\\ coefficients of orders < t vanish identically.  The flat limit is the union of the S_t; the script prints dim S_t and,
\\ for S_4, the dimensions of its subspaces with pole order <= (x,y) at (0,1), x,y <= 2.
OUT = getenv("OUT");
emit(s) = print(s); if (OUT != 0 && OUT != "", write(OUT, s));
K = 10;
P(bj, ck) = sum(a = 0, K, sum(cc = 0, K - a, binomial(1/2, a) * (-bj)^a * binomial(1/2, cc) * (-ck)^cc * 'e^(a + cc) / ('z^a * ('z - 1)^cc)));
\\ coordinates: principal parts at 0 and 1 (orders 1..K) and the value at infinity (degree-0 part)
cv(f) = {
  my(v = vector(2 * K + 1), s0 = f + O('z^1), s1 = subst(f, 'z, 1 + 'y) + O('y^1));
  for (k = 1, K, v[k] = polcoef(s0, -k, 'z); v[K + k] = polcoef(s1, -k, 'y));
  v[2 * K + 1] = subst(subst(f, 'z, 1 / 'w), 'w, 0);
  v;
}
run(b, c) = {
  my(F = [P(b[1], c[1]), P(b[1], c[2]), P(b[2], c[1]), P(b[2], c[2])]);
  my(co = vector(4, i, vector(K + 1, s, cv(polcoef(F[i], s - 1, 'e)))), D = 2 * K + 1);
  for (t = 0, 6,
    \\ unknowns x_{i,d}, d = 0..t; coefficient of order s: sum_{i,d} x_{i,d} co[i][s-d]
    my(nu = 4 * (t + 1), rows = List(), gi(i, d) = (i - 1) * (t + 1) + d + 1);
    for (s = 0, t - 1, for (pos = 1, D, listput(rows, vector(nu, u, my(i = (u - 1) \ (t + 1) + 1, d = (u - 1) % (t + 1)); if (s - d >= 0, co[i][s - d + 1][pos], 0)))));
    my(ker = if (#rows, matker(Mat(Vec(rows)~)), matid(nu)));
    my(lead = matrix(D, #ker, pos, col, sum(u = 1, nu, my(i = (u - 1) \ (t + 1) + 1, d = (u - 1) % (t + 1)); if (t - d >= 0, ker[u, col] * co[i][t - d + 1][pos], 0))));
    my(r = matrank(lead));
    emit(Str("  t=", t, ": dim S_t = ", r));
    if (t == 4, my(pr = select(v -> v != [0, 0], vector(#ker, col, [lead[2, col], lead[K + 2, col]])));
      if (#pr, emit(Str("    new direction: (u1^2, u2^2) coefficients proportional to ", pr[1], ", ratio ", if (pr[1][2] != 0, pr[1][1] / pr[1][2], "oo")))));
    if (t == 4, for (x = 0, 2, emit(Str("    pole order <= (", x, ", y), y = 0..2: ", vector(3, yy, my(y = yy - 1, drop = concat(vector(K - x, k, x + k), vector(K - y, k, K + y + k)));
      matrank(lead) - matrank(matrix(#drop, #ker, a, col, lead[drop[a], col])) ))))));
}
main() = {
  emit("shapes b = (-3/7, 5/7), c = (2/5, -1):"); run([-3/7, 5/7], [2/5, -1]);
  emit("shapes b = (1/3, -2), c = (3/4, 5/2):"); run([1/3, -2], [3/4, 5/2]);
  \\ ratio data for a formula: vary the shapes
  foreach ([[[1, 2], [3, 5]], [[1, 3], [3, 5]], [[1, 2], [3, 7]], [[2, 3], [3, 5]], [[0, 1], [0, 1]], [[0, 2], [0, 1]], [[0, 1], [0, 3]]], bc,
    emit(Str("shapes b = ", bc[1], ", c = ", bc[2], ":")); run(bc[1], bc[2]));
}
main();
quit
