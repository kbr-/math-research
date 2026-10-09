\\ First non-positive coefficient of (1+z)^(v-m*k) * h(z)^m, h the level polynomial of a half-table
\\ of largest immunity on k variables: b_i = binomial(k,i) from below until the total 2^(k-1) is used.
\\ Same statement as table_series.py (a statement about power series only), in exact arithmetic with
\\ PARI's power series; used for the larger cases, and cross-checked against table_series.py on the
\\ cases both compute.  Output: one line "v k m Dstar ratio" per case, Dstar = -1 if none up to v/2.
default(parisize, 2000000000);
halflevels(k) = { my(left = 2^(k-1), b = vector(k+1)); for(i = 0, k, b[i+1] = min(binomial(k,i), left); left -= b[i+1]); b };
dstar(v, k, m) = {
  my(N = v\2 + 2, b = halflevels(k), h, S, d = -1);
  h = sum(i = 0, k, b[i+1]*z^i) + O(z^N);
  S = (1 + z + O(z^N))^(v - m*k) * h^m;
  for(j = 0, N-1, if(polcoeff(S, j) <= 0, d = j; break));
  d
};
cases = [[1024,20,1044],[256,20,276],[512,20,532],[2048,20,2068],[4096,20,4116],[8192,20,8212],[1024,24,1048],[2048,24,2072],[4096,24,4120],[8192,24,8216],[2048,12,2060],[2048,16,2064],[8192,16,8208]];
for(c = 1, #cases, my(v = cases[c][1], k = cases[c][2], m = cases[c][3], d = dstar(v, k, m)); print(v, " ", k, " ", m, " ", d, " ", if(d < 0, "none", precision(1.*d/v, 5))));
quit
