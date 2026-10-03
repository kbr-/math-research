\\ Exact identical-vanishing test of the n=5 conic limit Z_6 mod 3 (written by the fresh-context reviewer of
\\ cycle kbt, 9 October 2026, promoted to the record).  The Hasse coefficient of T^m is homogeneous of degree m
\\ in (a1,a3), so det Z_d is homogeneous of degree D = N(N-1)/2 - 4*binom(4d-4,2) (2400 at d=6).  With a3 = 1
\\ and a1 a generator of GF(p^k), k > D, the determinant vanishes iff det(t,1) is identically zero mod p.
\\ Control: p = 5.
default(parisizemax, 2^30);
rows(a1, a3, d, N, o) = {
  my(l1 = o + a1 * T + O(T^N), l3 = o + a3 * T + O(T^N), w1 = sqrt(l1), w3 = sqrt(l3), gens, bnds, R = List());
  gens = [l3^2, w3 * l1, w1 * l3^2 / l1, w1 * w3]; bnds = vector(4, i, 4 * d - 5);
  for(j = 1, 4, for(i = 0, bnds[j], listput(R, gens[j] * T^i)));
  Vec(R);
}
chk(p, d, k) = {
  my(N = 16*d-16, x = ffgen(ffinit(p, k, 'y)), o = x^0, Rw = rows(x, o, d, N, o), M);
  M = matrix(N, N, i, c, polcoeff(Rw[i], c - 1, T));
  print("p=", p, " d=", d, " k=", k, " D=", N*(N-1)/2 - 4*sum(i=0,4*d-5,i), " detzero: ", matdet(M) == 0, " rank: ", matrank(M));
}
chk(5, 6, 2411);
chk(3, 6, 2411);
quit;
