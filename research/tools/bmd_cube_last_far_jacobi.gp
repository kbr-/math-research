\\ Exceptional Jacobi lead for the last even-peeling far polynomial (3 October 2026; cycle bmd-20261003-zi).
\\ Question: is W_(b-1) at b = 3 (e = 1, degree 16), written in w = -x so that its branch points are w = 0, 1, a Wronskian of
\\ Jacobi polynomials of one family, Wr[P_m^(a,b)(1-2w), m in S] with the factors w, w-1 removed (the exceptional Jacobi
\\ denominators, Darboux-Crum transforms of a Jacobi system)?  Search (a,b) in [-9/2, 9/2]^2, half-integer steps, a+1 not a
\\ non-positive integer, all S of distinct degrees <= 12 with |S| <= 4 and nominal degree sum(S) - binom(|S|,2) >= 16.
\\ Positive control: a planted target Wr[P_3, P_7, P_8]^(-3/2, 1/2), which must be found.
OUT = getenv("OUT");
emit(s) = print(s); if (OUT != 0 && OUT != "", write(OUT, s));
strip(N) = { if (N == 0, return(0)); while (subst(N, 'w, 0) == 0, N = N / 'w); while (subst(N, 'w, 1) == 0, N = N / ('w - 1)); N / pollead(N); }
jac(m, a, b) = sum(kk = 0, m, prod(i = 0, kk - 1, (-m + i) * (m + a + b + 1 + i) / ((a + 1 + i) * (i + 1))) * 'w^kk);
plainwr(S) = { my(d = #S, M = matrix(d, d)); for (i = 1, d, my(g = S[i]); for (j = 1, d, M[i, j] = g; g = deriv(g, 'w))); strip(matdet(M)); }
Rn(n) = n * (2 * n - 1);
farW(e, l, c) = {
  my(bl = [[0, 0, Rn(e)], [-3, 0, 1], [0, -(Rn(l) + 2), Rn(l)], [-7/2, 0, 4 * e], [-5/2, 1/2 - 4 * l, 4 * l], [0, -7/2 + 4 * e - 4 * e * l, 4 * e * l]]);
  my(d = sum(i = 1, 6, bl[i][3]), M = matrix(d, d), row = 0);
  foreach (bl, b, for (j = 0, b[3] - 1, row++; my(g = 'x^j);
    for (m = 1, d, M[row, m] = g; g = deriv(g, 'x) + (b[2] / 'x + b[1] * c / (1 + c * 'x)) * g)));
  my(N = numerator(matdet(M)));
  while (subst(N, 'x, 0) == 0, N = N / 'x); while (subst(N, 'x, -1/c) == 0, N = N / (1 + c * 'x));
  N / pollead(N);
}
search(R, name, MMAX, SMAX, LO, HI) = {
  my(dR = poldegree(R), hits = List(), tried = 0);
  forstep (a = LO, HI, 1/2, if (denominator(a) == 1 && a <= -1, next);
    forstep (b = LO, HI, 1/2,
      my(J = vector(MMAX + 1, m, jac(m - 1, a, b)));
      for (s = 1, SMAX, forsubset([MMAX + 1, s], T,
        my(S = Vec(T) - vector(s, i, 1));
        if (vecsum(S) - s * (s - 1) / 2 < dR, next);
        tried++;
        my(W = plainwr(vector(s, i, J[S[i] + 1])));
        if (W != 0 && W == R, listput(hits, [a, b, S]))))));
  emit(Str(name, ": deg ", dR, "; tried ", tried, " (a,b,S); matches ", #hits, if (#hits, Str(": ", Vec(hits)), "")));
}
main() = { my(H = if (getenv("HALF"), eval(getenv("HALF")), 9/2));
  my(ctrl = plainwr([jac(3, -3/2, 1/2), jac(7, -3/2, 1/2), jac(8, -3/2, 1/2)]));
  search(ctrl, "control Wr[P_3,P_7,P_8]^(-3/2,1/2)", 12, 4, -H, H);
  my(W = subst(farW(1, 1, 1), 'x, -'w)); W = strip(W);
  search(W, "W_(b-1), b = 3 (e = 1)", 12, 4, -H, H);
}
main();
