\\ Search: is the far polynomial R_(n,k) a Wronskian of Jacobi polynomials? (2 October 2026; cycle bmd-20261002-z)
\\ Crum/Darboux transforms of a Jacobi family have Wronskians that are Wronskians of Jacobi polynomials of one family indexed by a
\\ set (the exceptional-polynomial setting).  For each target (n,k), search all (a,b) in {-7/2, -3, ..., 7/2}^2 with a+1 not a (default range; wider ranges are passed per target)
\\ non-positive integer, and all index sets S of distinct degrees <= MMAX, |S| <= SMAX, whose nominal Wronskian degree
\\ sum(S) - binom(|S|,2) is at least deg R; compare Wr[P_m^(a,b)(1-2w), m in S] (factors w, w-1 removed, monic) with R.
\\ Jacobi polynomials are taken as 2F1(-m, m+a+b+1; a+1; w) (constant factors do not matter).
OUT = getenv("OUT");
emit(s) = print(s); if (OUT != 0 && OUT != "", write(OUT, s));
strip(N) = { if (N == 0, return(0)); while (subst(N, 'w, 0) == 0, N = N / 'w); while (subst(N, 'w, 1) == 0, N = N / ('w - 1)); N / pollead(N); }
thetastep(p, alpha, beta, e) = { (1 - 'w) * ('w * deriv(p, 'w) + (beta - e) * p) - alpha * 'w * p; }
wr(cls) = {
  my(d = sum(i = 1, #cls, #cls[i][3]), M = matrix(d, d), row = 0);
  foreach(cls, c, my(a = c[1], b = c[2]);
    foreach (c[3], f, row++; my(g = f);
      for (m = 1, d, M[row, m] = g; g = deriv(g, 'w) + (a / 'w + b / ('w - 1)) * g)));
  strip(numerator(matdet(M)));
}
farpoly(n, k) = {
  my(C = n * (n - 1) / 2, P = (k - 1) * (k - 2) / 2, E = concat(vector(C + P + 2, t, t - 1 - C), vector((k - 1) * n, t, 1/2 - (n - 1) + t - 1)), q = #E);
  my(P3 = vector(k - 1, j, my(p = 'w^(j - 1), al = 1/2); for (i = 1, q, p = thetastep(p, al, 0, E[i]); al--); p));
  my(P4 = vector(n, j, my(p = 'w^(j - 1), al = 1/2); for (i = 1, q, p = thetastep(p, al, 1/2 - (n - 1), E[i]); al--); p));
  wr([[0, 0, P3], [1/2, 0, apply(p -> p * 'w^(-(n - 1)), P4)]]);
}
jac(m, a, b) = sum(kk = 0, m, prod(i = 0, kk - 1, (-m + i) * (m + a + b + 1 + i) / ((a + 1 + i) * (i + 1))) * 'w^kk);
plainwr(S) = { my(d = #S, M = matrix(d, d)); for (i = 1, d, my(g = S[i]); for (j = 1, d, M[i, j] = g; g = deriv(g, 'w))); strip(matdet(M)); }
search(n, k, MMAX, SMAX, LO = -7/2, HI = 7/2) = {
  my(R = farpoly(n, k), dR = poldegree(R), hits = List(), tried = 0);
  forstep (a = LO, HI, 1/2, if (denominator(a) == 1 && a <= -1, next);
    forstep (b = LO, HI, 1/2,
      my(J = vector(MMAX + 1, m, jac(m - 1, a, b)));
      for (s = 1, SMAX, forsubset([MMAX + 1, s], T,
        my(S = Vec(T) - vector(s, i, 1));
        if (vecsum(S) - s * (s - 1) / 2 < dR, next);
        tried++;
        my(W = plainwr(vector(s, i, J[S[i] + 1])));
        if (W != 0 && W == R, listput(hits, [a, b, S]))))));
  emit(Str("(n,k)=", [n, k], ": deg R ", dR, "; tried ", tried, " (a,b,S); matches ", #hits, if (#hits, Str(": ", Vec(hits)), "")));
}
search(1, 3, 6, 2);
search(1, 4, 8, 2, -15, 8);
search(2, 3, 9, 4, -15, 8);
search(3, 3, 13, 5);
