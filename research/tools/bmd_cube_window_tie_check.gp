\\ Robustness of the 2x5 window tie (29 September 2026; cycle bmd-20260929-zj). The window valuations of the 2x5
\\ far-near product block (bmd_cube_window_all_valuations.gp) tie at p = 3 and p = 4 (value 59). A tie that is not
\\ forced by the F = n mirror symmetry could be an artifact of the constants; this recomputes all 2x5 windows (and
\\ 3x4 as a control without tie) with two further constant sets. Same rows, q = 1000003, truncation K = 120.
OUT = getenv("OUT");
emit(s) = print(s); if (OUT != 0 && OUT != "", write(OUT, s));
q = 1000003;
K = 120;
be(k) = binomial(-3/2, k);
main() = {
  foreach ([[[5, 17, -3], [-11, 4, 9, -23, 6]], [[-29, 8, 31], [7, -19, 2, 41, -13]]], CD,
    my(cs = CD[1], ds = CD[2]);
    foreach ([[2,5],[3,4]], FN,
      my(F = FN[1], n = FN[2], L = F * n, s = vector(F, i, cs[i] * q^i), t = vector(n, j, ds[j] * q^j), res = List());
      my(ent(i, j, e) = sum(a = max(0, -e), K - max(0, e), be(a) * be(a + e) * s[i]^a * t[j]^(a + e)));
      for (p = F - 1, L - n,
        my(A = matrix(L, L, r, c, my(i = (r - 1) \ n + 1, j = (r - 1) % n + 1); ent(i, j, c - 1 - p)), d = matdet(A));
        listput(res, [p, L - 1 - p, if (d == 0, oo, valuation(d, q))]));
      emit(Str("constants ", cs, " ", ds, ": ", F, "x", n, ": [p, q', val] = ", Vec(res)))));
}
main();
