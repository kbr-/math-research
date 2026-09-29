\\ Limits of the far-near product blocks of the N = 6 caterpillar middle components (29 September 2026;
\\ cycle bmd-20260929-z). Rows F_(i,j) = (1 + s_i/S)^(-3/2) (1 + t_j S)^(-3/2), far constants s_i and near
\\ constants t_j at caterpillar scales. Coefficient of S^e: sum_(b-a=e) beta_a beta_b s_i^a t_j^b. Prints the
\\ minimal eps-valuation of the Pluecker coordinates on exponent sets E in [-L, L] and all minimizing E.
\\ Cases: 2 far x 3 near (scale 2) and 3 far x 2 near (scale 3). For speed eps is the prime q = 1000003 and
\\ valuations are q-adic valuations of exact rational minors: the constants and the binomial denominators are
\\ q-units, and terms beyond the truncation K have q-valuation far above the minima. A symbolic-eps version
\\ timed out at 170 s.
OUT = getenv("OUT");
emit(s) = print(s); if (OUT != 0 && OUT != "", write(OUT, s));
q = 1000003;
be(n) = binomial(-3/2, n);
row(s, t, L, K) = vector(2 * L + 1, c, my(ee = c - L - 1); sum(a = max(0, -ee), K, my(b = a + ee); if (b > K, 0, be(a) * be(b) * s^a * t^b)));
run(name, sv, tv, L, K) = {
  my(rows = List());
  foreach (sv, s, foreach (tv, t, listput(rows, row(s, t, L, K))));
  my(n = #rows, best = oo, arg = List(), A = matrix(n, 2 * L + 1, i, j, rows[i][j]));
  forsubset([2 * L + 1, n], E,
    my(d = matdet(matrix(n, n, i, j, A[i, E[j]])));
    if (d != 0, my(v = valuation(d, q)); if (v < best, best = v; arg = List([Vec(E) - vector(n, i, L + 1)]), if (v == best, listput(arg, Vec(E) - vector(n, i, L + 1))))));
  emit(Str(name, ": minimal valuation ", best, ", minimizing exponent sets ", Vec(arg)));
}
e = q;
run("N=5 scale 2 control (far 2, near 2; symbolic run found [[-2,-1,0,1],[-1,0,1,2]])", [e^2 / 7, e / 3], [5 * e, 11 * e^2], 4, 12);
run("N=6 scale 2 (far 2, near 3)", [e^2 / 7, e / 3], [5 * e, 11 * e^2, 13 * e^3], 5, 14);
run("N=6 scale 3 (far 3, near 2)", [e^3 / 7, e^2 / 3, e / 2], [5 * e, 11 * e^2], 5, 14);
