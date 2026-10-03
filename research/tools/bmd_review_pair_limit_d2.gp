\\ Falsification test of the goal-level route review of cycle kbp (9 October 2026).
\\ Statement tested: statement 2's reduction (collision lattice + lem:cube-pair-confluence-limit) asks that
\\ the one-merge limit L_d on C_{n-2} be generically normal at T=0.  At the open slice p=3, d=2 the record
\\ certifies Delta_{n,2} != 0 mod 3 for n <= 21, while the sequential coface fails from n=5
\\ (check:cube-iterated-merge-orders).  Does L_2 stay normal at p=3, n = 5..12 (r = n-1 = 4..11 roots)?
\\ Control: the collision series U_2 on C_{n-1}.  Row builders copied from bmd_pair_limit_resonance_primes.gp.
\\ A nonzero value at a random point of GF(3^4) proves generic nonvanishing mod 3; zeros at all samples
\\ suggest (not prove) identical vanishing.


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

default(parisizemax, 2^31);
SAMPLES = 3;

report(p, d, r) = {
  my(g = ffgen(p^4, 'y), o = g^0, N = #Urows(vector(r, i, i), d, 1, 1), zU = 0, zL = 0);
  for(k = 1, SAMPLES,
    my(aU = roots(g, r), bL = roots(g, r - 1));
    my(RU = Urows(aU, d, N, o), RL = Lrows(bL, d, N, o));
    if(#RL != N, error("dimension of L"));
    my(MU = matrix(N, N, i, c, polcoeff(RU[i], c - 1, T)));
    my(ML = matrix(N, N, i, c, polcoeff(RL[i], c - 1, T)));
    if(matdet(MU) == 0, zU++);
    if(matdet(ML) == 0, zL++));
  printf("p=%d n=%d d=%d N=%d  zero det U at %d/%d points | zero det L at %d/%d points\n", p, r + 1, d, N, zU, SAMPLES, zL, SAMPLES);
}

setrand(20261009);
for(r = 4, 11, report(3, 2, r));
quit;
