\\ Companion of bmd_pair_limit_normality.gp for the primes 3 and 5, which integer points cannot test
\\ (too few distinct nonzero residues).  Statement tested: the one-merge limit L of
\\ lem:cube-pair-confluence-limit, and the collision series U_d (control), have nonzero length-N
\\ Hasse jet determinant at a random point with distinct nonzero roots in GF(p^4).  A nonzero value
\\ at one point proves generic nonvanishing mod p; zero at all SAMPLES points is reported.

coeffs(s, N) = vector(N, k, polcoeff(s, k - 1, T));

Urows(a, d, N, o) = {
  my(r = #a, w = vector(r, i, sqrt(o + a[i] * T + O(T^N))), rows = List());
  forsubset(r, S,
    my(wS = o + O(T^N));
    for(t = 1, #S, wS *= w[S[t]]);
    for(i = 0, d - #S, listput(rows, T^i * wS)));
  Vec(rows);
}

Lrows(b, d, N, o) = {
  my(s = #b, w = vector(s, i, sqrt(o + b[i] * T + O(T^N))), tau = T / (o + b[1] * T) + O(T^N), rows = List());
  forsubset(s - 1, R,
    my(wR = o + O(T^N), j = d - #R, e);
    for(t = 1, #R, wR *= w[R[t] + 1]);
    if(j >= 0,
      e = if(j >= 1, 2 * j - 1, 0);
      for(m = 0, e, listput(rows, wR * (o + b[1] * T)^j * tau^m)));
    if(j >= 1,
      for(m = 0, 2 * j - 1, listput(rows, wR * w[1] * (o + b[1] * T)^(j - 1) * tau^m))));
  Vec(rows);
}

\\ random distinct nonzero elements of GF(p^4)
roots(g, r) = {
  my(v = List());
  while(#v < r, my(x = random(g)); if(x != 0 && !setsearch(Set(Vec(v)), x), listput(v, x)));
  Vec(v);
}

SAMPLES = 4;
default(parisizemax, 2^31);

report(p, r, d) = {
  my(g = ffgen(p^4, 'y), o = g^0, N = #Urows(vector(r, i, i), d, 1, 1), zU = 0, zL = 0);
  for(k = 1, SAMPLES,
    my(aU = roots(g, r), bL = roots(g, r - 1));
    my(MU = matrix(N, N, i, c, polcoeff(Urows(aU, d, N, o)[i], c - 1, T)));
    my(ML = matrix(N, N, i, c, polcoeff(Lrows(bL, d, N, o)[i], c - 1, T)));
    if(matdet(MU) == 0, zU++);
    if(matdet(ML) == 0, zL++));
  printf("p=%d r=%d d=%d N=%d  zero det U at %d/%d points | zero det L at %d/%d points\n",
         p, r, d, N, zU, SAMPLES, zL, SAMPLES);
}

setrand(20261009);
foreach([3, 5], p, for(d = 2, 5, report(p, 3, d)); for(d = 2, 4, report(p, 4, d)));
quit;
