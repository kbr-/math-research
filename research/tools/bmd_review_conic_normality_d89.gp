\\ Falsification test of the goal-level route review of cycle kdt (9 October 2026): a copy of
\\ research/tools/bmd_two_pair_conic_normality.gp (cycle kbt) with the degree range d = 8, 9 instead of 2..7.
\\ Question: does the lone exception (d,p) = (6,3) recur at the next degrees (at p = 3 or another small prime),
\\ which would make the conic route need a structured exceptional set?  Prediction (isolated exceptions):
\\ no odd p <= 16d has zero determinant at every sample for d = 8, 9.  Original header follows.
\\ Exceptional-prime test of the n=5 two-pair limit (cycle kbt, 9 October 2026).
\\ Statement tested: by lem:cube-two-pair-confluence, generic normality of V_{5,d} in odd characteristic p
\\ follows from normality at T=0 of the conic space Z_d (roots a1 != a3, nonzero), where for d >= 3
\\   Z_d ~ F*<l3^2, w3*l1, w1*l1^-1*l3^2, w1*w3>,  F = k[T]_{<=4d-5},  l_i = 1+a_i T,  w_i = sqrt(l_i),
\\ and Z_2 = l1^-1 l3^-1 F_4 + w3 l3^-2 F_3 + w1 l1^-2 F_3 + w1 w3 l1^-1 l3^-2 F_3.
\\ For every odd p <= 16d (the small-prime range of statement 2 at n=5) and d = 2..7, the length-N Hasse
\\ determinant at T=0 is computed at SAMPLES random (a1,a3) in GF(p^e), p^e > 10^5 (GF(p^2) at small p flagged non-generic zeros).  A nonzero value proves generic
\\ normality of Z_d mod p; zeros at every sample flag a candidate exceptional prime.  The rational collision
\\ resonance (thm:cube-rational-collision-resonance) failed exactly at p | N^2-1 on a conic; compare.

rows(a1, a3, d, N, o) = {
  my(l1 = o + a1 * T + O(T^N), l3 = o + a3 * T + O(T^N), w1 = sqrt(l1), w3 = sqrt(l3), gens, bnds, R = List());
  if(d >= 3,
    gens = [l3^2, w3 * l1, w1 * l3^2 / l1, w1 * w3]; bnds = vector(4, i, 4 * d - 5),
    gens = [1 / (l1 * l3), w3 / l3^2, w1 / l1^2, w1 * w3 / (l1 * l3^2)]; bnds = [4, 3, 3, 3]);
  for(g = 1, 4, for(i = 0, bnds[g], listput(R, gens[g] * T^i)));
  Vec(R);
}

pick(g) = { my(a1, a3); until(a1 != 0 && a3 != 0 && a1 != a3, a1 = random(g); a3 = random(g)); [a1, a3]; }

default(parisizemax, 2000000000);
SAMPLES = 3;
setrand(20261009);
{
for(d = 8, 9,
  my(N = if(d >= 3, 16 * d - 16, 17), bad = List());
  forprime(p = 3, 16 * d,
    my(e = ceil(log(1e5) / log(p)), g = ffgen(p^e, 'y), o = g^0, z = 0);
    for(k = 1, SAMPLES,
      my(a = pick(g), Rw = rows(a[1], a[2], d, N, o));
      if(#Rw != N, error("dimension"));
      if(matdet(matrix(N, N, i, c, polcoeff(Rw[i], c - 1, T))) == 0, z++));
    if(z == SAMPLES, listput(bad, p)));
  print("d=", d, " N=", N, " N^2-1=", factor(N^2 - 1)~, "  primes p<=16d with zero determinant at all samples: ", Vec(bad)));
}
quit;
