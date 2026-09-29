\\ Control for the confluent half-class reduction (29 September 2026).
\\ Tested statement: for a cluster of M roots with one double root u and simple roots b_3..b_M,
\\ the r x r Taylor determinant at T = 0 (r = binom(M,2), orders 0..r-1) of the confluent internal
\\ rows is nonzero at a random rational point, M = 3..7. Rows: ((1+b_i T)(1+b_k T))^(-3/2) for simple
\\ pairs, (1+uT)^(-3/2)(1+b_k T)^(-3/2) and its u-derivative T(1+uT)^(-5/2)(1+b_k T)^(-3/2), and
\\ (1+uT)^(-3). The general proof (Moebius translation) is in the notebook entry.
OUT = getenv("OUT");
emit(s) = print(s); if (OUT != 0 && OUT != "", write(OUT, s));
ser(c, e, L) = sum(m = 0, L - 1, binomial(e, m) * c^m * T^m) + O(T^L);
main() = {
  setrand(29);
  for (M = 3, 7,
    my(r = M * (M - 1) / 2, L = r, u = (random(201) - 100) / (random(9) + 1), B = vector(M - 2, i, (random(2001) - 1000) / (random(13) + 1)));
    my(rows = List());
    for (i = 1, #B, for (k = i + 1, #B, listput(rows, ser(B[i], -3/2, L) * ser(B[k], -3/2, L))));
    for (k = 1, #B,
      listput(rows, ser(u, -3/2, L) * ser(B[k], -3/2, L));
      listput(rows, T * ser(u, -5/2, L) * ser(B[k], -3/2, L)));
    listput(rows, ser(u, -3, L));
    if (#rows != r, error("row count"));
    my(A = matrix(r, r, i, j, polcoeff(truncate(rows[i]), j - 1, T)));
    emit(Str("M=", M, " r=", r, " confluent Taylor determinant at T=0 nonzero: ", matdet(A) != 0)));
}
main();
