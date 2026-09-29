\\ Test of two competing window rules at F = 2 (29 September 2026; cycle bmd-20260929-zj).
\\ (A) Two-far closed form, fitted on 2x3, 2x4, 2x5: with k = p - 1, val(0) = n + 4 binom(n+1, 3) and
\\     val(k+1) - val(k) = -(n-2)(n+1) + 2kn - k(k-1). Predicts 2x6: 146, 118, 102, 96, 98, 106 (minimum p = 4) and
\\     2x7: 231, 191, 165, 151, 147, 151, 161 (minimum p = 5).
\\ (B) Centered window p = floor((Fn-1)/2): predicts minima at p = 5 (2x6) and p = 6 (2x7).
\\ Same rows as bmd_cube_window_all_valuations.gp, q = 1000003, truncation K = 260 (values below K are exact).
OUT = getenv("OUT");
emit(s) = print(s); if (OUT != 0 && OUT != "", write(OUT, s));
q = 1000003;
K = 260;
be(k) = binomial(-3/2, k);
pred(n) = my(v = n + 4 * binomial(n + 1, 3), r = [v]); for (k = 0, n - 2, v += -(n - 2) * (n + 1) + 2 * k * n - k * (k - 1); r = concat(r, v)); r;
main() = {
  my(cs = [3, -7], ds = [2, 13, -5, 7, 17, 19, -23]);
  foreach ([6, 7], n,
    my(F = 2, L = F * n, s = vector(F, i, cs[i] * q^i), t = vector(n, j, ds[j] * q^j), res = List());
    my(ent(i, j, e) = sum(a = max(0, -e), K - max(0, e), be(a) * be(a + e) * s[i]^a * t[j]^(a + e)));
    for (p = F - 1, L - n,
      my(A = matrix(L, L, r, c, my(i = (r - 1) \ n + 1, j = (r - 1) % n + 1); ent(i, j, c - 1 - p)), d = matdet(A));
      listput(res, if (d == 0, oo, valuation(d, q))));
    emit(Str("2x", n, ": valuations for p = 1..", L - n, ": ", Vec(res), "; closed form predicts ", pred(n))));
}
main();
