\\ Falsification test for lem:cube-pair-confluence-limit (route review of 9 October 2026).
\\ Statement tested: the one-merge limit L of the collision series U_d (roots a_1..a_r, a_2 -> a_1)
\\ has an invertible length-N Hasse jet map at T = 0 modulo every odd prime p, i.e. its jet
\\ determinant at a generic point has no odd prime factor.  Control: U_d itself (r = 3 is the
\\ dimension-four collision series, whose all-odd normality is thm:cube-four-all-odd-normality).
\\ Method: exact rational determinants at three fixed integer points; a prime p is reported
\\ only if it divides the determinant at all three points (generic vanishing mod p is then
\\ suggested; nonvanishing at one point proves generic nonvanishing mod p).
\\ Hypotheses asserted: distinct nonzero roots; dim L = dim U = N.

coeffs(s, N) = vector(N, k, polcoeff(s, k - 1, T));
wser(a, N) = sqrt(1 + a * T + O(T^N));

\\ rows of U_d for roots a (vector), as power series to precision N
Urows(a, d, N) = {
  my(r = #a, w = vector(r, i, wser(a[i], N)), rows = List());
  forsubset(r, S,
    my(wS = 1 + O(T^N));
    for(t = 1, #S, wS *= w[S[t]]);
    for(i = 0, d - #S, listput(rows, T^i * wS)));
  Vec(rows);
}

\\ rows of the limit L: b = [a_1, a_3, ..., a_r] (a_1 merged with a_2)
Lrows(b, d, N) = {
  my(s = #b, w = vector(s, i, wser(b[i], N)), tau = T / (1 + b[1] * T) + O(T^N), rows = List());
  forsubset(s - 1, R,
    my(wR = 1 + O(T^N), j = d - #R, e);
    for(t = 1, #R, wR *= w[R[t] + 1]);
    if(j >= 0,
      e = if(j >= 1, 2 * j - 1, 0);
      for(m = 0, e, listput(rows, wR * (1 + b[1] * T)^j * tau^m)));
    if(j >= 1,
      for(m = 0, 2 * j - 1, listput(rows, wR * w[1] * (1 + b[1] * T)^(j - 1) * tau^m))));
  Vec(rows);
}

oddpart(x) = { x = abs(numerator(x)); while(x % 2 == 0 && x, x /= 2); x; }

\\ A point is admissible for p when every root and every root difference is a p-unit.
admissible(a, p) = {
  for(i = 1, #a, if(a[i] % p == 0, return(0));
    for(k = i + 1, #a, if((a[i] - a[k]) % p == 0, return(0))));
  1;
}

PRIMES = primes([3, 61]);
SAMPLES = 16;
default(parisizemax, 2^31);

\\ For each odd prime p <= 61: p is reported for U (resp. L) when p divides the determinant at every
\\ admissible sample point (at least three are required, else the prime is reported as "untested").
report(r, d) = {
  setrand(20261009 + 100 * r + d);
  my(N = #Urows(vector(r, i, i), d, 1), dU = List(), dL = List(), badU = List(), badL = List(), thin = List());
  if(N != #Lrows(vector(r - 1, i, i), d, 1), error("dimension mismatch r=", r, " d=", d));
  for(k = 1, SAMPLES,
    my(aU = vector(r, i, random(401) - 200), bL = vector(r - 1, i, random(401) - 200));
    my(MU = matrix(N, N, i, c, polcoeff(Urows(aU, d, N)[i], c - 1, T)));
    my(ML = matrix(N, N, i, c, polcoeff(Lrows(bL, d, N)[i], c - 1, T)));
    listput(dU, [aU, matdet(MU)]); listput(dL, [bL, matdet(ML)]));
  foreach(PRIMES, p,
    my(nu = 0, hu = 0, nl = 0, hl = 0);
    foreach(dU, x, if(admissible(x[1], p), nu++; if(numerator(x[2]) % p == 0, hu++)));
    foreach(dL, x, if(admissible(x[1], p), nl++; if(numerator(x[2]) % p == 0, hl++)));
    if(nu < 3 || nl < 3, listput(thin, p), if(hu == nu, listput(badU, p)); if(hl == nl, listput(badL, p))));
  printf("r=%d d=%d N=%d  primes<=61 killing det U at every admissible point: %s | det L: %s | too few points: %s\n",
         r, d, N, Vec(badU), Vec(badL), Vec(thin));
}

for(d = 2, 5, report(3, d));
for(d = 2, 4, report(4, d));
quit;
