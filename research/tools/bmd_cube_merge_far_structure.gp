\\ Structure of the merge far polynomials (2 October 2026; cycle bmd-20261002-a).
\\ farR(n, k) is the exact R_(n,k) over Q, as in bmd_cube_merge_far_exact.gp.
\\ Part A: n = 1.  Claim: R_(1,k)(w) is proportional to Q_r(2w - 1), r = binom(k-1, 2), where Q_r is the binary-face
\\   polynomial of thm:cube-binary-face-weierstrass-points (Q_0 = 1, Q_1 = 3T, Q_(j+1) = (2j+3) T Q_j + j(j+2)(1-T^2) Q_(j-1)).
\\ Part B: n >= 2, tests of two routes to squarefreeness: reality of the roots (real Schubert transversality) and
\\   smoothness of the discriminant (a product formula), at (n,k) = (2,3), (3,3), (2,4), (4,3).
default(parisizemax, 2000000000);
OUT = getenv("OUT");
\\ farclasses and farR copied from bmd_cube_merge_far_exact.gp
farclasses(n, k) = {
  my(C = n * (n - 1) / 2, P = (k - 1) * (k - 2) / 2);
  [[0, 0, vector(C + 2 + P, t, 'w^(t - 1 - C))], [1/2, 0, vector((k - 1) * n, t, 'w^(t - n))],
   [0, 1/2, vector(k - 1, t, 'w^(t - 1))], [1/2, 1/2, vector(n, t, 'w^(t - n))]];
}
farR(n, k) = {
  my(F = farclasses(n, k), d = sum(c = 1, 4, #F[c][3]), M = matrix(d, d), row = 0);
  for (c = 1, 4, my(a = F[c][1], b = F[c][2]);
    foreach (F[c][3], f, row++; my(g = f);
      for (m = 1, d, M[row, m] = g; g = deriv(g, 'w) + (a / 'w + b / ('w - 1)) * g)));
  my(W = matdet(M), N = numerator(W));
  while (subst(N, 'w, 0) == 0, N = N / 'w);
  while (subst(N, 'w, 1) == 0, N = N / ('w - 1));
  N / pollead(N);
}
emit(s) = print(s); if (OUT != 0 && OUT != "", write(OUT, s));
Qr(r) = { my(a = 1, b = 3 * 'T, c); if (r == 0, return(a)); for (j = 1, r - 1, c = (2 * j + 3) * 'T * b + j * (j + 2) * (1 - 'T^2) * a; a = b; b = c); b; }
partA() = {
  for (k = 3, 7, my(R = farR(1, k), r = (k - 1) * (k - 2) / 2, Q = subst(Qr(r), 'T, 2 * 'w - 1));
    emit(Str("A: k=", k, " deg R_(1,k)=", poldegree(R), " r=", r, " R = Q_r(2w-1)/lead: ", R == Q / pollead(Q))));
}
partB() = {
  foreach([[2, 3], [3, 3], [2, 4], [4, 3]], v, my(R = farR(v[1], v[2]), P = R / content(R));
    my(dc = abs(numerator(poldisc(P))), f = factor(dc, 10^6), last = f[#f[, 1], 1]);
    emit(Str("B: (n,k)=", v, " deg ", poldegree(R), " real roots ", polsturm(R),
      "; disc: primes below 10^6 ", f[1..#f[, 1] - 1, 1]~, ", cofactor of ", #Str(last), " digits, pseudoprime ", ispseudoprime(last))));
}
partA();
partB();
