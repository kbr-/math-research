\\ Four-root Taylor determinant with lambda formal, and simplicity of the four-root points (29 September 2026;
\\ cycle bmd-20260929-zg). (a) Factors det[[T^m] phi_(b_i) phi_(b_j)] (M = 4, columns 0..5, phi = (1 + bT)^(-lam))
\\ in Q[lam, p, q, r, s], to prove C(lam) Vand^2 prod(pair-sum differences) for all lam at once and find the roots of
\\ C(lam). (b) For the roots (2, -3, 5, 7/2), checks that the three quadratics q_(ij|kl) are squarefree of degree 2
\\ and pairwise coprime (nonzero discriminants and resultants).
OUT = getenv("OUT");
emit(s) = print(s); if (OUT != 0 && OUT != "", write(OUT, s));
main() = {
  my(b = [p, q, r, s], M = 4, R = 6, rows = List());
  for (i = 1, M, for (j = i + 1, M, listput(rows, vector(R, m, sum(k = 0, m - 1, binomial(-lam, k) * binomial(-lam, m - 1 - k) * b[i]^k * b[j]^(m - 1 - k))))));
  my(d = matdet(matrix(R, R, a, c, rows[a][c])));
  my(V = (p - q) * (p - r) * (p - s) * (q - r) * (q - s) * (r - s), D = (p + q - r - s) * (p - q + r - s) * (p - q - r + s));
  my(Cl = d / (V^2 * D));
  emit(Str("(a) det / (Vand^2 * pair-sum differences) is a polynomial in lam only: ", vecmax([poldegree(Cl, p), poldegree(Cl, q), poldegree(Cl, r), poldegree(Cl, s)]) == 0 && denominator(Cl) == 1, "; C(lam) factorization ", factor(Cl)));
  my(bb = [2, -3, 5, 7/2], qd(i, j, k, l) = numerator(bb[i] / (1 + bb[i] * t) + bb[j] / (1 + bb[j] * t) - bb[k] / (1 + bb[k] * t) - bb[l] / (1 + bb[l] * t)));
  my(Q = [qd(1, 2, 3, 4), qd(1, 3, 2, 4), qd(1, 4, 2, 3)]);
  emit(Str("(b) roots ", bb, ": degrees ", apply(poldegree, Q), "; discriminants nonzero ", vector(3, i, poldisc(Q[i]) != 0),
    "; pairwise resultants nonzero ", [polresultant(Q[1], Q[2]) != 0, polresultant(Q[1], Q[3]) != 0, polresultant(Q[2], Q[3]) != 0]));
}
main();
