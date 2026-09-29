\\ Lambda dependence of the pair-space Taylor determinant (29 September 2026; cycle bmd-20260929-zg).
\\ Tested question: for phi_b = (1 + bT)^(-lam), is the Taylor determinant of the pair products at T = 0
\\ (columns 0..5, M = 4 roots) still Vand(b)^2 times the three disjoint pair-sum differences for lam other than
\\ 3/2? Prints the factorization for lam = 3/2, 1/3, 5/2, 1, 2.
OUT = getenv("OUT");
emit(s) = print(s); if (OUT != 0 && OUT != "", write(OUT, s));
main() = {
  my(b = [p, q, r, s], M = 4, R = 6);
  foreach ([3/2, 1/3, 5/2, 1, 2], lam,
    my(rows = List());
    for (i = 1, M, for (j = i + 1, M, listput(rows, vector(R, m, sum(k = 0, m - 1, binomial(-lam, k) * binomial(-lam, m - 1 - k) * b[i]^k * b[j]^(m - 1 - k))))));
    my(d = matdet(matrix(R, R, a, c, rows[a][c])));
    emit(Str("lam=", lam, ": ", if (d == 0, "zero", factor(d)))));
}
main();
