\\ Valuations of every consecutive window of a far-near product block (29 September 2026; cycle bmd-20260929-zj).
\\ Rows (i, j): coefficient of S^e in (1+s_i/S)^(-3/2)(1+t_j S)^(-3/2) = sum_{b-a=e} beta_a beta_b s_i^a t_j^b, with
\\ s_i = c_i q^i (i = 1..F) and t_j = d_j q^j (j = 1..n), q = 1000003 playing eps, as in the caterpillar.
\\ Tested hypothesis: the window valuation splits as A_F(p) + B_n(q') (far part depending only on F and p, near part
\\ only on n and q'), for windows [-p, q'], p + q' + 1 = F n, F - 1 <= p <= F n - n. Prints the valuation of each window.
\\ Truncation: entries are cut at a, b <= K; the change has valuation > K, so values below K are exact.
OUT = getenv("OUT");
emit(s) = print(s); if (OUT != 0 && OUT != "", write(OUT, s));
q = 1000003;
K = 120;
be(k) = binomial(-3/2, k);
main() = {
  my(cs = [3, -7, 11, 5, -2], ds = [2, 13, -5, 7, 17]);
  foreach ([[1,3],[2,2],[2,3],[3,2],[2,4],[4,2],[3,3],[2,5],[3,4],[4,3],[4,4]], FN,
    my(F = FN[1], n = FN[2], L = F * n, s = vector(F, i, cs[i] * q^i), t = vector(n, j, ds[j] * q^j), res = List());
    my(ent(i, j, e) = sum(a = max(0, -e), K - max(0, e), be(a) * be(a + e) * s[i]^a * t[j]^(a + e)));
    for (p = F - 1, L - n,
      my(A = matrix(L, L, r, c, my(i = (r - 1) \ n + 1, j = (r - 1) % n + 1); ent(i, j, c - 1 - p)), d = matdet(A));
      listput(res, [p, L - 1 - p, if (d == 0, oo, valuation(d, q))]));
    emit(Str(F, "x", n, ": [p, q', val] = ", Vec(res))));
}
main();
