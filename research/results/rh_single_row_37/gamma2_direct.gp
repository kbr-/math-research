\\ Independent control of the kernel's gamma_2(n): for the primary n = a + b w listed below (taken from the
\\ kernel's dump: split primes, an inert prime, the rational primes 7 and 13, products of two distinct split
\\ primes, and last a product with an inert factor, norm 175, and a product of three primes, norm 637), compute
\\   gamma_2(n) = N(n)^{-1/2} sum_{x mod n} (x/n)_3 e(x/n),  e(z) = exp(4 pi i Im z / sqrt 3),
\\ directly from the definition: the cubic symbol as the product over the prime ideals dividing n of
\\ x^((N p - 1)/3) in the residue field, the sum over all a', b' in [0, N)^2 counting each class N times.
\\ Output: a b re im, to be compared with the kernel's dump.
default(realprecision, 30);
rhK = nfinit(rhy^2 + rhy + 1);
rhw = exp(2*Pi*I/3);
rhcub(x, mp, q) =
{
  my(r = nfmodpr(rhK, x, mp), t);
  if(r == 0, return(0));
  t = r^((q - 1)/3);
  for(k = 0, 2, if(nfmodpr(rhK, Mod(rhy, rhy^2 + rhy + 1)^k, mp) == t, return(rhw^k)));
  error("no cube root");
}
rhg2(a, b) =
{
  my(nc = a + b*rhw, N = a^2 - a*b + b^2, fa = idealfactor(rhK, a + b*rhy), m = matsize(fa)[1], mps, qs, s = 0, c);
  mps = vector(m, i, nfmodprinit(rhK, fa[i, 1])); qs = vector(m, i, idealnorm(rhK, fa[i, 1]));
  for(i = 1, m, if(fa[i, 2] != 1, error("not squarefree")));
  for(u = 0, N - 1, for(v = 0, N - 1,
    c = prod(i = 1, m, rhcub(u + v*rhy, mps[i], qs[i]));
    if(c != 0, s += c*exp(4*Pi*I*imag((u + v*rhw)/nc)/sqrt(3)))));
  s /= N*sqrt(N);
  print(a, " ", b, " ", real(s), " ", imag(s));
}
{
  rhg2(-2, -3); rhg2(1, 3); rhg2(4, 3); rhg2(-5, 0); rhg2(7, 0); rhg2(-11, -6); rhg2(10, 9);
  rhg2(-8, 3); rhg2(-14, -15); rhg2(13, 0); rhg2(-5, -18); rhg2(25, 9); rhg2(-23, -3); rhg2(-20, 3);
  rhg2(10, 15); rhg2(28, 21);
}
