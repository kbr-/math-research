\\ The Taylor determinant of the pair space at T = 0 (29 September 2026; cycle bmd-20260929-zf).
\\ Tested question: is det[[T^m] phi_(b_i) phi_(b_j)]_{pairs i<j, 0 <= m < r}, r = binom(M,2), phi_b = (1 + bT)^(-3/2),
\\ a constant times a power of the Vandermonde of b (or another closed form)? Prints its factorization for M = 2..5.
OUT = getenv("OUT");
emit(s) = print(s); if (OUT != 0 && OUT != "", write(OUT, s));
main() = {
  my(V = [p, q, r, s, u]);
  for (M = 2, 5,
    my(b = V[1..M], R = binomial(M, 2), rows = List());
    for (i = 1, M, for (j = i + 1, M, listput(rows, vector(R, m, sum(k = 0, m - 1, binomial(-3/2, k) * binomial(-3/2, m - 1 - k) * b[i]^k * b[j]^(m - 1 - k))))));
    my(A = matrix(R, R, a, c, rows[a][c]), d = matdet(A));
    emit(Str("M=", M, ": factorization ", factor(d))));
}
main();
