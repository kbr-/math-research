\\ Falsification test of the goal-level route review of cycle kbw (9 October 2026).
\\ Statement tested: statement 2 rests on generic normality at T=0 of the one-merge limit L_d on C_{n-2}
\\ (lem:cube-pair-confluence-limit with the collision lattice).  It was tested at n=5 and at p=3, d=2 only.
\\ Here n=6 (r=5 roots), d=3, N=49, every odd p <= 2^{n-1} d = 96, at three random points of GF(p^e),
\\ p^e > 10^5.  Control: the collision series U_3 on C_5.  Row builders copied from
\\ bmd_pair_limit_resonance_primes.gp.  A nonzero value proves generic normality mod p.

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

roots(g, r) = {
  my(v = List());
  while(#v < r, my(x = random(g)); if(x != 0 && !setsearch(Set(Vec(v)), x), listput(v, x)));
  Vec(v);
}

default(parisizemax, 2^31);
SAMPLES = 3;
setrand(20261009);
{
my(d = 3, r = 5, N = #Urows(vector(r, i, i), d, 1, 1), bad = List());
print("n=6 d=3 N=", N);
forprime(p = 3, 96,
  my(e = ceil(log(1e5) / log(p)), g = ffgen(p^e, 'y), o = g^0, zU = 0, zL = 0);
  for(k = 1, SAMPLES,
    my(aU = roots(g, r), bL = roots(g, r - 1));
    my(RU = Urows(aU, d, N, o), RL = Lrows(bL, d, N, o));
    if(#RL != N, error("dimension of L"));
    if(matdet(matrix(N, N, i, c, polcoeff(RU[i], c - 1, T))) == 0, zU++);
    if(matdet(matrix(N, N, i, c, polcoeff(RL[i], c - 1, T))) == 0, zL++));
  if(zL == SAMPLES || zU == SAMPLES, listput(bad, [p, zU, zL])));
print("primes p <= 96 with U or L zero at all samples [p, zeros U, zeros L]: ", Vec(bad));
}
quit;
