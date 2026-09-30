\\ Review tests for far simplicity (2 October 2026; review cycle bmd-20261002-b).
\\ farRl(n, k, lam): the far polynomial of F(n,k) with the square roots replaced by powers lam (lam = 1/2 is R_(n,k)).
\\ Test 1 (generalized hypergeometric): do the coefficient ratios c_(m+1)/c_m of R_(n,k) in w fit P(m)/Q(m) with
\\   deg P, deg Q <= 3?  (R = pFq(...; w) up to scaling iff such a fit exists with the pFq shape.)
\\ Test 2 (reduction mod p): for primes 5 <= p < 60 not dividing denominators, is R mod p squarefree of full degree,
\\   and how many roots does it have in F_p?
\\ Test 3 (exponent family): for (n,k) = (2,3), the discriminant in w of farRl(2,3,lam) as a polynomial in lam: its
\\   degree, its real roots, and its value at lam = 1/2.
default(parisizemax, 2000000000);
OUT = getenv("OUT");
emit(s) = print(s); if (OUT != 0 && OUT != "", write(OUT, s));
farRl(n, k, lam) = {
  my(C = n * (n - 1) / 2, P = (k - 1) * (k - 2) / 2);
  my(F = [[0, 0, vector(C + 2 + P, t, 'w^(t - 1 - C))], [lam, 0, vector((k - 1) * n, t, 'w^(t - n))],
    [0, lam, vector(k - 1, t, 'w^(t - 1))], [lam, lam, vector(n, t, 'w^(t - n))]]);
  my(d = sum(c = 1, 4, #F[c][3]), M = matrix(d, d), row = 0);
  for (c = 1, 4, my(a = F[c][1], b = F[c][2]);
    foreach (F[c][3], f, row++; my(g = f);
      for (m = 1, d, M[row, m] = g; g = deriv(g, 'w) + (a / 'w + b / ('w - 1)) * g)));
  my(N = numerator(matdet(M)));
  while (subst(N, 'w, 0) == 0, N = N / 'w);
  while (subst(N, 'w, 1) == 0, N = N / ('w - 1));
  N;
}
fitratio(R, dP, dQ) = {
  my(d = poldegree(R, 'w), c = vector(d + 1, m, polcoef(R, m - 1, 'w)), rows = List());
  for (m = 0, d - 1, if (c[m + 1] != 0,
    listput(rows, concat(vector(dP + 1, i, m^(i - 1) * c[m + 1]), vector(dQ + 1, i, -m^(i - 1) * c[m + 2])))));
  my(A = Mat(Vec(rows))); A = matrix(#rows, dP + dQ + 2, i, j, rows[i][j]);
  #matker(A);
}
test1() = {
  foreach([[3, 3], [2, 4], [4, 3]], v, my(R = farRl(v[1], v[2], 1/2));
    emit(Str("T1 (n,k)=", v, " deg ", poldegree(R, 'w), ": kernel dimension of the ratio fit with deg P, deg Q <= 3: ", fitratio(R, 3, 3))));
}
test2() = {
  foreach([[2, 3], [3, 3], [2, 4], [4, 3]], v, my(R = farRl(v[1], v[2], 1/2), R0 = R / content(R), d = poldegree(R0, 'w), sq = List(), nsq = List(), roots = List());
    forprime(p = 5, 59, if (denominator(content(R)) % p != 0 && pollead(R0, 'w) % p != 0,
      my(Rp = R0 * Mod(1, p)); if (poldegree(gcd(Rp, deriv(Rp, 'w))) == 0, listput(sq, p), listput(nsq, p));
      listput(roots, [p, #polrootsmod(Rp, p)])));
    emit(Str("T2 (n,k)=", v, " deg ", d, ": squarefree mod p for p in ", Vec(sq), "; not squarefree for ", Vec(nsq), "; roots in F_p ", Vec(roots))));
}
test3() = {
  my(R = farRl(2, 3, 'l), D = poldisc(R, 'w), Dn = numerator(D), f = factor(Dn));
  emit(Str("T3 (n,k)=(2,3): deg_w ", poldegree(R, 'w), ", disc numerator degree in lam ", poldegree(Dn, 'l), ", factor degrees ", apply(x -> poldegree(x, 'l), f[, 1]~),
    ", real roots of each factor ", apply(x -> if (poldegree(x, 'l) > 0, polsturm(x), 0), f[, 1]~), ", value at lam = 1/2 nonzero: ", subst(Dn, 'l, 1/2) != 0));
  emit(Str("T3 factors: ", f[, 1]~));
}
test1();
test2();
test3();
