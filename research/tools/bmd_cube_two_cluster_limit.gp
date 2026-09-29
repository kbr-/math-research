\\ Limit of a far-near product block of two multiscale clusters (29 September 2026; cycle bmd-20260929-y).
\\ Rows F_(i,j) = (1 + s_i/S)^(-3/2) (1 + t_j S)^(-3/2), far constants s_i and near constants t_j at
\\ separated scales. Coefficient of S^e: sum_(b-a=e) beta_a beta_b s_i^a t_j^b. Prints, for each case, the
\\ minimal eps-valuation of the Pluecker coordinates on exponent sets E in [-L, L] and all minimizing E.
\\ A unique minimizer E means the normalized span tends to span{S^e : e in E}.
\\ Case N=5 scale 2: s = (e^2/c1, e/c2), t = (c4 e, c5 e^2).
OUT = getenv("OUT");
emit(s) = print(s); if (OUT != 0 && OUT != "", write(OUT, s));
be(n) = binomial(-3/2, n);
row(s, t, L, K) = vector(2 * L + 1, c, my(ee = c - L - 1); sum(a = max(0, -ee), K, my(b = a + ee); if (b > K, 0, be(a) * be(b) * s^a * t^b)));
run(name, sv, tv, L, K) = {
  my(rows = List());
  foreach (sv, s, foreach (tv, t, listput(rows, row(s, t, L, K))));
  my(A = Mat(Vec(rows)~), n = #rows, best = oo, arg = List());
  A = matrix(n, 2 * L + 1, i, j, rows[i][j]);
  forsubset([2 * L + 1, n], E,
    my(d = matdet(matrix(n, n, i, j, A[i, E[j]])));
    if (d != 0, my(v = valuation(d, e)); if (v < best, best = v; arg = List([Vec(E) - vector(n, i, L + 1)]), if (v == best, listput(arg, Vec(E) - vector(n, i, L + 1))))));
  emit(Str(name, ": minimal valuation ", best, ", minimizing exponent sets ", Vec(arg)));
}
run("N=5 scale 2 (far 2, near 2)", [e^2 / 7, e / 3], [5 * e, 11 * e^2], 4, 12);
