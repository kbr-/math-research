\\ Resonance-targeted falsification test (route review of 9 October 2026, cycle kbi).
\\ Statement tested: the one-merge limit L_d of lem:cube-pair-confluence-limit at n=5 (r=4 roots) has a
\\ nonzero length-N Hasse jet determinant at a random admissible point of GF(p^4), N = 16d-16, at the primes
\\ where earlier collisions failed: p | N^2-1 (the n=4 second-collision resonance shape) and p | 2j-1 (the
\\ unbalanced second merge).  d=5: N=64, N^2-1 = 3^2*5*7*13, 2j-1 in {9,7,5}.  d=6: N=80, N^2-1 = 3^4*79.
\\ Control: the collision series U_d itself.  A nonzero value proves generic nonvanishing mod p.

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

report(p, d) = {
  my(g = ffgen(p^4, 'y), o = g^0, r = 4, N = #Urows(vector(r, i, i), d, 1, 1), zU = 0, zL = 0);
  if(N != 16 * d - 16, error("unexpected N"));
  for(k = 1, SAMPLES,
    my(aU = roots(g, r), bL = roots(g, r - 1));
    my(RU = Urows(aU, d, N, o), RL = Lrows(bL, d, N, o));    \\ rows built once
    my(MU = matrix(N, N, i, c, polcoeff(RU[i], c - 1, T)));
    my(ML = matrix(N, N, i, c, polcoeff(RL[i], c - 1, T)));
    if(matdet(MU) == 0, zU++);
    if(matdet(ML) == 0, zL++));
  printf("p=%d n=5 d=%d N=%d  zero det U at %d/%d points | zero det L at %d/%d points\n", p, d, N, zU, SAMPLES, zL, SAMPLES);
}

setrand(20261009);
foreach([3, 5, 7, 13], p, report(p, 5));
foreach([3, 79], p, report(p, 6));
quit;
