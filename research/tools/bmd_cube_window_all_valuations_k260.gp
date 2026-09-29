\\ Rerun of bmd_cube_window_all_valuations.gp with truncation K = 260 (29 September 2026; cycle bmd-20260929-zj),
\\ for 4x4, whose window valuations exceed the earlier K = 120, and 3x5. These are the smallest cases that
\\ overdetermine the additive hypothesis val[-p, q'] = base(F, n) + sum_{m <= p-F+1} c_F(m) + sum_{m <= q'-n+1} c_n(m),
\\ with per-cluster increments c_F depending only on the cluster size.
\\ Rows (i, j): coefficient of S^e in (1+s_i/S)^(-3/2)(1+t_j S)^(-3/2), s_i = c_i q^i, t_j = d_j q^j, q = 1000003.
OUT = getenv("OUT");
emit(s) = print(s); if (OUT != 0 && OUT != "", write(OUT, s));
q = 1000003;
K = 260;
be(k) = binomial(-3/2, k);
main() = {
  my(cs = [3, -7, 11, 5, -2], ds = [2, 13, -5, 7, 17]);
  foreach ([[4,4],[3,5]], FN,
    my(F = FN[1], n = FN[2], L = F * n, s = vector(F, i, cs[i] * q^i), t = vector(n, j, ds[j] * q^j), res = List());
    my(ent(i, j, e) = sum(a = max(0, -e), K - max(0, e), be(a) * be(a + e) * s[i]^a * t[j]^(a + e)));
    for (p = F - 1, L - n,
      my(A = matrix(L, L, r, c, my(i = (r - 1) \ n + 1, j = (r - 1) % n + 1); ent(i, j, c - 1 - p)), d = matdet(A));
      listput(res, [p, L - 1 - p, if (d == 0, oo, valuation(d, q))]));
    emit(Str(F, "x", n, ": [p, q', val] = ", Vec(res))));
}
main();
