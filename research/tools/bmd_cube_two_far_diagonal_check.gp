\\ Check of lem:cube-two-far-diagonal-coefficient (29 September 2026; cycle bmd-20260929-zl).
\\ Lemma: for the two-far window [-(n-r), n-1+r] and K* = {0..n-r-1} u {n-r+1, n-r+3, ..., n+r-1},
\\ the skew determinant det[beta_(k-a)]_(k in K*, a in E \ K*) equals beta_1^r det[beta_(m+k-j)]_(0<=k,j<m), m = n-r,
\\ up to sign. Compares this with the directly computed determinant for n = 2..7, all r.
OUT = getenv("OUT");
emit(s) = print(s); if (OUT != 0 && OUT != "", write(OUT, s));
be(k) = if (k < 0, 0, binomial(-3/2, k));
main() = {
  for (n = 2, 7, for (r = 0, n - 1,
    my(m = n - r, E = [-m .. n - 1 + r], Ks = concat([0 .. m - 1], vector(r, i, m - 1 + 2 * i)), A = setminus(Set(E), Set(Ks)));
    my(direct = matdet(matrix(n, n, a, b, be(Ks[a] - A[b]))), formula = be(1)^r * matdet(matrix(m, m, k, j, be(m + k - j))));
    emit(Str("n=", n, " r=", r, ": direct ", direct, ", formula ", formula, ", equal up to sign: ", direct == formula || direct == -formula))));
}
main();
