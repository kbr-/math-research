\\ Minimality for caterpillar clusters of every size: test of the predicted valuation (29 September 2026; cycle
\\ bmd-20260929-zi; thm:cube-caterpillar-minimality). For roots b_i = c_i q^i (i = 1..M, q = 1000003 playing eps),
\\ the theorem predicts val P_{0..r-1} = sum_i val Vand(b_(i+1..M)) + sum_i i * (sum of block_i) - sum_i i * binom(M-i, 2),
\\ where block_i is the i-th block of consecutive Taylor degrees, of size M - i, allotted in order to the groups
\\ i = M-1, M-2, ..., 1 (largest weight first), and every other coordinate has valuation at least one more.
\\ Checks M = 4, 5, 6: the Taylor coordinate against the prediction, and the nearest competitors
\\ E = {0..r-2, r} and E = {0..r-3, r-1, r} against prediction + 1.
OUT = getenv("OUT");
emit(s) = print(s); if (OUT != 0 && OUT != "", write(OUT, s));
q = 1000003;
coef(x, y, m) = sum(k = 0, m, binomial(-3/2, k) * binomial(-3/2, m - k) * x^k * y^(m - k));
predict(M) = {
  my(c0 = sum(i = 1, M - 1, sum(j = i + 1, M, sum(l = j + 1, M, j))), start = 0, cost = 0, sk = 0);
  forstep (i = M - 1, 1, -1, my(sz = M - i); cost += i * sum(m = start, start + sz - 1, m); start += sz; sk += i * binomial(sz, 2));
  c0 + cost - sk;
}
main() = {
  my(cs = [3, -7, 11, 5, -2, 13]);
  for (M = 4, 6,
    my(r = binomial(M, 2), L = r + 2, b = vector(M, i, cs[i] * q^i), rows = List());
    for (i = 1, M, for (j = i + 1, M, listput(rows, vector(L, m, coef(b[i], b[j], m - 1)))));
    my(A = matrix(r, L, a, c, rows[a][c]), val(E) = my(d = matdet(matrix(r, r, a, c, A[a, E[c] + 1]))); if (d == 0, oo, valuation(d, q)));
    my(E0 = [0 .. r - 1], E1 = concat([0 .. r - 2], [r]), E2 = concat([0 .. r - 3], [r - 1, r]));
    emit(Str("M=", M, ": predicted ", predict(M), "; val P_E0 = ", val(E0), "; nearest competitors ", [val(E1), val(E2)], " (predicted >= ", predict(M) + 1, ")")));
}
main();
