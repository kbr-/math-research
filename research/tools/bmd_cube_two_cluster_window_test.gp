\\ Falsification test of the balanced-window conjecture for products of two caterpillar clusters
\\ (29 September 2026; cycle bmd-20260929-z; conj:cube-two-cluster-balanced-window).
\\ Conjecture: for F far roots s_i with valuations F, F-1, ..., 1 and n near roots t_j with valuations 1, ..., n
\\ (generic constants), the span of (1+s_i/S)^(-3/2)(1+t_j S)^(-3/2) has minimal Pluecker valuation exactly on
\\ the consecutive windows of length Fn that extend {-(F-1), ..., n-1} by as equal numbers of exponents on each
\\ side as possible: one window if (F-1)(n-1) is even, two (a tie) if it is odd.
\\ Predictions tested here (N = 7 middle components): 2 x 4 -> tie of {-3..4} and {-2..5}; 3 x 3 -> {-4..4}.
\\ eps is the prime q = 1000003 and valuations are q-adic, as in bmd_cube_two_cluster_limit_six.gp.
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
run("N=7 scale 2 (far 2, near 4); predicted tie {-3..4}, {-2..5}", [e^2 / 7, e / 3], [5 * e, 11 * e^2, 13 * e^3, 17 * e^4], 6, 18);
run("N=7 scale 3 (far 3, near 3); predicted {-4..4}", [e^3 / 7, e^2 / 3, e / 2], [5 * e, 11 * e^2, 13 * e^3], 6, 18);
